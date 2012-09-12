import zope.component
import zope.schema

from z3c.form.converter import SequenceDataConverter, FormatterValidationError
from z3c.form.interfaces import IErrorViewSnippet

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
        except LookupError, err:
            # Swallow lookup errors and provide the value, even if the
            # option was changed.  The widget this converter is for can
            # handle additional missing values, but it still relies on
            # the parent method, and it does not trap any exceptions.
            # This means it is impossible for proper notifications to be
            # propagated forward.
            # 
            # Second point: the value passed into here is derived from
            # the context.  If this is converted into some token that
            # represents an invalid value, the update method of the
            # widget will then have to rely on a separate value field or
            # method to again derive the original value.
            # 
            # In the interest of not duplicating the entire update
            # method and keeping this simple, we just return the value
            # as is, and have the user of this method try to convert
            # this result back to the field value using the method below
            # as the validation.
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
