import zope.schema
import zope.interface
import zope.publisher.interfaces
from plone.theme.interfaces import IDefaultPloneLayer
from plone.z3cform.interfaces import IFormWrapper

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from pmr2.app.schema import ObjectId

from pmr2.app.content.interfaces import IPMR2Search


class IThemeSpecific(IDefaultPloneLayer):
    """\
    Marker interface that defines a Zope 3 browser layer.
    """


class IPlainLayoutWrapper(IFormWrapper):
    """\
    Interface for the plain layout wrapper.
    """


class IPloneviewLayoutWrapper(IFormWrapper):
    """\
    Interface for the Ploneview layout wrapper.
    """


class IMathMLLayoutWrapper(IFormWrapper):
    """\
    Interface for the MathML layout wrapper.
    """


class IPublishTraverse(zope.publisher.interfaces.IPublishTraverse):
    """\
    Our specialized traversal class with specifics defined.
    """

    traverse_subpath = zope.schema.List(
        title=u'Traverse Subpath',
        description=u'A list of traversal subpaths that got captured.',
    )


class IPMR2Form(zope.interface.Interface):
    """\
    Interface for PMR2 forms.
    """

    disableAuthenticator = zope.schema.Bool(
        title=_('Disable Authenticator'),
        description=_('Disable CSRF protection authenticator.'),
        default=False,
        required=True,
    )

    def authenticate():
        """\
        Authenticate request.
        """


class IObjectIdMixin(zope.interface.Interface):
    """\
    Provides a generic id field attribute for use by AddForm.
    """

    id = ObjectId(
        title=u'Id',
        description=u'The identifier of the object, used for URI.',
    )


class IPMR2SearchAdd(IObjectIdMixin, IPMR2Search):
    """\
    Interface for the use by PMR2AddForm.
    """
