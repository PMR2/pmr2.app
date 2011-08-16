import re

import zope.interface
import zope.schema

from pmr2.app.schema.interfaces import InvalidObjectId
from pmr2.app.schema.interfaces import IObjectId, IWorkspaceList, ICurationDict
from pmr2.app.schema.interfaces import ITextLineList


_isobjectid = re.compile(r'^[a-zA-Z0-9_\.\-]*$').match

class ObjectId(zope.schema.BytesLine):
    """\
    This is implemented because zope.schema.Id does not work as
    advertised.
    """

    zope.interface.implements(IObjectId)

    def _validate(self, value):
        """\
        >>> id = ObjectId(__name__='test')
        >>> id.validate("foo")
        >>> id.validate("foo.bar")
        >>> id.validate("foo/bar")
        Traceback (most recent call last):
        ...
        InvalidObjectId: foo/bar
        >>> id.validate("foo bar")
        Traceback (most recent call last):
        ...
        InvalidObjectId: foo bar
        >>> id.validate("http://www.example.org/foo/bar")
        Traceback (most recent call last):
        ...
        InvalidObjectId: http://www.example.org/foo/bar
        """

        super(ObjectId, self)._validate(value)
        if _isobjectid(value):
            return

        raise InvalidObjectId(value)


class WorkspaceList(zope.schema.List):
    """\
    Workspace listing field.
    """

    zope.interface.implements(IWorkspaceList)


class CurationDict(zope.schema.Dict):
    """\
    Curation dictionary.
    """

    zope.interface.implements(
        ICurationDict, 
        zope.schema.interfaces.IFromUnicode,
    )

    key_type = zope.schema.TextLine(
        title=u'Key',
    )
    value_type = zope.schema.List(
        title=u'Value',
        value_type=zope.schema.TextLine(title=u'Values',),
    )

    def fromUnicode(self, u):
        """\
        >>> d = CurationDict()
        >>> d.fromUnicode(u'key:value')
        {u'key': [u'value']}
        >>> result = d.fromUnicode(u'key:value\\nkey2:type2\\nkey:value2')
        >>> result[u'key']
        [u'value', u'value2']
        >>> result[u'key2']
        [u'type2']
        """

        result = {}
        for i in u.splitlines():
            k, v = i.split(u':', 1)
            if k not in result:
                result[k] = []
            result[k].append(v)
        return result


class TextLineList(zope.schema.List):
    """\
    Workspace listing field.
    """

    zope.interface.implements(
        ITextLineList,
        zope.schema.interfaces.IFromUnicode,
    )
    value_type = zope.schema.TextLine(title=u'Values',),

    def fromUnicode(self, u):
        """\
        >>> d = TextLineList()
        >>> d.fromUnicode(u'')
        []
        >>> d.fromUnicode(u'test')
        [u'test']
        >>> d.fromUnicode(u'test\\ntest2')
        [u'test', u'test2']
        """

        return u.splitlines()
