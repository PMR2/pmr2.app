import zope.interface
import zope.schema

from z3c.form.interfaces import ISelectWidget


class IStorageFileSelectWidget(ISelectWidget):
    """
    Select widget customized for the storage file list.
    """
