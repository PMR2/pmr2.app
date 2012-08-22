from os.path import join
import json
import urllib2

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
from zope.schema.interfaces import RequiredMissing
from zope.annotation.interfaces import IAnnotations
from zope.publisher.interfaces import NotFound
from zope.publisher.browser import BrowserPage
from zope.i18nmessageid import MessageFactory
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.container.interfaces import IContainer
_ = MessageFactory("pmr2")

import z3c.form.field
from z3c.form import button
from plone.memoize.view import memoize
from plone.z3cform import layout
from plone.z3cform.fieldsets import group, extensible

from Acquisition import aq_parent, aq_inner
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream
from Products.statusmessages.interfaces import IStatusMessage

from zope.app.pagetemplate.viewpagetemplatefile \
    import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from pmr2.app.workspace.browser.browser import WorkspaceLog
from pmr2.app.workspace.interfaces import IStorage, ICurrentCommitIdProvider
from pmr2.app.workspace.exceptions import *

from pmr2.app.exposure import table

from pmr2.app.exposure.interfaces import *
from pmr2.app.exposure.browser.interfaces import *

from pmr2.app.interfaces import *
from pmr2.app.interfaces.exceptions import *
from pmr2.app.browser.interfaces import *
from pmr2.app.annotation.interfaces import *
from pmr2.app.annotation.factory import has_note, del_note
from pmr2.app.exposure.content import *

from pmr2.app.browser import form
from pmr2.app.browser import page
from pmr2.app.browser import widget
from pmr2.app.browser.layout import *

from pmr2.app.exposure.browser.util import *
from pmr2.app.exposure.urlopen import urlopen


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
    label = "Exposure Create Form"

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


class ExposureEditForm(form.EditForm):
    """\
    Exposure editing form.
    """

    fields = z3c.form.field.Fields(IExposure).select(
        'title',
        'curation',
    )
    label = "Exposure Edit Form"


class ExposureEditCurationForm(form.EditForm):
    """\
    Exposure editing form.
    """

    fields = z3c.form.field.Fields(IExposure).select(
        'curation',
    )
    label = "Curation Editor"


class ExposureFileGenForm(form.AddForm):
    """\
    Form to generate an exposure file (encapsulates an actual file in a
    workspace).
    """

    zope.interface.implements(ICurrentCommitIdProvider)

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    fields = z3c.form.field.Fields(IExposureFileGenForm)

    label = "Add a file to the exposure"

    def current_commit_id(self):
        return self.context.commit_id

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



class ExposureFileAnnotatorForm(form.BaseAnnotationForm):
    """\
    Form to add a note to an ExposureFile.
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    fields = z3c.form.field.Fields(IExposureFileAnnotatorForm)
    label = "Add an annotation to an Exposure File."

    @button.buttonAndHandler(_('Annotate'), name='apply')
    def handleAnnotate(self, action):
        self.baseAnnotate(action)

    def annotate(self):
        annotatorFactory = zope.component.getUtility(
            IExposureFileAnnotator,
            name=self._data['annotators']
        )
        annotator = annotatorFactory(self.context, self.request)
        annotator()

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


class ExposureFileTypeAddForm(form.AddForm):
    """\
    ExposureFileType creation form.
    """

    fields = z3c.form.field.Fields(IObjectIdMixin) + \
             z3c.form.field.Fields(IExposureFileType)
    clsobj = ExposureFileType
    label = "Exposure File Type creator"

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']
        ctxobj.views = self._data['views']
        ctxobj.select_view = self._data['select_view']
        ctxobj.tags = self._data['tags']
        

class ExposureFileTypeEditForm(form.EditForm):
    """\
    ExposureFileType editing form.
    """

    fields = z3c.form.field.Fields(IExposureFileType)
    label = "Exposure File Type editor"

    def update(self):
        super(ExposureFileTypeEditForm, self).update()


class ExposureFileTypeDisplayForm(form.DisplayForm):
    """\
    ExposureFileType creation form.
    """

    fields = z3c.form.field.Fields(IExposureFileType)
    label = "Exposure File Type viewer"


class ExposureFileTypeChoiceForm(form.PostForm):
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
    label = "Add an annotation to an Exposure File."

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


class BaseExposureFileTypeAnnotatorForm(
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

    enable_form_tabbing = False

    def __init__(self, *a, **kw):
        super(BaseExposureFileTypeAnnotatorForm, self).__init__(*a, **kw)
        self.groups = []

    def split_groups(self, data):
        # have to process the data as it's merged between all the forms
        # due to heavy customization of this particular subgroup 
        # processing method.
        groups = {}
        for k, value in data.iteritems():
            if '.' not in k:
                # data can be mixed, only prefixed ids are wanted.
                continue
            group, key = k.split('.', 1)
            if not group in groups:
                groups[group] = []
            groups[group].append((key, value,))
        return groups

    def annotate(self):
        """
        Goes through the notes and adapt to each specific annotator.

        XXX this assumes nobody changed what this form had and what the
        self.context.views contains now.
        """

        groups = self.split_groups(self._data)
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
            annotator = annotatorFactory(self.context, self.request)
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


class ExposureFileTypeAnnotatorForm(BaseExposureFileTypeAnnotatorForm):

    label = "Add an annotation to an Exposure File."

    @button.buttonAndHandler(_('Annotate'), name='apply')
    def handleAnnotate(self, action):
        self.baseAnnotate(action)


class ExposureFileTypeAnnotatorExtender(extensible.FormExtender):
    zope.component.adapts(
        IExposureFile, IBrowserRequest, ExposureFileTypeAnnotatorForm)

    def update(self):
        for name in self.context.views:
            # XXX self.context.views should be a tuple of ascii values
            # taken from the constraint vocabulary of installed views.
            name = name.encode('ascii', 'replace')
            annotatorFactory = zope.component.queryUtility(
                IExposureFileAnnotator, name=name)
            if not annotatorFactory:
                # silently ignore missing fields.
                continue

            annotator = annotatorFactory(self.context, self.request)
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

    label = "Edit an Exposure File Note."

    def getContent(self):
        return self.note

    def applyChanges(self, data):
        results = super(ExposureFileNoteEditForm, self).applyChanges(data)
        name = '/'.join(self.traverse_subpath)
        annotatorFactory = zope.component.getUtility(
            IExposureFileAnnotator, name=name)
        # since this form already assigns the data, we don't need to
        # pass in data for the call method for assignment, but we need
        # an empty tuple (for now)
        annotator = annotatorFactory(self.context, self.request)
        annotator(())
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
            raise NotFound(self.context, self.context.title_or_id())
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


class ExposureFileNoteArrangeForm(form.EditForm):
    """\
    Form to allow rearrangement of notes
    """

    #zope.interface.implements(IExposureFileNoteArrangeForm)
    fields = z3c.form.field.Fields(IExposureFile).select('views')
    label = "Arrange Exposure File Notes."

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


class ExposureDocViewGenForm(form.BaseAnnotationForm):
    """\
    Form to generate the default view of the base exposure.
    """

    ignoreContext = False

    zope.interface.implements(ICurrentCommitIdProvider, 
        IExposureDocViewGenForm)

    fields = z3c.form.field.Fields(IExposureDocViewGenForm)
    label = "Generate Default View for Exposure."

    def current_commit_id(self):
        return self.context.commit_id

    def getContent(self):
        # since we are not using the same interface as the exposure
        # object as it does not use choice, to populate the values here
        # will require an adapter.
        return zope.component.getAdapter(self.context, IExposureDocViewGenForm)

    @button.buttonAndHandler(_('Generate'), name='apply')
    def handleGenerate(self, action):
        self.baseAnnotate(action)

    def annotate(self):
        if not self._data['docview_gensource'] is None:
            # XXX manual unicode call, because vocab derives data directly
            # from manifest in mercurial, which is str.
            self.context.docview_gensource = \
                unicode(self._data['docview_gensource'])
        self.context.docview_generator = self._data['docview_generator']
        if not self.context.docview_generator:
            # reset the gensource to None when we don't have a 
            # generator, and do nothing.
            self.context.docview_gensource = None
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


class ExposureInfo(page.SimplePage):
    """\
    Simple exposure information display 
    
    This is for folder-like Exposure obejcts.  This should redirect to
    the actual content if there is only one item, or display a page that
    will direct to those items.

    If there are documentation assigned to this item, render them
    instead.
    """

    render = ViewPageTemplateFile('exposure_docview.pt')

    def subtitle(self):
        return self.context.Description()

    def content(self):
        return self.context.getText()

    def render(self):
        # could check for source, but users can manually edit this page,
        # no need to take away this feature, yet.
        if self.content():
            return super(ExposureInfo, self).render()

        catalog = getToolByName(self.context, 'portal_catalog')
        efiles = catalog(path={
            'query': '/'.join(self.context.getPhysicalPath()),
            'depth': 1
        })

        if len(efiles) == 0:
            # no item to render, do default thing.
            return super(ExposureInfo, self).render()

        if len(efiles) > 1:
            # should figure out how to generate a list of available
            # items for user consumption.  For now, default.
            return super(ExposureInfo, self).render()

        # XXX maybe control this with another setting too?
        # since we have exactly one item, it should redirect to its
        # default view.
        return self.request.response.redirect(efiles[0].getURL() + '/view')


class ExposureFileInfo(page.TraversePage):
    """\
    Base view of an ExposureFile object.  Shows the list of adapters.
    """

    content = ViewPageTemplateFile('exposure_file_info.pt')
    subtitle = u'Exposure File Information'


class ExposureFileSelectViewForm(form.EditForm):
    """\
    Form to select a note view for exposure files.
    """

    fields = z3c.form.field.Fields(IExposureFileSelectView).select(
        'selected_view')
    label = "Select Default View"

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


class ExposureFileDocument(page.TraversePage):
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


class ExposureFileRedirect(BrowserPage):
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

    index = ViewPageTemplateFile('code.pt')
    description = u'The following is a raw text representation of the file.'
    subtitle = u'Raw text view'

    @memoize
    def content(self):
        return self.note.text


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
            return view()
        # XXX set an information note about invalid choice?
        return self.template()


# utility

class ExposurePort(form.PostForm):
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
                # we are ignoring other folder types, let an adapter
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

        exported = self.export()
        return moldExposure(target, self.request, exported)


class ExposurePortJsonExport(ExposurePort):
    """\
    Export the structure as json.
    """

    def render(self):
        result = list(self.export())
        return json.dumps(result)


class ExposurePortCommitIdForm(ExposurePort):

    # this just have commit id, create exposure.

    formErrorsMessage = _('There are errors')

    _finishedAdd = False
    fields = z3c.form.field.Fields(IExposure).select(
        'commit_id',
    )
    label = "Exposure Port to new commit id"

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


class ExposureFileRegenerateForm(ExposurePort):
    """\
    This is to regenerate all exposure file notes.
    """

    # this just have commit id, create exposure.

    formErrorsMessage = _('There are errors with regeneration.')
    label = "Exposure Regeneration"
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


class ExposureFileBulkRegenerateForm(form.PostForm):
    """\
    Exposure bulk regeneration form.
    """

    label = "Exposure File Bulk Regeneration"

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


class WorkspaceExposureRollover(ExposurePort, WorkspaceLog):

    # more suitable interface name needed?
    zope.interface.implements(IExposureRolloverForm)
    _finishedAdd = False
    fields = z3c.form.field.Fields(IExposureRolloverForm)
    label = 'Exposure Rollover'

    shortlog = True
    tbl = table.ExposureRolloverLogTable
    template = ViewPageTemplateFile('workspace_exposure_rollover.pt')

    def update(self):
        self.request['enable_border'] = True
        ExposurePort.update(self)
        WorkspaceLog.update(self)

    def export_source(self):
        return self.source_exposure

    # acquire default container
    def getDefaultExposureContainer(self):
        try:
            exposure_container = restrictedGetExposureContainer()
            self._gotExposureContainer = True
        except:
            raise ProcessingError(
                u'Unauthorized to create new exposure at default location.')
        return exposure_container

    def acquireSource(self, exposure_path):
        try:
            source_exposure = self.context.restrictedTraverse(
               exposure_path)
        except Unauthorized:
            raise ProcessingError(
                u'Unauthorized to read exposure at selected location')
        except (AttributeError, KeyError):
            raise ProcessingError(
                u'Cannot find exposure at selected location.')
        return source_exposure

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

        try:
            exposure_container = self.getDefaultExposureContainer()
            self.source_exposure = self.acquireSource(data['exposure_path'])
        except ProcessingError, e:
            raise z3c.form.interfaces.ActionExecutionError(e)

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
