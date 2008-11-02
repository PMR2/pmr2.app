import zope.interface
from  zope.schema import ValidationError
import z3c.form.validator

from pmr2.app.interfaces import ObjectIdExistsError, IObjectIdMixin

class ObjectIdValidator(z3c.form.validator.SimpleFieldValidator):

    def validate(self, value):
        super(ObjectIdValidator, self).validate(value)
        if value in self.context:
            raise ObjectIdExistsError('object id `%s` already exists' % value)


z3c.form.validator.WidgetValidatorDiscriminators(
    ObjectIdValidator, 
    field=IObjectIdMixin['id'],
)
