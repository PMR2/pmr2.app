from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.atct import ATFolderSchema, ATDocumentSchema
from Products.ATContentTypes.atct import ATFolder, ATDocument
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.interfaces import IATDocument, IATFolder

ATFolderDocumentSchema = ATFolderSchema.copy() + ATDocumentSchema.copy()
finalizeATCTSchema(ATFolderDocumentSchema)


class ATFolderDocument(ATFolder, ATDocument):
    """\
    A Folder that has can alsoo act like a document.  Doing this in
    Archetypes because we are current dependent on the defaults while
    inside Plone (i.e. the ones we just inherited).  So this is a copy
    pasta of sort.
    """

    # XXX For Exposure and ExposureFolders

    schema         =  ATFolderDocumentSchema

    portal_type    = 'PMR2 Exposure'
    archetype_name = 'PMR2 Exposure'
    _atct_newTypeFor = {'portal_type' : 'PMR2 Exposure', 'meta_type' : 'PMR2 Exposure'
}
    assocMimetypes = ()
    assocFileExt   = ()

    security       = ClassSecurityInfo()
