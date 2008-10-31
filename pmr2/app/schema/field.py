import re

import zope.interface
import zope.schema

from pmr2.app.schema.interfaces import InvalidObjectId
from pmr2.app.schema.interfaces import IObjectId


_isobjectid = re.compile(r'^[a-zA-Z][a-zA-Z0-9_\.]*$').match

class ObjectId(zope.schema.BytesLine):
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
