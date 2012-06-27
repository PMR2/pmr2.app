import os.path

from plone.z3cform.templates import ZopeTwoFormTemplateFactory

from pmr2.testing.base import IPMR2TestRequest
from pmr2.app.exposure.browser.interfaces import IExposureWizardForm

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)

wizard_form_factory = ZopeTwoFormTemplateFactory(path('wizard.pt'),
        form=IExposureWizardForm,
        request=IPMR2TestRequest,
    )
