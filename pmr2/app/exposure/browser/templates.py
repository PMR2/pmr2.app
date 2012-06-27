import os.path

import z3c.form.interfaces
from plone.z3cform.templates import ZopeTwoFormTemplateFactory

from pmr2.app.exposure.browser.interfaces import IExposureWizardForm
from pmr2.app.interfaces import IPMR2AppLayer

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)

wizard_form_factory = ZopeTwoFormTemplateFactory(path('wizard.pt'),
        form=IExposureWizardForm,
        request=IPMR2AppLayer,
    )
