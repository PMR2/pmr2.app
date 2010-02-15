from zope.component import getUtility
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('pmr2')

import z3c.form
from plone.z3cform import layout
from pmr2.app.interfaces import IPMR2GlobalSettings #, get_pmr2_settings
from pmr2.app.browser import form


class PMR2GlobalSettingsEditForm(form.EditForm):

    fields = z3c.form.field.Fields(IPMR2GlobalSettings)

    def getContent(self):
        # ensure we get the one annotated to the site manager.
        return getUtility(IPMR2GlobalSettings)


PMR2GlobalSettingsEditFormView = layout.wrap_form(PMR2GlobalSettingsEditForm,
    label = _(u'PMR2 Core Configuration'))

