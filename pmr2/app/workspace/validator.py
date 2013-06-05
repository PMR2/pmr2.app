import os.path

import zope.component
import zope.interface
import z3c.form.validator

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.interfaces import exceptions
from pmr2.app.schema.validator import ObjectIdValidator
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


class StorageFileChoiceFieldValidator(z3c.form.validator.SimpleFieldValidator):

    def validate(self, value):
        """\
        We have to coerce the parent to validate against the correct set
        of values, which means getting the parent to bind the form
        rather than the context the field.  In the interests of reusing
        as much code as possible, we swap the context with the form for
        the scope of this method.
        """

        context = self.context
        self.context = self.view
        zope.interface.alsoProvides(self.view, self.field.interface)
        result = super(StorageFileChoiceFieldValidator, self).validate(value)
        self.context = context
        return result
