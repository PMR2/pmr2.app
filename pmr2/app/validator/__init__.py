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


class StorageExistsValidator(ObjectIdValidator):

    def validate(self, value):
        super(StorageExistsValidator, self).validate(value)
        # context assumed to be WorkspaceContainer
        p = os.path.join(self.context.get_path(), value)
        if os.path.exists(p):
            raise interfaces.StorageExistsError()

z3c.form.validator.WidgetValidatorDiscriminators(
    StorageExistsValidator, 
    field=interfaces.IWorkspaceStorageCreate['id'],
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
