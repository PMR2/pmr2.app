import z3c.form.validator

from pmr2.app import interfaces

from pmr2.app.interfaces import exceptions
from pmr2.app.browser.interfaces import IObjectIdMixin


class ObjectIdValidator(z3c.form.validator.SimpleFieldValidator):

    def validate(self, value):
        super(ObjectIdValidator, self).validate(value)
        if value in self.context:
            raise exceptions.ObjectIdExistsError()

z3c.form.validator.WidgetValidatorDiscriminators(
    ObjectIdValidator, 
    field=IObjectIdMixin['id'],
)
