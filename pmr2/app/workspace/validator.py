import os.path

import zope.component
import z3c.form.validator

from pmr2.app.interfaces import exceptions
from pmr2.app.interfaces import IPMR2GlobalSettings
from pmr2.app.validator import ObjectIdValidator
from pmr2.app.workspace.browser.interfaces import IWorkspaceStorageCreate

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
