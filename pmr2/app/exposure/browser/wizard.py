import json

import zope.interface
import zope.component
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

import z3c.form

from plone.z3cform import layout
from plone.z3cform.fieldsets import group, extensible

from pmr2.app.browser import form
from pmr2.app.browser import page
from pmr2.app.browser import widget
from pmr2.app.browser.layout import *

from pmr2.app.exposure.interfaces import IExposure
from pmr2.app.exposure.browser.interfaces import IExposureExportImportGroup
from pmr2.app.exposure.browser.interfaces import IExposureFileGenForm
from pmr2.app.exposure.browser.interfaces import IExposureWizardForm
from pmr2.app.exposure.browser.browser import ExposureFileTypeAnnotatorForm
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile


class ExposureWizardForm(form.PostForm):
    """\
    The exposure wizard.
    """

    zope.interface.implements(IExposureWizardForm)

    # XXX temporary.
    ignoreContext = True
    fields = z3c.form.field.Fields(IExposureExportImportGroup)

