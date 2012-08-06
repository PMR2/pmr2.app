import os.path

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from pmr2.testing.base import IPMR2TestRequest
from pmr2.app.exposure.browser.interfaces import IExposureWizardForm

from pmr2.app.exposure.browser import templates


class Macros(templates.Macros):
    """\
    Extension to the default macros.
    """

    index = ViewPageTemplateFile('macros.pt')
