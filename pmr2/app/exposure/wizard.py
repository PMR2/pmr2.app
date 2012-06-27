import zope.component
import zope.interface
from zope.schema import fieldproperty
from zope.app.container.contained import Contained
from zope.annotation.interfaces import IAnnotations
from zope.annotation import factory
from persistent import Persistent

from pmr2.app.exposure.interfaces import IExposure, IExposureWizard


class ExposureWizard(Persistent, Contained):
    """\
    Exposure wizard.
    """

    zope.component.adapts(IExposure)
    zope.interface.implements(IExposureWizard)
    structure = fieldproperty.FieldProperty(IExposureWizard['structure'])

    def updateFromExposure(self):
        """\
        Generate a new structure from the exposure.
        """

        pass

ExposureWizardFactory = factory(ExposureWizard)
