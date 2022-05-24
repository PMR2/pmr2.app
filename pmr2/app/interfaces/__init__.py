import zope.schema
import zope.interface

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from plone.app.z3cform.interfaces import IPloneFormLayer
from pmr2.app.schema import ObjectId
from pmr2.app.interfaces.exceptions import *

__all__ = [
    'IPMR2AppLayer',
    'IPMR2KeywordProvider',
]


# Interfaces

class IPMR2AppLayer(IPloneFormLayer):
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


class IRegistrySettings(zope.interface.Interface):
    """
    Settings to be registered to the configuration registry.
    """

    github_issue_repo = zope.schema.TextLine(
        title=u'The uri to the Github issue repository',
        description=u'The repository to file issues with user data on PMR',
        default=u'',
        required=False,
    )
