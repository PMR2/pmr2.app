import json

import zope.interface
import zope.component
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.location import Location

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

import z3c.form

from plone.z3cform import layout
from plone.z3cform.fieldsets import group, extensible

from Products.statusmessages.interfaces import IStatusMessage

from pmr2.app.browser import form
from pmr2.app.browser import page
from pmr2.app.browser import widget

from pmr2.app.workspace.interfaces import ICurrentCommitIdProvider

from pmr2.app.exposure.interfaces import IExposure
from pmr2.app.exposure.browser.interfaces import IExposureExportImportGroup
from pmr2.app.exposure.browser.interfaces import IExposureFileGenForm
from pmr2.app.exposure.browser.interfaces import IExposureWizardForm
from pmr2.app.exposure.browser.browser import BaseExposureFileTypeAnnotatorForm
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile
from pmr2.app.exposure.browser.browser import ExposurePort
from pmr2.app.exposure.browser.util import moldExposure

from pmr2.app.exposure.browser.workspace import *


def _changeWizard(exposure):
    wh = zope.component.getAdapter(exposure, IExposureWizard)
    structure = []
    if wh.structure:
        structure.extend(wh.structure)
    wh.structure = structure


class StructureWrapper(Location):
    """\
    Internal use structure wrapper for dicts.

    Instead of using dict directly and let the DataManager for dict
    manager the data acquisition, we are doing this long way because of
    key/value pairs that are assigned to the dict that are not defined
    within the interface of the annotator that will ultimately assign
    the values defined within it to the actual annotation.  A better fix
    would probably define our own custom DataManager for this entire
    thing, but the effort involved will be much greater than writing
    bridges between the predefined managers and forms.
    """
    
    def __init__(self, context=None, structure=None):
        self.__parent__ = context
        self._structure = structure
        if structure:
            for k, v in structure.iteritems():
                setattr(self, k, v)

    def _original(self):
        return self._structure


class BaseSubGroup(form.Form, form.Group):

    zope.interface.implements(ICurrentCommitIdProvider)

    ignoreContext = False

    # None as in undefined, True is collapsed, False is expanded
    collapseState = None

    @property
    def collapsible(self):
        return not self.collapseState is None

    @property
    def collapsibleCss(self):
        if not self.collapsible:
            return ''
        state = self.collapseState and ' collapsedOnLoad' or ''
        return 'collapsible%s' % state

    def current_commit_id(self):
        return self.context.commit_id

    def getStructure(self):
        # assigned by constructor.
        return self.structure

    def getContent(self):
        # assigned by constructor.
        obj = StructureWrapper(self, self.getStructure())
        if hasattr(self, 'field_iface') and self.field_iface:
            zope.interface.alsoProvides(obj, self.field_iface)
        else:
            # XXX
            self.ignoreContext = True
            zope.interface.alsoProvides(obj, zope.interface.Interface)
        return obj


class BaseAnnotationGroup(BaseSubGroup):
    """\
    Subgroups for the annotator

    This is created in place.
    """

    def getStructure(self):
        content = self.parentForm.getContent()
        views = dict(content.views)
        return views[self.__name__]


class BaseWizardGroup(BaseSubGroup):
    """\
    Subgroups for the wizard.

    This is a mixin with the workspace creation subgroups to add the
    update button.
    """

    structure = None
    filename = None
    new_filename = None
    deleted = False
    pos = None

    collapseState = False
    showDeleteButton = True
    showClearButton = True

    @z3c.form.button.buttonAndHandler(_('Update'), name='update')
    def handleUpdate(self, action):
        """\
        Call update and update the structure we have.
        """

        result = self.generateStructure()
        if not result:
            return

        filename, structure = result

        # as this is a direct reference to the wizard's structure, it
        # will be updated if the structure attribute is pinged.
        if structure:
            self.structure.update(structure)
            self.parentForm._updated = True

        if self.filename != filename:
            self.new_filename = filename
            self.parentForm._updated = True

    def showClearButtonState(self):
        return self.showClearButton

    @z3c.form.button.buttonAndHandler(_('Clear Subgroup'), name='clear',
            condition=showClearButtonState)
    def handleClear(self, action):
        """\
        Clear this group.

        This will clear the groups associated with the filetype and so
        allowing the selection of a different one for a new set of 
        groups.
        """

        self.structure.clear()
        self.parentForm._updated = True

    def showDeleteButtonState(self):
        return self.showDeleteButton

    @z3c.form.button.buttonAndHandler(_('Delete'), name='delete',
            condition=showDeleteButtonState)
    def handleDelete(self, action):
        """\
        Delete this group.
        """

        # XXX this only mark the structure as deleted as the actual
        # list entry (with the filename) can't be directly manipulated
        # here, as it is not the content.
        self.deleted = True
        self.parentForm._updated = True


def mixin_wizard(groupform, static=False):
    class WizardGroupMixed(BaseWizardGroup, groupform):
        showDeleteButton = not static
        showClearButton = not static
        def __repr__(self):
            return '<%s for <%s.%s> object at %x>' % (
                self.__class__.__name__, 
                groupform.__module__,
                groupform.__name__,
                id(self),
            )

    #assert IDocGenSubgroup.implementedBy(groupform)
    return WizardGroupMixed

# The subforms that need this.

ExposureViewGenWizardGroup = mixin_wizard(ExposureViewGenGroup, static=True)
ExposureFileChoiceTypeWizardGroup = mixin_wizard(ExposureFileChoiceTypeGroup)


class ExposureFileTypeAnnotatorWizardGroup(
        BaseWizardGroup,
        BaseExposureFileTypeAnnotatorForm,
        ):
    
    zope.interface.implements(z3c.form.interfaces.ISubForm)
    fields = z3c.form.field.Fields(IExposureFileGenForm)
    field_iface = IExposureFileGenForm

    # while this can be a property based on file name, this assumption
    # is subject to change.
    prefix = 'annotate'

    empty_groups = None

    def __init__(self, *a, **kw):
        super(ExposureFileTypeAnnotatorWizardGroup, self).__init__(*a, **kw)
        self.empty_groups = []

    def getContent(self):
        obj = BaseWizardGroup.getContent(self)
        obj.filename = self.filename
        return obj

    def generateStructure(self):
        data, errors = self.extractData()
        obj = self.getContent()

        # grab original
        groups = self.split_groups(data)
        # maintain original ordering.
        views = [(k, k in groups and dict(groups[k]) or None) 
            for k, v in obj.views]

        filename = data['filename']

        # final result to update the parent structure with.
        structure = (filename, {
            'views': views,
        })

        return structure


class ExposureWizardForm(form.PostForm, extensible.ExtensibleForm):
    """\
    The exposure wizard.
    """

    zope.interface.implements(IExposureWizardForm)

    ignoreContext = True
    enable_form_tabbing = False

    _updated = False
    _next = None

    def __init__(self, *a, **kw):
        super(ExposureWizardForm, self).__init__(*a, **kw)
        self.fields = z3c.form.field.Fields()

    def update(self):
        # No need to call form.PostForm.update because that path added
        # nothing.
        self.appendGroups()
        extensible.ExtensibleForm.update(self)
        self.updateGroups()

    def appendViewGroup(self):
        wh = zope.component.getAdapter(self.context, IExposureWizard)

        self.viewGroup = ExposureViewGenWizardGroup(
            self.context, self.request, self)
        self.viewGroup.structure = {}
        self.viewGroup.filename = ''
        if isinstance(wh.structure, list) and wh.structure:
            # is a list and not empty.
            self.viewGroup.structure = wh.structure[-1][1]
        else:
            # initiate the structure in wizard helper with empty set.
            wh.structure = [('', {
                # XXX this structure is duping.
                'commit_id': self.viewGroup.current_commit_id(),
                'curation': {},
                'docview_generator': None,
                'docview_gensource': None,
                'title': u'',
                'workspace': self.context.workspace,
                'Subject': (),
            })]
        self.groups.append(self.viewGroup)

    def appendGroups(self):
        self.groups = []


        self.appendViewGroup()
        # handle the rest.

        wh = zope.component.getAdapter(self.context, IExposureWizard)
        structures = wh.structure[:-1]

        for i, o in enumerate(structures):
            filename, structure = o
            if filename is None or not structure:
                grp = ExposureFileChoiceTypeWizardGroup(
                    self.context, self.request, self)
            else:
                grp = ExposureFileTypeAnnotatorWizardGroup(
                    self.context, self.request, self)

            grp.pos = i
            grp.filename = filename
            grp.structure = structure
            grp.prefix = grp.prefix + str(i)
            self.groups.append(grp)

    def updateGroups(self):
        # XXX this is a hack around the current implementation. it might 
        # be better to keep the data in the groups and do the mass 
        # manipulation here and just here only.  See the method 
        # associated with the update button in the mixin class above.

        wh = zope.component.getAdapter(self.context, IExposureWizard)

        # XXX skip the first one, base on assumption that the view is
        # going to be first.
        for g in self.groups[1:]:
            if g.deleted:
                # Have to manipulate the current structure.
                del wh.structure[g.pos]
                continue

            if g.new_filename is None:
                continue

            # so we have a new file name, the entry will be replaced.
            wh.structure[g.pos] = (g.new_filename, g.structure)

        # trigger the update (ping it).
        _changeWizard(self.context)

    @z3c.form.button.buttonAndHandler(_('Build'), name='build')
    def handleBuild(self, action):
        """\
        Build the thing
        """

        wh = zope.component.getAdapter(self.context, IExposureWizard)
        moldExposure(self.context, self.request, wh.structure)
        self._updated = True
        self._next = ''

    @z3c.form.button.buttonAndHandler(_('Add File'), name='add_file')
    def handleAddFile(self, action):
        """\
        Add a blank file structure.
        """

        structure = (None, {
           'file_type': None,
        })
        wh = zope.component.getAdapter(self.context, IExposureWizard)
        wh.structure.insert(-1, structure)
        _changeWizard(self.context)
        self._updated = True

    # subform removes file.

    @z3c.form.button.buttonAndHandler(_('Revert'), name='revert')
    def handleRevert(self, action):
        """\
        Revert the states to what is in the structure.
        """

        porter = ExposurePort(self.context, self.request)
        structure = list(porter.export())
        wh = zope.component.getAdapter(self.context, IExposureWizard)
        wh.structure = structure
        self._updated = True

    def render(self):
        next = self._next
        if self._next is None:
            next = '/@@wizard'

        if self._updated:
            self.request.response.redirect(
                self.context.absolute_url() + next)
            return ''
            
        return super(ExposureWizardForm, self).render()


class ExposureFileTypeWizardGroupExtender(extensible.FormExtender):
    # For subform
    # XXX refactor and merge this with the standard form

    zope.component.adapts(
        IExposure, IBrowserRequest, ExposureFileTypeAnnotatorWizardGroup)

    @property
    def viewsEnabled(self):
        # return a list of views that are enabled.
        return [k for k, v in self.form.structure['views']]

    def _update(self):
        for name in self.viewsEnabled:
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

    def update(self):
        # for the format may have changed, we have a wrapper of sort.
        try:
            self._update()
        except:
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                _(
                    'There were errors loading the wizard due to corrupted '
                    'data.  Please discard all changes and restart the wizard.'
                ),
                'error'
            )

    def add(self, annotator):
        fields = self.makeField(annotator)
        if not fields.keys():
            # Rather than rendering an empty box, return nothing
            self.form.empty_groups.append(annotator.title)
            return

        # XXX name may need to reference the path to the file
        name = str(annotator.__name__)
        context = self.context

        # make the group and assign data.
        g = BaseAnnotationGroup(context, self.request, self.form)
        g.__name__ = annotator.__name__
        g.label = annotator.title
        g.fields = fields
        g.prefix = self.form.prefix
        g.field_iface = annotator.for_interface

        # finally append this group
        self.form.groups.append(g)

    def makeField(self, annotator):
        # XXX this method could potentially be refactored out into an 
        # adapter as this is copied from browser
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

