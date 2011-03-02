from zope import interface
import zope.component
from zope.schema import fieldproperty

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.atct import ATFolder, ATBTreeFolder
from Products.ATContentTypes.atct import ATDocument
from Products.CMFCore.permissions import View

from pmr2.app.exposure.interfaces import *
from pmr2.app.exposure.atct import ATFolderDocument


class ExposureContainer(ATBTreeFolder):
    """\
    Container for exposures in PMR2.
    """

    interface.implements(IExposureContainer)
    security = ClassSecurityInfo()

    def __init__(self, oid='exposure', **kwargs):
        super(ExposureContainer, self).__init__(oid, **kwargs)


class Exposure(ATFolderDocument):
    """\
    PMR Exposure object is used to encapsulate a single version of any
    given workspace and will allow more clear presentation to users of
    the system.

    This is implemented as a folder to allow inclusion of different 
    types of data that may be generated as part of the exposure process,
    such as data plots for graphs, graphical representation of metadata
    or the generated diagrams of models, or even other types of data.

    Naturally, specific types of extended exposure data will need to
    have classes defined for them.
    """

    interface.implements(IExposure, IExposureFolder, IExposureObject)
    security = ClassSecurityInfo()
    # XXX the get_ methods are similar to IWorkspace.
    # best to define a common interface.

    workspace = fieldproperty.FieldProperty(IExposure['workspace'])
    commit_id = fieldproperty.FieldProperty(IExposure['commit_id'])
    curation = fieldproperty.FieldProperty(IExposure['curation'])
    docview_gensource = fieldproperty.FieldProperty(IExposure['docview_gensource'])
    docview_generator = fieldproperty.FieldProperty(IExposure['docview_generator'])


class ExposureFolder(ATFolderDocument):

    interface.implements(IExposureFolder, IExposureObject)
    docview_gensource = fieldproperty.FieldProperty(IExposureFolder['docview_gensource'])
    docview_generator = fieldproperty.FieldProperty(IExposureFolder['docview_generator'])


class ExposureFile(ATDocument):
    """\
    Generic object within an exposure that represents a file in the
    workspace, and as an anchor for adapted content.
    """

    interface.implements(
        IExposureObject,
        IExposureFile,
    )
    views = fieldproperty.FieldProperty(IExposureFile['views'])
    file_type = fieldproperty.FieldProperty(IExposureFile['file_type'])
    docview_gensource = fieldproperty.FieldProperty(IExposureFile['docview_gensource'])
    docview_generator = fieldproperty.FieldProperty(IExposureFile['docview_generator'])
    selected_view = fieldproperty.FieldProperty(IExposureFile['selected_view'])
    security = ClassSecurityInfo()

    security.declareProtected(View, 'raw_text')
    def raw_text(self):
        """\
        Fetches raw text of all notes that are annotate to this file.
        """

        results = []
        for view in self.views:
            ctxobj = zope.component.queryAdapter(self, name=view)
            if ctxobj is not None:
                results.append(ctxobj.raw_text())
        return '\n'.join(results)


class ExposureFileType(atapi.BaseContent):
    """\
    This allows types of file be defined for an ExposureFile.  This is
    basically a profile that for a file type that defines which views to
    generate and tags to attached to a file.
    """

    interface.implements(IExposureFileType)
    security = ClassSecurityInfo()

    title = fieldproperty.FieldProperty(IExposureFileType['title'])
    views = fieldproperty.FieldProperty(IExposureFileType['views'])
    select_view = fieldproperty.FieldProperty(IExposureFileType['select_view'])
    tags = fieldproperty.FieldProperty(IExposureFileType['tags'])


atapi.registerType(ExposureContainer, 'pmr2.app.exposure')
atapi.registerType(Exposure, 'pmr2.app.exposure')
atapi.registerType(ExposureFile, 'pmr2.app.exposure')
atapi.registerType(ExposureFileType, 'pmr2.app.exposure')
atapi.registerType(ExposureFolder, 'pmr2.app.exposure')
