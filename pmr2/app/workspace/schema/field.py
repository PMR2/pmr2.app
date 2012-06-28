import zope.interface
import zope.schema

from pmr2.app.workspace.schema.interfaces import IStorageFileChoice


class StorageFileChoice(zope.schema.Choice):
    """
    Choice field for the list of Storage Files.
    """

    zope.interface.implements(IStorageFileChoice)
