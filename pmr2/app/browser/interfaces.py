import zope.schema
import zope.interface
import zope.publisher.interfaces
from plone.theme.interfaces import IDefaultPloneLayer

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from pmr2.app.schema import ObjectId

try:
    from pmr2.z3cform.interfaces import IPublishTraverse
    zope.deprecation.deprecated('IPublishTraverse', 
        'IPublishTraverse has been moved to pmr2.z3cform.interfaces.  '
        'Please update the import location before pmr2.app-0.7')
except ImportError:
    pass


class IThemeSpecific(IDefaultPloneLayer):
    """\
    Marker interface that defines a Zope 3 browser layer.
    """


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
