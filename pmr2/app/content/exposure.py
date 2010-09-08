import zope.deprecation

from pmr2.app.exposure.content import Exposure
from pmr2.app.exposure.content import ExposureContainer
from pmr2.app.exposure.content import ExposureFile
from pmr2.app.exposure.content import ExposureFileType
from pmr2.app.exposure.content import ExposureFolder

zope.deprecation.deprecated('Exposure',
    'Please use the archetype tool in the ZMI to update the schema for '
    'Exposure before pmr2.app-0.5.')

zope.deprecation.deprecated('ExposureContainer',
    'Please use the archetype tool in the ZMI to update the schema for '
    'ExposureContainer before pmr2.app-0.5.')

zope.deprecation.deprecated('ExposureFile',
    'Please use the archetype tool in the ZMI to update the schema for '
    'ExposureFile before pmr2.app-0.5.')

zope.deprecation.deprecated('ExposureFileType',
    'Please use the archetype tool in the ZMI to update the schema for '
    'ExposureFileType before pmr2.app-0.5.')

zope.deprecation.deprecated('ExposureFolder',
    'Please use the archetype tool in the ZMI to update the schema for '
    'ExposureFolder before pmr2.app-0.5.')
