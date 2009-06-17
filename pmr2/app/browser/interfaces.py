import zope.schema
import zope.interface
from plone.theme.interfaces import IDefaultPloneLayer
from plone.z3cform.interfaces import IFormWrapper

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")


class IWorkspaceActionsViewlet(zope.interface.Interface):
    """\
    Interface for the Workspace action menu.
    """


class IWorkspaceFilePageView(zope.interface.Interface):
    """\
    Interface for the Workspace action menu.
    """


class IThemeSpecific(IDefaultPloneLayer):
    """\
    Marker interface that defines a Zope 3 browser layer.
    """


class IPlainLayoutWrapper(IFormWrapper):
    """\
    Interface for the plain layout wrapper.
    """
