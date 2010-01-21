from os import getenv
from os.path import join

from persistent import Persistent
from zope.annotation import factory, IAttributeAnnotatable
from zope.component import getUtility
import zope.schema
import zope.interface
from zope.app.component.hooks import getSite, getSiteManager

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('pmr2')

try:
    from Products.CMFCore.interfaces import ISiteRoot
except ImportError:
    ISiteRoot = None

pmr2_settings = 'pmr2_settings'


class IPMR2GlobalSettings(zope.interface.Interface):
    """\
    Interface to hold global configuration settings.
    """

    repo_root = zope.schema.BytesLine(
        title=_(u'Repository Root'),
        description=_(u'The working root directory for PMR2, where the files '
                       'that make up the workspaces will be stored.'),
    )


class PMR2GlobalSettingsAnnotation(Persistent):
    zope.interface.implements(IPMR2GlobalSettings)
    zope.component.adapts(IAttributeAnnotatable)

    repo_root = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['repo_root'])

    def __init__(self):
        self.repo_root = _make_default_path()

PMR2GlobalSettings = factory(PMR2GlobalSettingsAnnotation)


def _make_default_path():
    # While ${SOFTWARE_HOME} is typically standard "default" location
    # for application specific files, this product is normally installed 
    # via buildout, hence this directory will be recreated on each 
    # reinstall.  This basically makes it a bad choice for storing any
    # persistent information as they will be unlinked every upgrade.
    # The ${CLIENT_HOME} is more stable, however it might not exist, so
    # we will have fallback.

    suffix = 'pmr2'
    envvar = ['CLIENT_HOME', 'SOFTWARE_HOME']

    for v in envvar:
        root = getenv(v, None)
        if root is not None:
            return join(root, suffix)

    # This should never happen, but None does not make a path.
    return ''
