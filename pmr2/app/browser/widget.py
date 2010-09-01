import zope.component
import zope.interface
import zope.schema.interfaces

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

import z3c.form.interfaces
from z3c.form.browser import textarea
import z3c.form.widget
from z3c.form.widget import FieldWidget

from pmr2.app.workspace.table import WorkspaceStatusTable

__all__ = [
    'WorkspaceListingWidget',
    'WorkspaceListingWidgetFactory',
    'TextAreaWidget',
    'TextAreaWidgetFactory',
    'ExposureFileAnnotationWidget',
    'ExposureFileAnnotationWidgetFactory',
]


class WorkspaceListingWidget(z3c.form.widget.Widget):
    """\
    Widget that will render a table of workspace statuses.
    """

    def update(self):
        super(WorkspaceListingWidget, self).update()
        self.table = WorkspaceStatusTable(self.value, self.request)
        self.table.update()

    def render(self):
        return self.table.render()


@zope.component.adapter(zope.schema.interfaces.IField,
        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def WorkspaceListingWidgetFactory(field, request):
    """IFieldWidget factory for the above TextWidget."""
    return FieldWidget(field, WorkspaceListingWidget(request))


class TextAreaWidget(textarea.TextAreaWidget):
    """Customize the rows/cols to something usable."""
    cols = 60
    rows = 15


@zope.component.adapter(zope.schema.interfaces.IField,
        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def TextAreaWidgetFactory(field, request):
    """IFieldWidget factory for the above TextWidget."""
    return FieldWidget(field, TextAreaWidget(request))


class CurationWidget(TextAreaWidget):
    """Customize the rows/cols to something usable."""


@zope.component.adapter(zope.schema.interfaces.IField,
        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def CurationWidgetFactory(field, request):
    """IFieldWidget factory for the above TextWidget."""
    return FieldWidget(field, CurationWidget(request))


class TextLineListTextAreaWidget(TextAreaWidget):
    """Customize the rows/cols to something usable."""

@zope.component.adapter(zope.schema.interfaces.IField,
        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def TextLineListTextAreaWidgetFactory(field, request):
    """IFieldWidget factory for the above TextWidget."""
    return FieldWidget(field, TextLineListTextAreaWidget(request))
