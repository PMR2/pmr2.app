import zope.schema

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

# General exceptions.

class PathLookupError(LookupError):
    """cannot calculate the path to some resource.."""


# Validation errors


class ObjectIdExistsError(zope.schema.ValidationError):
    __doc__ = _("""The specified id is already in use.""")


class StorageExistsError(zope.schema.ValidationError):
    __doc__ = _("""A previous workspace may have used this id but is not fully removed from the system.  Please use another id.""")


class InvalidPathError(zope.schema.ValidationError):
    __doc__ = _("""The value specified is not a valid path.""")


class RepoRootNotExistsError(zope.schema.ValidationError):
    __doc__ = _("""The repository root at the specified path does not exist.""")


class RepoNotExistsError(zope.schema.ValidationError):
    __doc__ = _("""The repository at the specified path does not exist.""")


class RepoPathUndefinedError(zope.schema.ValidationError):
    __doc__ = _("""The repository path is undefined.""")


class WorkspaceDirNotExistsError(zope.schema.ValidationError):
    __doc__ = _("""The workspace directory does not exist.""")


class WorkspaceObjNotFoundError(zope.schema.ValidationError):
    __doc__ = _("""The workspace object is not found.""")


class ExposureContainerInaccessibleError(zope.schema.ValidationError):
    __doc__ = _("""The exposure container cannot be accessed.""")


class ExposureInaccessibleError(zope.schema.ValidationError):
    __doc__ = _("""The exposure cannot be accessed.""")


class ExposureIdGeneratorMissingError(zope.schema.ValidationError):
    __doc__ = _("""The exposure id generator is missing.""")
