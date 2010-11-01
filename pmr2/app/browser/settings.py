import zope.interface
import zope.component
from zope.location import Location, locate
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.container.interfaces import IContainer
_ = MessageFactory('pmr2')

import z3c.form
from plone.z3cform import layout
from plone.z3cform.fieldsets import group, extensible
from pmr2.app.content.interfaces import IExposureFile
from pmr2.app.interfaces import IPMR2GlobalSettings, IPMR2PluggableSettings
from pmr2.app.browser import form


class PMR2GlobalSettingsEditForm(extensible.ExtensibleForm, form.EditForm):

    fields = z3c.form.field.Fields(IPMR2GlobalSettings).omit('subsettings')

    def __init__(self, *a, **kw):
        super(PMR2GlobalSettingsEditForm, self).__init__(*a, **kw)
        # the group lists needs to be instantiated per object and not
        # use the parent class.
        self.groups = []

    def getContent(self):
        # ensure we get the one annotated to the site manager.
        return zope.component.getUtility(IPMR2GlobalSettings)

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        # have to repeat the definition here because a new button in
        # a class overwrites the ones from parent classes.
        return form.EditForm.handleApply(self, action)

    @z3c.form.button.buttonAndHandler(_('Apply and Create Objects'),
                                      name='apply_and_create')
    def handleApplyAndCreate(self, action):
        # Call handleApply first
        form.EditForm.handleApply(self, action)
        # have to read a string as the method above has no return value
        if self.status == self.formErrorsMessage:
            return
        
        results = []
        settings = self.getContent()
        try:
            created = settings.createDefaultWorkspaceContainer()
            if created:
                results.append('Created Workspace Container.')
            else:
                results.append('Workspace Container already exists.')
        except:
            results.append('Failed to created Workspace Container.')
            raise

        try:
            settings.createDefaultExposureContainer()
            if created:
                results.append('Created Exposure Container.')
            else:
                results.append('Exposure Container already exists.')
        except:
            results.append('Failed to created Exposure Container.')

        self.status = self.status + ' '.join(results)


PMR2GlobalSettingsEditFormView = layout.wrap_form(PMR2GlobalSettingsEditForm,
    label = _(u'PMR2 Core Configuration'))


class PMR2PluginSettingsExtender(extensible.FormExtender):
    zope.component.adapts(
        IContainer, IBrowserRequest, PMR2GlobalSettingsEditForm)

    def update(self):
        utilities = zope.component.getUtilitiesFor(IPMR2PluggableSettings)
        for name, utility in utilities:
            prefix = utility.name
            title = utility.title
            if utility.fields:
                fields = utility.fields
            else:
                # Assumption
                interface = list(zope.interface.implementedBy(
                    utility.factory))[0]
                fields = z3c.form.field.Fields(interface, prefix=prefix)
            self.add(fields, group=title)
