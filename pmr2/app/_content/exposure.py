import os.path

from zope import interface
from zope.schema import fieldproperty

from Acquisition import aq_parent, aq_inner

from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder
from Products.ATContentTypes.content.document import ATDocument
from Products.Archetypes import atapi

import pmr2.mercurial
import pmr2.mercurial.utils

from pmr2.app.interfaces import *
from pmr2.app.mixin import TraversalCatchAll


class ExposureContainer(ATBTreeFolder):
    """\
    Container for exposures in PMR2.
    """

    interface.implements(IExposureContainer)

    def __init__(self, oid='exposure', **kwargs):
        super(ExposureContainer, self).__init__(oid, **kwargs)

    def get_path(self):
        # XXX quickie code
        #"""See IWorkspaceContainer"""

        p = aq_parent(aq_inner(self)).repo_root
        if not p:
            return None
        # XXX magic string
        return os.path.join(p, 'workspace')

atapi.registerType(ExposureContainer, 'pmr2.app')


class Exposure(ATFolder, TraversalCatchAll):
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

    interface.implements(IExposure)
    # XXX the get_ methods are similar to IWorkspace.
    # best to define a common interface.

    workspace = fieldproperty.FieldProperty(IExposure['workspace'])
    commit_id = fieldproperty.FieldProperty(IExposure['commit_id'])
    curation = fieldproperty.FieldProperty(IExposure['curation'])

    def __before_publishing_traverse__(self, ob, request):
        TraversalCatchAll.__before_publishing_traverse__(self, ob, request)
        ATFolder.__before_publishing_traverse__(self, ob, request)

    def get_path(self):
        """See IExposure"""

        # aq_inner needed to get out of form wrappers
        p = self.get_parent_container().get_path()  # XXX get_path = quickie
        if not p:
            return None
        return os.path.join(p, self.workspace)

    def get_log(self, rev=None, branch=None, shortlog=False, datefmt=None):
        """See IExposure"""

        # XXX valid datefmt values might need to be documented/checked
        storage = self.get_storage()
        return storage.log(rev, branch, shortlog, datefmt).next()

    def get_storage(self):
        """See IExposure"""

        path = self.get_path()
        return pmr2.mercurial.Storage(path)

    def get_manifest(self):
        storage = self.get_storage()
        return storage.raw_manifest(self.commit_id)

    def get_file(self, path):
        storage = self.get_storage()
        return storage.file(self.commit_id, path)

    def get_parent_container(self):
        """\
        returns the container object that stores this.
        """

        result = aq_parent(aq_inner(self))
        return result

    def get_pmr2_container(self):
        """\
        returns the root pmr2 object that stores this.
        """

        result = aq_parent(self.get_parent_container())
        return result

atapi.registerType(Exposure, 'pmr2.app')


class ExposureDocument(ATDocument, TraversalCatchAll):
    """\
    Documentation for an exposure.
    """

    interface.implements(IExposureDocument)

    origin = fieldproperty.FieldProperty(IExposureDocument['origin'])
    transform = fieldproperty.FieldProperty(IExposureDocument['transform'])

    def generate_content(self, data):
        pass

atapi.registerType(ExposureDocument, 'pmr2.app')


class ExposureMathDocument(ATDocument):
    """\
    Documentation for an exposure.
    """

    interface.implements(IExposureMathDocument)
    origin = fieldproperty.FieldProperty(IExposureMathDocument['origin'])
    transform = fieldproperty.FieldProperty(IExposureMathDocument['transform'])
    mathml = fieldproperty.FieldProperty(IExposureMathDocument['mathml'])

    def generate_content(self, data):
        pass

atapi.registerType(ExposureMathDocument, 'pmr2.app')
