import zope.component
import zope.schema

from z3c.form.converter import SequenceDataConverter, FormatterValidationError

from pmr2.app.workspace.widgets.interfaces import IStorageFileSelectWidget
from pmr2.app.workspace.i18n import MessageFactory as _


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

    def toFieldValue(self, value):
        """\
        As the value could be set with an invalid value that can't be
        looked up, we have to catch that and raise a new exception that
        Field.extract can catch.
        """

        try:
            return super(StorageFileSequenceDataConverter, 
                self).toFieldValue(value)
        except LookupError, err:
            raise FormatterValidationError(_(
                "The selected path is invalid as it does not exist within "
                "this revision."), err)
