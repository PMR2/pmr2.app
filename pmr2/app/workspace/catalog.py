import zope.interface
import logging
from plone.indexer import indexer
from Products.CMFCore.utils import getToolByName

from pmr2.app.schema.converter import curation_to_textline_list
from pmr2.app.workspace.interfaces import IWorkspace
from pmr2.app.workspace.interfaces import IStorage

logger = logging.getLogger(__name__)


@indexer(IWorkspace)
def pmr2_workspace_storage_roots(self):
    """
    Index the roots of all the underlying storage.
    """

    try:
        storage = IStorage(self)
        return storage.roots()
    except NotImplementedError:
        return []
    except Exception:
        logger.exception('failed to derive roots for storage of %s', self)
        return []
