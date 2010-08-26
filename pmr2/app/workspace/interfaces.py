import zope.interface
import zope.schema


class IWorkspaceListing(zope.interface.Interface):
    """\
    Returns a list of workspaces.
    """
