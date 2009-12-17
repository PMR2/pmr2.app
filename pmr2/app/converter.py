import zope.schema
import zope.schema.interfaces
import z3c.form.converter
import z3c.form.interfaces

from pmr2.app.schema import interfaces


class AccessorCallConverter(z3c.form.converter.BaseDataConverter):
    """\
    Calls an accessor as a method to get the data within.
    """

    # XXX the accessor classes in zope.schema doesn't have any 
    # associated interface, so all interfaces that are meant to be used
    # in conjunction with them must be listed here.
    zope.component.adapts(
        interfaces.IWorkspaceList, z3c.form.interfaces.IWidget
    )

    def toFieldValue(self, value):
        # no reverse process
        return None

    def toWidgetValue(self, value):
        if not value:
            return None
        # XXX error checking
        # make sure this is callable.
        return value()


class CurationTextAreaConverter(z3c.form.converter.BaseDataConverter):
    """\
    Calls an accessor as a method to get the data within.
    """
    zope.component.adapts(
        interfaces.ICurationDict, z3c.form.interfaces.ITextAreaWidget
    )

    def toWidgetValue(self, value):
        """\
        >>> import pmr2.app.schema
        >>> f = pmr2.app.schema.CurationDict()
        >>> # no need to test widget here
        >>> c = CurationTextAreaConverter(f, None)  
        >>> c.toWidgetValue(None)
        u''
        >>> c.toWidgetValue({})
        u''
        >>> c.toWidgetValue({u'key': [u'value']})
        u'key:value'
        >>> c.toWidgetValue({u'key': [u'value', u'value2']})
        u'key:value\\nkey:value2'
        >>> c.toWidgetValue({u'key': [u'value', u'value2'],
        ...                  u'xyz': [u'1.2.3']})
        u'key:value\\nkey:value2\\nxyz:1.2.3'
        >>> c.toWidgetValue({u'middle': [u'zxy', u'abc'],
        ...                  u'bottom': [u'hello'],
        ...                  u'top': [u'goodbye']})
        u'bottom:hello\\nmiddle:abc\\nmiddle:zxy\\ntop:goodbye'
        """

        if not value:
            return u''

        result = []
        for k, v in value.iteritems():
            for i in v:
                result.append('%s:%s' % (k, i))
        result.sort()
        return u'\n'.join(result)


class TextLineListTextAreaConverter(z3c.form.converter.BaseDataConverter):
    """\
    Calls an accessor as a method to get the data within.
    """
    zope.component.adapts(
        interfaces.ITextLineList, z3c.form.interfaces.ITextAreaWidget
    )

    def toWidgetValue(self, value):
        """\
        >>> f = zope.schema.List()
        >>> # no need to test widget here
        >>> c = TextLineListTextAreaConverter(f, None)  
        >>> c.toWidgetValue(None)
        u''
        >>> c.toWidgetValue([])
        u''
        >>> c.toWidgetValue([u'test', u'test2'])
        u'test\\ntest2'
        """

        if not value:
            return u''
        return u'\n'.join(value)
