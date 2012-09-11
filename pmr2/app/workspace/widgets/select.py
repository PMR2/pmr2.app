import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from zope.i18n import translate

from z3c.form.interfaces import IFormLayer, IFieldWidget, NO_VALUE
from z3c.form.browser import select
from z3c.form.widget import FieldWidget

from pmr2.app.workspace.schema.interfaces import IStorageFileChoice
from pmr2.app.workspace.i18n import MessageFactory as _
from pmr2.app.workspace.widgets.interfaces import IStorageFileSelectWidget

INVALID_VALUE = '--INVALID--'


class StorageFileSelectWidget(select.SelectWidget):
    zope.interface.implementsOnly(IStorageFileSelectWidget)

    klass = u'storagefileselect-widget'

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
                    'value': value,
                    'content': value,
                    'selected': 1,
                })
        items.extend(self.parent_items)
        return items

    def extract(self, default=NO_VALUE):
        """See z3c.form.interfaces.IWidget."""
        if (self.name not in self.request and
            self.name+'-empty-marker' in self.request):
            return []
        value = self.request.get(self.name, default)
        if value != default:
            if not isinstance(value, (tuple, list)):
                value = (value,)
            # do some kind of validation, at least only use existing values
            for token in value:
                if token == self.noValueToken:
                    continue
                try:
                    self.terms.getTermByToken(token)
                except LookupError:
                    # Ideally we only do this when this is equal to a
                    # valid invalid value, which is an invalid value
                    # that was already assigned to the context and not
                    # one randomly submitted by the user through form
                    # manipulation.  However the latter is generally
                    # malicious and seeing that the error handling will
                    # catch that value in the exact same way, we can let
                    # this particular instance slide, but at the cost of
                    # not displaying the correct wrong value (that is of
                    # the context as now extract provides one).  To
                    # fully rectify this will require rewriting the
                    # entire update method, which is something that
                    # should be avoided.  There may be alternative ways
                    # to achieve this.
                    return value
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


# multi select widget not implemented
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
