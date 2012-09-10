import zope.component
import zope.schema

from z3c.form.converter import SequenceDataConverter

from pmr2.app.workspace.widgets.interfaces import IStorageFileSelectWidget


class StorageFileSequenceDataConverter(SequenceDataConverter):
    """Converter between storage file and its widget
    
    This converter will permit missing values.
    """

    zope.component.adapts(
        zope.schema.interfaces.IField, IStorageFileSelectWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return []
        widget = self.widget
        terms = widget.updateTerms()
        try:
            return [terms.getTerm(value).token]
        except LookupError:
            # Swallow lookup errors and we provide the original value
            # XXX make this an error in the final rendering, somehow?
            return [value]
