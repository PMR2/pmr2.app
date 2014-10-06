import zope.component
import zope.interface
import zope.schema

from plone.registry.interfaces import IRegistry
import z3c.form
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget

from pmr2.z3cform import form

from pmr2.app.workflow.interfaces import ISettings


class SettingsEditForm(form.EditForm):
    """
    Workflow settings edit form.
    """

    fields = z3c.form.field.Fields(ISettings)
    fields['wf_send_email'].widgetFactory = SingleCheckBoxFieldWidget

    def update(self):
        super(SettingsEditForm, self).update()
        self.request['disable_border'] = True

    def getContent(self):
        registry = zope.component.getUtility(IRegistry)
        return registry.forInterface(
            ISettings,
            prefix='pmr2.app.workflow.settings',
        )

