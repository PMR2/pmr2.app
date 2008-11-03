import os.path

import zope.interface
from  zope.schema import ValidationError
import z3c.form.validator

from pmr2.app import interfaces


class ObjectIdValidator(z3c.form.validator.SimpleFieldValidator):

    def validate(self, value):
        super(ObjectIdValidator, self).validate(value)
        if value in self.context:
            raise interfaces.ObjectIdExistsError()

z3c.form.validator.WidgetValidatorDiscriminators(
    ObjectIdValidator, 
    field=interfaces.IObjectIdMixin['id'],
)


class RepoPathValidator(z3c.form.validator.SimpleFieldValidator):

    def validate(self, value):
        super(RepoPathValidator, self).validate(value)
        if not os.path.exists(value):
            raise interfaces.InvalidPathError()

z3c.form.validator.WidgetValidatorDiscriminators(
    RepoPathValidator, 
    field=interfaces.IPMR2['repo_root'],
)
