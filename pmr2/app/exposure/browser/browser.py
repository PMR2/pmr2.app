from os.path import join
import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
from zope.app.component.hooks import getSite
from zope.schema.interfaces import RequiredMissing
from zope.annotation.interfaces import IAnnotations
from zope.publisher.browser import BrowserPage
from zope.i18nmessageid import MessageFactory
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.container.interfaces import IContainer
_ = MessageFactory("pmr2")

from paste.httpexceptions import HTTPNotFound
import z3c.form.field
from z3c.form import button
from plone.memoize.view import memoize
from plone.z3cform import layout
from plone.z3cform.fieldsets import group, extensible

from Acquisition import aq_parent, aq_inner
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream
from Products.CMFCore import permissions
from Products.statusmessages.interfaces import IStatusMessage

from zope.app.pagetemplate.viewpagetemplatefile \
    import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from pmr2.idgen.interfaces import IIdGenerator

from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.app.workspace.browser.browser import WorkspaceLog
from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.exceptions import *

from pmr2.app.exposure import table

from pmr2.app.exposure.interfaces import *
from pmr2.app.exposure.browser.interfaces import *

from pmr2.app.interfaces import *
from pmr2.app.browser.interfaces import *
from pmr2.app.annotation.interfaces import *
from pmr2.app.annotation.factory import has_note, del_note
from pmr2.app.exposure.content import *

from pmr2.app.browser import form
from pmr2.app.browser import page
from pmr2.app.browser import widget
from pmr2.app.browser.layout import *

from pmr2.app.exposure.browser.util import fieldvalues
from pmr2.app.exposure.browser.util import viewinfo

def restrictedGetExposureContainer():
    # If there is a way to "magically" anchor this form at the
    # target exposure container rather than the workspace, this
    # would be unnecesary.
    settings = zope.component.queryUtility(IPMR2GlobalSettings)
    site = getSite()
    exposure_container = site.restrictedTraverse(
        str(settings.default_exposure_subpath), None)
    if exposure_container is None:
        # assume lack of permission.
        raise Unauthorized('No permission to make exposures.')
    security = getSecurityManager()
    if not security.checkPermission(permissions.AddPortalContent, 
            exposure_container):
        raise Unauthorized('No permission to make exposures.')
    return exposure_container

def getGenerator(form):
    # Using default id generator as specified by global settings. 
    # Will need to change this if exposure containers can specify
    # its own id generation scheme.
    settings = zope.component.queryUtility(IPMR2GlobalSettings)
    name = settings.default_exposure_idgen
    idgen = zope.component.queryUtility(IIdGenerator, name=name)
    if idgen is None:
        status = IStatusMessage(form.request)
        status.addStatusMessage(
            u'The exposure id generator `%s` cannot be found; '
            'please contact site administrator.' % name, 'error')
        raise z3c.form.interfaces.ActionExecutionError(
            ExposureIdGeneratorMissingError())
    return idgen


class ExposureAddForm(form.AddForm):
    """\
    Exposure creation form.
    """

    fields = z3c.form.field.Fields(IExposure).select(
        'workspace',
        'commit_id',
        'curation',
    )
    clsobj = Exposure

    def create(self, data):
        generator = getGenerator(self)
        data['id'] = generator.next()
        return form.AddForm.create(self, data)

    def add_data(self, ctxobj):
        ctxobj.workspace = self._data['workspace']
        ctxobj.commit_id = self._data['commit_id']
        ctxobj.curation = self._data['curation']
        helper = zope.component.queryAdapter(ctxobj, IExposureSourceAdapter)
        if helper:
            exposure, workspace, path = helper.source()
            ctxobj.setTitle(workspace.title)
        

ExposureAddFormView = layout.wrap_form(ExposureAddForm, 
    label="Exposure Create Form")


class CreateExposureForm(form.AddForm, page.TraversePage):
    """\
    Page that will create an exposure inside the default exposure
    container from within a workspace.
    """

    _gotExposureContainer = False

    def create(self, data):
        # no data assignments here
        generator = getGenerator(self)
        eid = generator.next()
        return Exposure(eid)

    def add(self, obj):
        """\
        The generic add method.
        """
        if not self.traverse_subpath:
            raise HTTPNotFound(self.context.title_or_id())

        exposure = obj
        workspace = u'/'.join(self.context.getPhysicalPath())
        commit_id = unicode(self.traverse_subpath[0])

        try:
            exposure_container = restrictedGetExposureContainer()
        except Unauthorized:
            self.status = 'Unauthorized to create new exposure.'
            raise z3c.form.interfaces.ActionExecutionError(
                ExposureContainerInaccessibleError())
        self._gotExposureContainer = True

        exposure_container[exposure.id] = exposure
        exposure = exposure_container[exposure.id]
        exposure.workspace = workspace
        exposure.commit_id = commit_id
        exposure.setTitle(self.context.title)
        exposure.notifyWorkflowCreated()
        exposure.reindexObject()

        # so redirection via self.getURL will work.
        self.ctxobj = exposure

    def render(self):
        if not self._gotExposureContainer:
            # we didn't finish.
            self._finishedAdd = False
        return super(CreateExposureForm, self).render()

    def __call__(self, *a, **kw):
        if not self.traverse_subpath:
            raise HTTPNotFound(self.context.title_or_id())

        try:
            storage = zope.component.getAdapter(self.context, IStorage)
            commit_id = unicode(self.traverse_subpath[0])
            # Make sure this is a valid revision.
            storage.checkout(commit_id)
        except (PathInvalidError, RevisionNotFoundError,):
            raise HTTPNotFound(self.context.title_or_id())

        return super(CreateExposureForm, self).__call__(*a, **kw)

CreateExposureFormView = layout.wrap_form(CreateExposureForm,
    __wrapper_class=TraverseFormWrapper,
    label="Select 'Add' to begin creating the exposure")


class ExposureEditForm(z3c.form.form.EditForm):
    """\
    Exposure editing form.
    """

    fields = z3c.form.field.Fields(IExposure).select(
        'title',
        'curation',
    )

ExposureEditFormView = layout.wrap_form(ExposureEditForm, 
    label="Exposure Edit Form")


class ExposureEditCurationForm(z3c.form.form.EditForm):
    """\
    Exposure editing form.
    """

    fields = z3c.form.field.Fields(IExposure).select(
        'curation',
    )

ExposureEditCurationFormView = layout.wrap_form(ExposureEditCurationForm, 
    label="Curation Editor")


class ExposureFileGenForm(form.AddForm):
    """\
    Form to generate an exposure file (encapsulates an actual file in a
    workspace).
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    fields = z3c.form.field.Fields(IExposureFileGenForm)

    def create(self, data):
        self._data = data
        # XXX assert that filename exists in workspace?
        path = data['filename'].split('/')
        # get the name first
        id_ = path.pop()
        # then reverse so they will be popped in the right order
        path.reverse()

        # save this for later use.
        self._data['_path'] = path

        result = ExposureFile(id_)
        # XXX is the id validated to be not a duplicate?
        # I guess we don't need validation if the object
        self._name = result.id
        # XXX this could probably also do annotation from a list
        return result

    def resolve_file(self, path):
        # XXX move to separate class?
        if not path:
            path = []
        if isinstance(path, basestring):
            path = path.split('/')
        path.reverse()
        context = self.context
        while path:
            name = path.pop()
            if name in context:
                # reusing existing context.
                context = context[name]
                continue
            raise ValueError('%s is not in context' % name)
        return context

    def resolve_folder(self, path):
        if not path:
            path = []
        if isinstance(path, basestring):
            path = path.split('/')
        path.reverse()
        return self._resolve_folder(path)

    def _resolve_folder(self, path, create=False):
        # XXX move to separate class?
        # there are id checks for the path components within the field 
        # itself, so any failure happens (due to possible duplicates
        # invalids) will cause 
        # an exception during the nested folder creation below.

        context = self.context
        while path:
            name = path.pop()
            if name in context:
                # reusing existing context.
                context = context[name]
                if IExposureFolder.providedBy(context):
                    continue
                # we have some inconsistency, giving up.
                raise TypeError('`%s` is not an ExposureFolder' % name)

            if not create:
                # XXX exception type?
                raise ValueError('%s is not in context' % name)

            # object not exist, standard routine to create, add, reindex
            folderobj = ExposureFolder(name)
            context[name] = folderobj
            context.notifyWorkflowCreated()
            context.reindexObject()
            # done, we have next context.
            context = context[name]
        return context

    def add(self, obj):
        # switch to new context so parent class knows to here.
        # XXX other side effects from setting a new self.context?
        self.context = self._resolve_folder(self._data['_path'], True)
        # parent to add
        super(ExposureFileGenForm, self).add(obj)

    def add_data(self, ctxobj):
        # give a default title based on filename
        ctxobj.setTitle(ctxobj.id)

ExposureFileGenFormView = layout.wrap_form(ExposureFileGenForm, 
    label="Add a file to the exposure")


class ExposureFileAnnotatorForm(form.BaseAnnotationForm):
    """\
    Form to add a note to an ExposureFile.
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    fields = z3c.form.field.Fields(IExposureFileAnnotatorForm)

    @button.buttonAndHandler(_('Annotate'), name='apply')
    def handleAnnotate(self, action):
        self.baseAnnotate(action)

    def annotate(self):
        annotator = zope.component.getUtility(
            IExposureFileAnnotator,
            name=self._data['annotators']
        )
        annotator(self.context)()

    def nextURL(self):
        # if there are multiple choices, redirect to default view.
        # XXX default view only for now.
        note = zope.component.getAdapter(
            self.context, name=self._data['annotators'])
        if IExposureFileEditableNote.providedBy(note):
            # redirect to note editor view for the note as no data
            # should have been added.
            return '%s/@@note_editor/%s' % (self.context.absolute_url(), 
                                            self._data['annotators'])
        return '%s/@@%s' % (self.context.absolute_url(), 
                            self._data['annotators'])

ExposureFileAnnotatorFormView = layout.wrap_form(ExposureFileAnnotatorForm, 
    label="Add an annotation to an Exposure File.")


class ExposureFileTypeAddForm(form.AddForm):
    """\
    ExposureFileType creation form.
    """

    fields = z3c.form.field.Fields(IObjectIdMixin) + \
             z3c.form.field.Fields(IExposureFileType)
    clsobj = ExposureFileType

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']
        ctxobj.views = self._data['views']
        ctxobj.select_view = self._data['select_view']
        ctxobj.tags = self._data['tags']
        

ExposureFileTypeAddFormView = layout.wrap_form(ExposureFileTypeAddForm, 
    label="Exposure File Type creator")


class ExposureFileTypeEditForm(z3c.form.form.EditForm):
    """\
    ExposureFileType editing form.
    """

    fields = z3c.form.field.Fields(IExposureFileType)

    def update(self):
        super(ExposureFileTypeEditForm, self).update()

ExposureFileTypeEditFormView = layout.wrap_form(ExposureFileTypeEditForm, 
    label="Exposure File Type editor")


class ExposureFileTypeDisplayForm(form.DisplayForm):
    """\
    ExposureFileType creation form.
    """

    fields = z3c.form.field.Fields(IExposureFileType)

ExposureFileTypeDisplayFormView = layout.wrap_form(ExposureFileTypeDisplayForm, 
    label="Exposure File Type viewer")


class ExposureFileTypeChoiceForm(form.Form):
    """\
    This form chooses the views available for this page, based on either
    the file type or selecting the list of views to be made available.

    It will also tag the context with the tag as specified by the
    choosen file type.
    """

    ignoreContext = True
    ignoreReadonly = True
    formErrorsMessage = _('There were some errors.')
    group_names = None

    def __init__(self, *a, **kw):
        super(ExposureFileTypeChoiceForm, self).__init__(*a, **kw)
        # since this can change, we instantiate a copy of the fields for
        # each form
        self.fields = z3c.form.field.Fields(IExposureFileTypeChoiceForm)

    @button.buttonAndHandler(_('Next'), name='next')
    def handleNext(self, action):
        data, errors = self.extractData()
        group_names = None
        if 'annotators' in data and data['annotators']:
            group_names = list(data['annotators'])

        if 'eftypes' in data and data['eftypes']:
            catalog = getToolByName(self.context, 'portal_catalog')
            if not catalog:
                # abort, since there really is no catalog, let the user
                # know.
                self.status = _('Catalog not found.')
                return

            results = catalog(
                portal_type='ExposureFileType',
                review_state='published',
                path=data['eftypes'],
            )
            if results:
                # we have what we want.
                group_names = results[0].pmr2_eftype_views
                self.context.setSubject(results[0].pmr2_eftype_tags)
                # XXX might consider setting following on the next form,
                # which is when this particular view is generated.
                self.context.selected_view = results[0].pmr2_eftype_select_view
                self.context.file_type = data['eftypes']
                self.status = _('File type assigned. Please select views '
                                'to add to this file.')

        self.context.views = self.group_names = group_names
        if group_names:
            # we have more views, redirect
            return self.request.response.redirect(
                self.context.absolute_url() + '/@@edit_annotations')

        # since there was no fields selected and the file type supplied 
        # had no views defined, we prompt the form again without the
        # types enabled.
        self.fields.omit('eftypes')

ExposureFileTypeChoiceFormView = layout.wrap_form(
    ExposureFileTypeChoiceForm, 
    label="Add an annotation to an Exposure File.")


class ExposureFileTypeAnnotatorForm(
        extensible.ExtensibleForm, 
        form.BaseAnnotationForm):
    """\
    Form to add a group of notes to an ExposureFile.  Specific notes
    involved are retrievable via querying for IExposureFileType with
    its specific name (e.g. cellml, fieldml).  Then a form is generated
    with all the required fields.  The sets of file types and views that
    will be generated are currently defined by packages, but in the
    future it may be possible that a mixture of user-defined and package
    provided profiles can be used.

    However, the current implementation can result in a rather 
    inconsistent view for the users of this form if she submitted this
    as someone else changed the views that are available for this form -
    the resulting data will be inconsistent.
    """

    def __init__(self, *a, **kw):
        super(ExposureFileTypeAnnotatorForm, self).__init__(*a, **kw)
        self.groups = []
        self.fields = z3c.form.field.Fields()

    @button.buttonAndHandler(_('Annotate'), name='apply')
    def handleAnnotate(self, action):
        self.baseAnnotate(action)

    def annotate(self):
        """
        Goes through the notes and adapt to each specifc annotator.

        XXX this assumes nobody changed what this form had and what the
        self.context.views contains now.
        """

        # have to process the data as it's merged between all the forms.
        groups = {}
        for k, value in self._data.iteritems():
            group, key = k.split('.', 1)
            if not group in groups:
                groups[group] = []
            groups[group].append((key, value,))

        self._annotate(groups)

    def _annotate(self, groups):
        # iterate through the views that had been selected for this
        # form, and use the data supplied by the groups parameter.
        for name in self.context.views:
            annotatorFactory = zope.component.queryUtility(
                IExposureFileAnnotator,
                name=name,
            )

            if not annotatorFactory:
                # self.context.views somehow included invalid values, we
                # should log it and continue (something somewhere messed
                # with it.
                continue

            # Default annotator fully generates its data, we do not need 
            # to pass in extra arguments.
            args = ()

            # Instantiate annotator with our context.
            annotator = annotatorFactory(self.context)
            if IExposureFileEditAnnotator.providedBy(annotator) or \
                    IExposureFilePostEditAnnotator.providedBy(annotator):
                # The edited annotator will need the fields.
                if name not in groups.keys():
                    # well, it looks like somehow the set of views that
                    # this form submittal was based upon is no longer
                    # same as the set of views stored now.  We should 
                    # raise a validation error of sort, but for now we 
                    # ignore it.
                    continue
                args = (groups[name],)

            # Call annotator to annotate our file.
            annotator(*args)

        # The tagging should have been done in the previous form.

    def nextURL(self):
        return '%s/view' % self.context.absolute_url() 

ExposureFileTypeAnnotatorFormView = layout.wrap_form(
    ExposureFileTypeAnnotatorForm, 
    label="Add an annotation to an Exposure File.")


class ExposureFileTypeAnnotatorExtender(extensible.FormExtender):
    zope.component.adapts(
        IExposureFile, IBrowserRequest, ExposureFileTypeAnnotatorForm)

    def update(self):
        for name in self.context.views:
            # XXX self.context.views should be a tuple of ascii values
            # taken from the constraint vocabulary of installed views.
            name = name.encode('ascii', 'replace')
            a_factory = zope.component.queryUtility(IExposureFileAnnotator, 
                                                    name=name)
            if not a_factory:
                # silently ignore missing fields.
                continue

            annotator = a_factory(self.context)
            self.add(annotator)

    def add(self, annotator):
        fields = self.makeField(annotator)
        name = str(annotator.__name__)
        context = self.context
        ignoreContext = True

        # since the adapter results in a factory that instantiates
        # the annotation, this side effect must be avoided.
        if has_note(context, name):
            ignoreContext = False
            context = zope.component.getAdapter(
                context, annotator.for_interface, name=name)

        # make the group and assign data.
        g = form.Group(context, self.request, self.form)
        g.__name__ = annotator.title
        g.label = annotator.title
        g.fields = fields
        g.ignoreContext = ignoreContext
        if not fields.keys():
            g.description = u''\
                'There are no editable attributes for this note as values ' \
                'for this annotation are automatically generated.'

        # finally append this group
        self.form.groups.append(g)

    def makeField(self, annotator):
        # this method could potentially be refactored out into an 
        # adapter.
        name = str(annotator.__name__)
        if IExposureFileEditAnnotator.providedBy(annotator) or \
                IExposureFilePostEditAnnotator.providedBy(annotator):
            # edited fields
            fields = z3c.form.field.Fields(annotator.for_interface, 
                                           prefix=name)
            if IExposureFilePostEditAnnotator.providedBy(annotator):
                # select just the fields that will be edited.
                sel = ['%s.%s' % (name, n) for n in annotator.edited_names]
                fields = fields.select(*sel)
        else:
            # no edited fields available.
            fields = z3c.form.field.Fields(prefix=name)
        return fields


class ExposureFileNoteEditForm(form.EditForm, page.TraversePage):
    """\
    Some notes need to be user editable rather than generated.  They 
    must not be confused with the autogenerated ones, for the output may
    need sanitization that the editor cannot provide somehow (for now).

    This is the edit form for the annotation notes, it will validate
    whether the supplied annotation name provides the interface that
    allows editing.  If so, it will query for the interface with the
    fields it tracks so the correct widgets can be rendered.
    """

    zope.interface.implements(IExposureFileNoteEditForm)

    def getContent(self):
        return self.note

    def applyChanges(self, data):
        results = super(ExposureFileNoteEditForm, self).applyChanges(data)
        name = '/'.join(self.traverse_subpath)
        annotator = zope.component.getUtility(
            IExposureFileAnnotator, name=name)
        # since this form already assigns the data, we don't need to
        # pass in data for the call method for assignment, but we need
        # an empty tuple (for now)
        annotator(self.context)(())
        return results

    def update(self):
        """\
        Since the generic call method will call this first, and the
        default update will also update the widgets and things, we will
        first update the instance with what it is supposed to be.
        """

        # fail silently on slashes, because we don't (yet) have a case 
        # where two distinct path components are needed.
        name = '/'.join(self.traverse_subpath)
        note = zope.component.queryAdapter(self.context, name=name)
        if note is None or not IExposureFileEditableNote.providedBy(note):
            # this place does not exist for notes not meant to edited.
            # or an unspecified note.
            # maybe later if note is None, we return a view that lists
            # links to the editable notes.
            raise HTTPNotFound()
        self.note = note

        # This might be worth some thought.
        # So the note exists, we now determine whether a default editor
        # had been registered for this note to redirect to.  If not, we
        # use this default note editor for it.

        # assign the field
        # XXX this appears to work, we only want the interface that is
        # directly implemented by the class, which this appears to 
        # return in the order provided.
        # See: Exposure.ExposureExport (uses same method)
        inf = zope.interface.providedBy(note).interfaces().next()
        self.fields = z3c.form.field.Fields(inf)
        super(ExposureFileNoteEditForm, self).update()

ExposureFileNoteEditFormView = layout.wrap_form(ExposureFileNoteEditForm, 
    __wrapper_class=PlainTraverseLayoutWrapper,
    label="Edit an Exposure File Note.")


class ExposureFileNoteArrangeForm(form.EditForm):
    """\
    Form to allow rearrangement of notes
    """

    #zope.interface.implements(IExposureFileNoteArrangeForm)
    fields = z3c.form.field.Fields(IExposureFile).select('views')

    def update(self):
        """\
        Call update as per normal, and then filter out the resulting
        values.
        """

        result = super(ExposureFileNoteArrangeForm, self).update()
        views = [i for i in self.context.views if
                    zope.component.queryAdapter(self.context, name=i)]
        self.context.views = views
        return result

ExposureFileNoteArrangeFormView = layout.wrap_form(ExposureFileNoteArrangeForm, 
    label="Arrange Exposure File Notes.")


class ExposureDocViewGenForm(form.BaseAnnotationForm):
    """\
    Form to generate the default view of the base exposure.
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    ignoreContext = False
    zope.interface.implements(IExposureDocViewGenForm)
    fields = z3c.form.field.Fields(IExposureDocViewGenForm)

    def getContent(self):
        # since we are not using the same interface as the exposure
        # object as it does not use choice, to populate the values here
        # will require an adapter.
        return zope.component.getAdapter(self.context, IExposureDocViewGenForm)

    @button.buttonAndHandler(_('Generate'), name='apply')
    def handleGenerate(self, action):
        self.baseAnnotate(action)

    def annotate(self):
        if self._data['docview_gensource'] is not None:
            # XXX manual unicode call, because vocab derives data directly
            # from manifest in mercurial, which is str.
            self.context.docview_gensource = \
                unicode(self._data['docview_gensource'])
        self.context.docview_generator = self._data['docview_generator']
        if not self.context.docview_generator:
            # do nothing if we have no generator.
            return None 
        viewgen = zope.component.getUtility(
            IDocViewGen,
            name=self._data['docview_generator']
        )
        viewgen(self.context)()
        self.context.reindexObject()

    def nextURL(self):
        # return to the root, because we will only have one default view
        # that generally will work.
        uri = self.context.absolute_url()
        propsTool = getToolByName(self.context, 'portal_properties')
        siteProperties = getattr(propsTool, 'site_properties')
        views_req = list(siteProperties.getProperty(
                         'typesUseViewActionInListings'))
        if self.context.portal_type in views_req:
            # assumption
            uri += '/view'
        return uri

ExposureDocViewGenFormView = layout.wrap_form(
    ExposureDocViewGenForm, 
    label="Generate Default View for Exposure.")


class ExposureInfo(page.SimplePage):
    """\
    Simple exposure file page

    Renders the documentation that was manually assigned to the file.
    """

    render = ViewPageTemplateFile('exposure_docview.pt')

    def subtitle(self):
        return self.context.Description()

    def content(self):
        return self.context.getText()

ExposureInfoView = layout.wrap_form(ExposureInfo,
    __wrapper_class=PloneviewLayoutWrapper)


class ExposureFileInfo(page.TraversePage):
    """\
    Base view of an ExposureFile object.  Shows the list of adapters.
    """

    content = ViewPageTemplateFile('exposure_file_info.pt')
    subtitle = u'Exposure File Information'

ExposureFileInfoView = layout.wrap_form(ExposureFileInfo,
    __wrapper_class=PlainLayoutWrapper)


class ExposureFileSelectViewForm(form.EditForm):
    """\
    Form to select a note view for exposure files.
    """

    fields = z3c.form.field.Fields(IExposureFileSelectView).select(
        'selected_view')

    def getContent(self):
        # since we are not using the same interface as the exposure
        # object as it does not use choice, to populate the values here
        # will require an adapter.
        return zope.component.getAdapter(self.context, 
                                         IExposureFileSelectView)

    def applyChanges(self, data):
        # Since we only have one field, and the default method doesn't
        # quite suit our needs here, we bypass the datamanager and 
        # manually assign the fields.
        content = self.context
        if content.selected_view == data['selected_view']:
            return {}
        content.selected_view = data['selected_view']
        changes = {
            IExposureFile: ['selected_view'],
        }
        # Construct change-descriptions for the object-modified event
        descriptions = []
        for interface, names in changes.items():
            descriptions.append(
                zope.lifecycleevent.Attributes(interface, *names))
        # Send out a detailed object-modified event
        zope.event.notify(
            zope.lifecycleevent.ObjectModifiedEvent(content, *descriptions))
        return changes

ExposureFileSelectViewFormView = layout.wrap_form(ExposureFileSelectViewForm, 
    label="Select Default View")


class ExposureFileDocumentView(page.TraversePage):
    """\
    ExposureFile is based on ATDocument, but we implemented a custom
    view selection, which this view handles.
    """

    def __call__(self):
        selected_view = self.context.selected_view
        # make sure the data is set correctly
        if selected_view in self.context.views:
            view = zope.component.queryMultiAdapter(
                (self.context, self.request), 
                name=selected_view,
            )
            if view:
                # let the view acquire the context so it doesn't fail
                # security checks.
                view = view.__of__(self.context)
                return view()
        # nothing can be done, default treatment
        return self.context.document_view()


class ExposureFileRedirectView(BrowserPage):
    """\
    The view that redirects to the original file.  This should be the
    default view for all ExposureFiles as they should have been anchored
    to specific files, thus resolved to be original content within its
    workspace and revision.
    """

    target_view = 'rawfile'

    def __call__(self):
        helper = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter)
        exposure, workspace, path = helper.source()
        target_uri = '%s/@@%s/%s/%s' % (workspace.absolute_url(), 
            self.target_view, exposure.commit_id, path)
        return self.request.response.redirect(target_uri)


class ExposureFileViewBase(page.TraversePage):
    """\
    Base class for views that peek require the annotation adapters that
    are attached to the ExposureFile objects.
    """

    zope.interface.implements(IExposureFileView)

    @property
    def name(self):
        return self.__name__

    @property
    def view_url(self):
        return '%s/@@%s' % (self.context.absolute_url(), self.name)

    @property
    def note(self):
        # get the utility that is tailored for this view.
        return zope.component.queryAdapter(self.context, name=self.__name__)


class RawTextNote(ExposureFileViewBase):
    """\
    This is a raw text view, wrapped in a pre block by the default 
    template.
    """

    template = ViewPageTemplateFile('code.pt')
    description = u'The following is a raw text representation of the file.'
    subtitle = u'Raw text view'

    @memoize
    def content(self):
        return self.note.text

RawTextNoteView = layout.wrap_form(RawTextNote,
    __wrapper_class=PlainLayoutWrapper)


class RawContentNote(ExposureFileViewBase):
    """\
    This is a raw content view, where the raw text is rendered as a
    struture as per the default template.
    """

    template = ViewPageTemplateFile('raw_content.pt')
    description = u'The following is a raw representation of the file.'
    subtitle = u'Raw content view'

    def content(self):
        return self.note.text


class GroupedNoteViewBase(ExposureFileViewBase):
    """\
    This view looks into a valid list of text.

    Quick way to regroup existing raw texts, or a lazy way to create new
    views but make juggling easier.

    In the future look into a clean way (and not complicated) to
    generate this.
    """

    template = ViewPageTemplateFile('sublinks.pt')
    description = u'The following is a list of available choices'
    subtitle = u'Raw text view'
    choices = {}

    @property
    def items(self):
        # XXX should this can be derived from the choices provided by 
        # context
        # the attributes/keys stored by the context plus all available
        # views could be listed (can show what can be done, what is not
        # generated)
        result = self.choices.keys()
        result.sort()
        return result

    def __call__(self):
        if not self.traverse_subpath:
            # nothing, give up early by showing the default list.
            return self.template()

        name = self.traverse_subpath[0]
        if name in self.choices:
            view = zope.component.getMultiAdapter(
                (self.context, self.request), 
                name=self.choices[name],
            )
            # since the view registered is the wrapper, we call the 
            # inner part of the it rather than itself.
            return view.form_instance()
        # XXX set an information note about invalid choice?
        return self.template()

# base
GroupedNoteViewBaseView = layout.wrap_form(
    GroupedNoteViewBase, __wrapper_class=PlainLayoutWrapper)


# utility

class ExposurePort(form.Form):
    """
    an export/importer for exposures
    """

    ignoreContext = True
    ignoreReadonly = True

    def __init__(self, *a, **kw):
        super(ExposurePort, self).__init__(*a, **kw)
        self.errors = []

    def _export(self, cur, prefix=''):

        # we don't have or need leading / to denote root.
        if not prefix:
            objpath = lambda x: '%s' % x
        else:
            objpath = lambda x: '%s/%s' % (prefix, x)

        for obj_id, obj in cur.items():
            p = objpath(obj_id)
            # do stuff depend on type

            if IExposureFile.providedBy(obj):
                d = {}
                for n in IExposureFile.names():
                    d[n] = getattr(obj, n)
                # query each views manually.
                d['views'] = viewinfo(obj)
                # retain the subject.
                d['Subject'] = obj.Subject()
                yield (p, d,)
            elif IExposureFolder.providedBy(obj):
                # we are ignorning other folder types, let an adapter
                # handle it below.
                for i in self._export(obj, p):
                    yield i
            else:
                # we don't know, so we ask an adapter to provide the
                # structure required, and trust they won't provide
                # something they don't own.
                a = zope.component.queryAdapter(obj, IExposurePortDataProvider)
                if a is not None:
                    yield a()

        # folder gets appended last for lazy reason - we assume all
        # paths will be created as files, meaning folders are created 
        # automatically, rather than creating that as file.
        # Then annotations can be assigned to them later, use viewinfo
        # to grab the relevant fields.
        fv = fieldvalues(cur)
        # need the subject of the current folder.
        fv['Subject'] = cur.Subject()
        yield (prefix, fv,)

    def export_source(self):
        return self.context

    def export(self):
        """\
        Returns a generator object that produces tuples containing the
        full path of the objects and a dictionary with values of its
        fields and annotations (notes) attached to it, along with its
        field values if applicable.
        """

        for i in self._export(self.export_source()):
            yield i

    def mold(self, target):
        """\
        Creates the new exposure at target, using what is produced by
        the export method.
        """

        for path, fields in self.export():
            if 'views' in fields:
                # XXX assume this specifies an ExposureFile
                fgen = ExposureFileGenForm(target, None)
                # since we may use this in a regenerative context, check
                # whether file had been created.
                try:
                    ctxobj = fgen.resolve_file(path)
                except ValueError:
                    # I guess not.
                    d = {
                        'filename': path,
                    }
                    fgen.createAndAdd(d)
                    # XXX using something that is magic in nature
                    # <form>.ctxobj is created by our customized object
                    # creation method for the form, and we are using 
                    # this informally declared object.
                    ctxobj = fgen.ctxobj

                # generate docview
                if fields['docview_generator']:
                    ctxobj.docview_gensource = fields['docview_gensource']
                    viewgen = zope.component.getUtility(
                        IDocViewGen,
                        name=fields['docview_generator'],
                    )
                    viewgen(ctxobj)()

                for view, view_fields in fields['views']:
                    # generate views
                    annotator = zope.component.getUtility(
                        IExposureFileAnnotator,
                        name=view,
                    )
                    # pass in the view_fields regardless whether it is
                    # editable or not because editable notes will have
                    # data ignored.
                    data = view_fields and view_fields.items() or None
                    try:
                        annotator(ctxobj)(data)
                    except RequiredMissing:
                        # this does not cover cases where schema have
                        # changed, or the old scheme into the new scheme.
                        note = zope.component.queryAdapter(
                            ctxobj,
                            name=view
                        )
                        if note:
                            # This editable note is missing some data,
                            # probably because it never existed, bad
                            # export data, updated schema or other
                            # errors.  We ignore it for now, and purge
                            # the stillborn note from the new object.
                            del_note(ctxobj, view)
                        else:
                            # However, the automatic generated ones we
                            # will continue to raise errors.  Maybe in
                            # the future we group these together, or
                            # make some way to adapt this to something
                            # that will handle the migration case.
                            raise

                # only ExposureFiles have this
                if IExposureFile.providedBy(ctxobj):
                    ctxobj.selected_view = fields['selected_view']
                    ctxobj.file_type = fields['file_type']
                    ctxobj.setSubject(fields['Subject'])

                ctxobj.reindexObject()
            else:
                # generate views.
                # using this to resolve the folder object
                fgen = ExposureFileGenForm(target, None)
                # XXX couldn't this just create the folder first for out
                # of order exports?
                container = fgen.resolve_folder(path)

                if fields['docview_gensource']:
                    # there is a source
                    container.docview_gensource = fields['docview_gensource']
                    viewgen = zope.component.queryUtility(
                        IDocViewGen,
                        name=fields['docview_generator']
                    )
                    if viewgen:
                        # and the view generator is still available
                        viewgen(container)()

                if IExposure.providedBy(container):
                    # only copy curation over, until this becomes an
                    # annotation.
                    container.curation = fields['curation']
                container.setSubject(fields['Subject'])
                container.reindexObject()


class ExposurePortCommitIdForm(ExposurePort):

    # this just have commit id, create exposure.

    formErrorsMessage = _('There are errors')

    _finishedAdd = False
    fields = z3c.form.field.Fields(IExposure).select(
        'commit_id',
    )

    def find_exposure_container(self):
        context = aq_inner(self.context)
        while context:
            if IExposureContainer.providedBy(context):
                return context
            context = aq_parent(context)

    @button.buttonAndHandler(_('Migrate'), name='apply')
    def handleMigrate(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        parent = self.find_exposure_container()

        eaf = ExposureAddForm(parent, None)
        data = {
            'workspace': self.context.workspace,
            'curation': None,  # to be copied later
            'commit_id': data['commit_id'],
        }
        eaf.createAndAdd(data)
        exp_id = data['id']
        target = parent[exp_id]
        self.mold(target)
        self._finishedAdd = True
        self.target = target

    def nextURL(self):
        return self.target.absolute_url()

    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(ExposurePortCommitIdForm, self).render()

ExposurePortCommitIdFormView = layout.wrap_form(ExposurePortCommitIdForm, 
    label="Exposure Port to new commit id")


class ExposureFileRegenerateForm(ExposurePort):
    """\
    This is to regenerate all exposure file notes.
    """

    # this just have commit id, create exposure.

    formErrorsMessage = _('There are errors with regeneration.')
    _finishedAdd = False

    def export(self):
        """\
        Generate and save structure, delete all objects, rebuild.
        """

        if hasattr(self, 'exported'):
            return self.exported

        cur = self.export_source()
        # we need the actual data, now.
        self.exported = list(self._export(cur))

        # delete all existing annotations
        notes = IAnnotations(cur)
        for key, obj in notes.items():
            if IExposureFileNote.providedBy(obj):
                del notes[key]

        return self.exported

    @button.buttonAndHandler(_('Migrate'), name='apply')
    def handleMigrate(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        try:
            self.migrate()
        except:
            self.status = self.formErrorsMessage
            return

    def migrate(self):
        target = self.context
        self.mold(target)

    def nextURL(self):
        return self.target.absolute_url()

    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(ExposureFileRegenerateForm, self).render()

ExposureFileRegenerateFormView = layout.wrap_form(ExposureFileRegenerateForm, 
    label="Exposure Regeneration")


class ExposureFileBulkRegenerateForm(form.Form):
    """\
    Exposure bulk regeneration form.
    """

    @button.buttonAndHandler(_('Migrate'), name='apply')
    def handleMigrate(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # search for all exposures
        catalog = getToolByName(self.context, 'portal_catalog')
        q = {
            'path': self.context.getPhysicalPath(),
            'portal_type': 'Exposure',
        }

        for b in catalog(**q):
            ctx = b.getObject()
            f = ExposureFileRegenerateForm(ctx, None)
            f.migrate()

ExposureFileBulkRegenerateFormView = layout.wrap_form(
    ExposureFileBulkRegenerateForm, 
    label="Exposure File Bulk Regeneration")


class WorkspaceExposureRollover(ExposurePort, WorkspaceLog):

    # more suitable interface name needed?
    zope.interface.implements(IExposureRolloverForm)
    _finishedAdd = False
    fields = z3c.form.field.Fields(IExposureRolloverForm)

    shortlog = True
    tbl = table.ExposureRolloverLogTable
    template = ViewPageTemplateFile('workspace_exposure_rollover.pt')

    def update(self):
        ExposurePort.update(self)
        WorkspaceLog.update(self)

    def export_source(self):
        return self.source_exposure

    @z3c.form.button.buttonAndHandler(_('Migrate'), name='apply')
    def handleMigrate(self, action):
        data, errors = self.extractData()
        if errors:
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                u'Please ensure both radio columns have been selected before '
                 'trying again.',
                'error')
            return

        # acquire default container
        try:
            exposure_container = restrictedGetExposureContainer()
            self.exposure_container = exposure_container
            self._gotExposureContainer = True
        except Unauthorized:
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                u'Unauthorized to create new exposure at default location.',
                'error')
            return

        # acquire source
        try:
            self.source_exposure = self.context.restrictedTraverse(
                data['exposure_path'])
        except Unauthorized:
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                u'Unauthorized to read exposure at selected location',
                'error')
            return
        except (AttributeError, KeyError):
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                u'Cannot find exposure at selected location.',
                'error')
            return


        eaf = ExposureAddForm(exposure_container, None)
        data = {
            'workspace': u'/'.join(self.context.getPhysicalPath()),
            'curation': None,  # to be copied later
            'commit_id': data['commit_id'],
        }
        eaf.createAndAdd(data)
        exp_id = data['id']
        target = exposure_container[exp_id]
        self.mold(target)
        self._finishedAdd = True
        self.target = target

    def nextURL(self):
        return self.target.absolute_url()

    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(WorkspaceExposureRollover, self).render()

WorkspaceExposureRolloverView = layout.wrap_form(
    WorkspaceExposureRollover,
    __wrapper_class=BorderedTraverseFormWrapper,
    label='Exposure Rollover'
)


