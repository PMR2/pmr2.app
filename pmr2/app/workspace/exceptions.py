class ProtocolError(Exception):
    """generic workspace protocol error"""


class NotProtocolRequestError(ProtocolError):
    """not a protocol request."""


class UnsupportedCommandError(ProtocolError):
    """unsupported protocol command"""


class UnknownStorageTypeError(ValueError):
    """unknown storage type error"""


class StorageArchiveError(ValueError):
    """Repository archive error."""


class PathInvalidError(ValueError):
    """path invalid"""


class PathNotDirError(PathInvalidError):
    """path not a directory"""


class PathNotFoundError(PathInvalidError):
    """path not found"""


class PathExistsError(PathInvalidError):
    """path exists"""


class SubrepoPathUnsupportedError(PathInvalidError):
    """unsupported subrepo path format"""


class RevisionNotFoundError(ValueError):
    """revision not found"""


class RepoEmptyError(ValueError):
    """repository empty"""


class RepoNotFoundError(ValueError):
    """repository not found"""
