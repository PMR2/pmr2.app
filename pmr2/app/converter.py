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
