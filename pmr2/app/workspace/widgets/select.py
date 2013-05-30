import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from zope.i18n import translate

from z3c.form.interfaces import IFormLayer, IFieldWidget, IDataConverter
from z3c.form.interfaces import IErrorViewSnippet, NO_VALUE 
from z3c.form.converter import FormatterValidationError
from z3c.form.browser import select
from z3c.form.widget import FieldWidget

from pmr2.app.workspace.schema.interfaces import IStorageFileChoice
from pmr2.app.workspace.i18n import MessageFactory as _
from pmr2.app.workspace.widgets.interfaces import IStorageFileSelectWidget

INVALID_VALUE = '--INVALID--'


class StorageFileSelectWidget(select.SelectWidget):
    zope.interface.implementsOnly(IStorageFileSelectWidget)

    klass = u'storagefileselect-widget'
    invalidSelection = False

    parent_items = select.SelectWidget.items

    @property
    def items(self):
        if self.terms is None:  # update() has not been called yet
            return ()

        items = []
        tokens = [term.token for term in self.terms]
        for value in self.value:
            if value != self.noValueToken and value not in tokens:
                items.append({
                    'id': self.id + '-invalid',
                    'value': INVALID_VALUE,
                    'content': value,
                    'selected': 1,
                })
                self.invalidSelection = True

        items.extend(self.parent_items())
        return items

    def update(self):
        """\
        Customized update method.
        """

        # Since we are interested in acquring what the context had first
        # before we are interested in what was submitted in the request,
        # we forcibly set ignoreRequest on and continue as normal.  Once
        # that is done, process the request as normal.

        ignoreRequest = self.ignoreRequest
        self.ignoreRequest = True
        super(StorageFileSelectWidget, self).update()
        # Restore original value.
        self.ignoreRequest = ignoreRequest

        if not ignoreRequest:
            # Extract the request value like how the parent would have 
            # done
            widget_value = self.extract()

            if widget_value not in (NO_VALUE, INVALID_VALUE):
                # Only set the widget with the value from request that
                # is valid
                self.value = widget_value
                # As this deferred self.value assignment from request
                # is complete, with everything else done, return here.
                return

        # The follow are steps that should also have been done inside
        # step 1.2 in that method.  To begin validate that the
        # applicable conditions are available.
        if not IFieldWidget.providedBy(self):
            return

        # Always set errors, since context could provide an invalid
        # value due to changing conditions.
        self.setErrors = True

        # Now verify that the current widget value (which is extracted
        # by the data manager) is valid, attempt the conversion back to
        # the field value using toFieldValue as the reverse method
        # toWidgetValue does not and cannot raise exceptions due to
        # how and where it is used by the parent update method.

        converter = IDataConverter(self)
        try:
            converter.toFieldValue(self.value)
        except (zope.interface.Invalid, ValueError), error:
            # We have an exception, so we adapt and set the error view.
            view = zope.component.getMultiAdapter(
                (error, self.request, self, self.field,
                 self.form, self.context), IErrorViewSnippet)
            view.update()
            self.error = view

    def extract(self, default=NO_VALUE):
        # In the parent method, both legitimate missing value or values
        # that raise LookupError return the same default value, which
        # should be differentiated.  This is the extraction method that
        # will be used by the customized updated method, but first make
        # use of the default one provided by parent but pass along a
        # modified default value.
        value = super(StorageFileSelectWidget, self).extract(INVALID_VALUE)

        if value == []:
            # First possible result is an unspecified value - simply 
            # return that as it is valid.
            return value

        # Now manually verify that request is specified, if so we just
        # return the default value (which should be NO_VALUE if used
        # internally, and will be expected).
        request_value = self.request.get(self.name, default)
        if request_value == default:
            return default

        # We can now return the extracted value as is, and any result
        # of INVALID_VALUE will be handled there.
        return value


@zope.component.adapter(IStorageFileChoice, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def StorageFileChoiceWidgetDispatcher(field, request):
    return zope.component.getMultiAdapter((field, field.vocabulary, request),
                                          IFieldWidget)


@zope.component.adapter(IStorageFileChoice,
                        zope.interface.Interface,
                        IFormLayer)
@zope.interface.implementer(IFieldWidget)
def StorageFileSelectFieldWidget(field, source, request=None):
    return FieldWidget(field, StorageFileSelectWidget(request))


# multi select widget not implemented, yet.
# 
# @zope.component.adapter(
#     zope.schema.interfaces.IUnorderedCollection, IFormLayer)
# @zope.interface.implementer(IFieldWidget)
# def CollectionSelectFieldWidget(field, request):
#     """IFieldWidget factory for SelectWidget."""
#     widget = zope.component.getMultiAdapter((field, field.value_type, request),
#         IFieldWidget)
#     widget.size = 5
#     widget.multiple = 'multiple'
#     return widget
#
#
# @zope.component.adapter(
#     zope.schema.interfaces.IUnorderedCollection,
#     IStorageFileChoice, IFormLayer)
# @zope.interface.implementer(IFieldWidget)
# def CollectionChoiceSelectFieldWidget(field, value_type, request):
#     """IFieldWidget factory for SelectWidget."""
#     return SelectFieldWidget(field, None, request)
