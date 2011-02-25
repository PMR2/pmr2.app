import zope.interface
import zope.schema


class IStorageProtocol(zope.interface.Interface):
    """\
    Utility to match an incoming request with specific protocol.

    Provides method to look for characteristics in a given HTTP request
    to trigger basic http authentication for protocol level access to 
    the request workspace.
    """
