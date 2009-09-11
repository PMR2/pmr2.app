import zope.schema
import zope.interface
from plone.theme.interfaces import IDefaultPloneLayer
from plone.z3cform.interfaces import IFormWrapper

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")


class IUpdatablePageView(zope.interface.Interface):
    """\
    Interface for the Workspace action menu.
    """

    def update():
        """
        Method call to update the internal structure before the view
        is rendered.
        """


class IWorkspaceActionsViewlet(zope.interface.Interface):
    """\
    Interface for the Workspace action menu.
    """


class IWorkspaceFilePageView(IUpdatablePageView):
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


class IMathMLLayoutWrapper(IFormWrapper):
    """\
    Interface for the MathML layout wrapper.
    """
