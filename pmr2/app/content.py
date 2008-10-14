from zope import interface
from zope.schema.fieldproperty import FieldProperty

from plone.app.content import container

from pmr2.app.interfaces import *


class RepositoryRoot(container.Container):
    """\
    The repository root object.
    """

    interface.Implements(IRepositoryRoot)

    title = fieldproperty.FieldProperty(IRepositoryRoot.title)
    description = fieldproperty.FieldProperty(IRepositoryRoot.description)
    path = fieldproperty.FieldProperty(IRepositoryRoot.path)

