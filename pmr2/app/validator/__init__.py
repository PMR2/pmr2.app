import os.path

import zope.interface
import zope.component
from  zope.schema import ValidationError
import z3c.form.validator

from pmr2.app import interfaces
from pmr2.app.settings import IPMR2GlobalSettings


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
        u = zope.component.getUtility(IPMR2GlobalSettings)
        root = u.dirCreatedFor(self.context)
        if root is None:
            raise interfaces.WorkspaceDirNotExistsError()
        p = os.path.join(root, value)
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
