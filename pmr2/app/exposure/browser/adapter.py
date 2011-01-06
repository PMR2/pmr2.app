import zope.interface
import zope.schema
from zope.location import Location, locate

from pmr2.app.exposure.browser.interfaces import IExposureFileSelectView


class ExposureFileSelectView(Location):

    zope.interface.implements(IExposureFileSelectView)
    selected_view = zope.schema.fieldproperty.FieldProperty(
        IExposureFileSelectView['selected_view'])
    views = zope.schema.fieldproperty.FieldProperty(
        IExposureFileSelectView['views'])

    def __init__(self, context):
        # must locate itself into context the very first thing, as the
        # vocabulary uses source adapter registered above.
        locate(self, context, '')
        # have to assign the views
        self.views = context.views
        # before we can try to assign the selected views do to usage of
        # constrained vocabulary.
        try:
            self.selected_view = context.selected_view
        except:
            pass
