import zope.deprecation
import zope.schema
import zope.interface

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from pmr2.app.schema import ObjectId
from pmr2.app.interfaces.exceptions import *

from pmr2.app.settings.interfaces import IPMR2GlobalSettings

zope.deprecation.deprecated('IPMR2GlobalSettings',
    'Please run migration script for pmr2.app-0.4 before 0.5 is installed.')

__all__ = [
    'IPMR2AppLayer',
    'IPMR2KeywordProvider',
]


# Interfaces

class IPMR2AppLayer(zope.interface.Interface):
    """\
    Marker interface for this product.
    """


class IPMR2KeywordProvider(zope.interface.Interface):
    """\
    A provider of keywords that are captured from the object.

    Even though currently notes are the primary provider of data, which
    by extension provides the keywords for a particular file, the 
    indexed terms will be anchored on the parent object rather than the
    note.  If a note wish to manually be referenced it must generate the
    right values which can uniquely identify the note, and the view must
    be overridden to link to the intended results.
    """
