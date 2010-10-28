import os.path

import zope.interface
import zope.component
from  zope.schema import ValidationError
import z3c.form.validator

from pmr2.app import interfaces

from pmr2.app.interfaces import exceptions
from pmr2.app.interfaces import IPMR2GlobalSettings
from pmr2.app.content.interfaces import IPMR2
from pmr2.app.browser.interfaces import IObjectIdMixin
from pmr2.app.workspace.interfaces import IWorkspaceStorageCreate


class ObjectIdValidator(z3c.form.validator.SimpleFieldValidator):

    def validate(self, value):
        super(ObjectIdValidator, self).validate(value)
        if value in self.context:
            raise exceptions.ObjectIdExistsError()

z3c.form.validator.WidgetValidatorDiscriminators(
    ObjectIdValidator, 
    field=IObjectIdMixin['id'],
)


class StorageExistsValidator(ObjectIdValidator):

    def validate(self, value):
        super(StorageExistsValidator, self).validate(value)
        # context assumed to be WorkspaceContainer
        u = zope.component.getUtility(IPMR2GlobalSettings)
        root = u.dirCreatedFor(self.context)
        if root is None:
            raise exceptions.WorkspaceDirNotExistsError()
        p = os.path.join(root, value)
        if os.path.exists(p):
            raise exceptions.StorageExistsError()

z3c.form.validator.WidgetValidatorDiscriminators(
    StorageExistsValidator, 
    field=IWorkspaceStorageCreate['id'],
)
