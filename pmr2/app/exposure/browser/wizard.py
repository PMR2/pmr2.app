import json

import zope.interface
import zope.component

import z3c.form

from plone.z3cform import layout
from plone.z3cform.fieldsets import group, extensible

from pmr2.app.browser import form
from pmr2.app.browser import page
from pmr2.app.browser import widget
from pmr2.app.browser.layout import *

from pmr2.app.exposure.browser.interfaces import ICreateExposureForm
from pmr2.app.exposure.browser.workspace import CreateExposureForm


class ExposureWizard(form.EditForm):
    """\
    The exposure wizard.
    """

    # XXX temporary.
    ignoreContext = True
    fields = z3c.form.field.Fields(ICreateExposureForm)

ExposureWizardView = layout.wrap_form(ExposureWizard,
    __wrapper_class=TraverseFormWrapper,
    label="Exposure Wizard")
