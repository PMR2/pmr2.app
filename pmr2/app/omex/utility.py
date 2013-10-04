import zope.component
from zope.interface import implementer

from pmr2.app.workspace.interfaces import IStorageArchiver

from .omex import build_omex


@implementer(IStorageArchiver)
class OmexStorageArchiver(object):

    label = u'COMBINE Archive'
    suffix = '.omex'
    mimetype = 'application/vnd.combine.omex'

    def enabledFor(self, storage):
        try:
            manifest = storage.file('manifest.xml')
            return True
        except:
            return False

    def archive(self, storage):
        return build_omex(storage)
