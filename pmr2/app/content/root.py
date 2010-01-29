from zope import interface
from zope.schema import fieldproperty
from zope.component import queryAdapter

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes import atapi

from pmr2.app.content.interfaces import *
from pmr2.app.mixin import TraversalCatchAll


class PMR2(ATFolder, TraversalCatchAll):
    """\
    The repository root object.
    """

    interface.implements(IPMR2)

    # title is defined by ATFolder
    repo_root = fieldproperty.FieldProperty(IPMR2['repo_root'])

    def __before_publishing_traverse__(self, ob, request):
        """
        This is needed here for redirection purposes.
        """

        # check whether we have an import map, only do stuff if we have
        # one.
        o = queryAdapter(self, name='PMRImportMap')
        if o is not None:
            TraversalCatchAll.__before_publishing_traverse__(
                self, ob, request, '@@root_folder_listing')
        ATFolder.__before_publishing_traverse__(self, ob, request)

atapi.registerType(PMR2, 'pmr2.app')
