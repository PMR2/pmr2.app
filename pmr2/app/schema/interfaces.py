import zope.schema.interfaces

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")


class InvalidObjectId(zope.schema.interfaces.ValidationError):
    __doc__ = _("""The specified object id is not valid.""")


class IObjectId(zope.schema.interfaces.IBytesLine):
    """\
    A field containing a valid Zope object id.
    """


class IWorkspaceList(zope.schema.interfaces.IList):
    """\
    Workspace list field.  Meant to be used in conjunction with
    zope.schema.accessor.
    """


class ICurationDict(zope.schema.interfaces.IDict):
    """\
    Curation dictionary.
    """
