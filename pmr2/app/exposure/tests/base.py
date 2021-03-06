from os.path import dirname
from os.path import join

import zope.component
from zope.component import testing
from zope.traversing.interfaces import BeforeTraverseEvent
from plone.browserlayer.layer import mark_layer

from Testing import ZopeTestCase as ztc
from Zope2.App import zcml
from Products.CMFCore.utils import getToolByName
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.layer import onteardown

from pmr2.app.workspace.interfaces import IStorageUtility
from pmr2.app.workspace.content import Workspace

import pmr2.testing
from pmr2.testing import utils
from pmr2.app.workspace.tests.base import WorkspaceDocTestCase


@onsetup
def setup():
    import pmr2.app
    import pmr2.app.annotation.tests
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', pmr2.app)
    zcml.load_config('test.zcml', pmr2.app.annotation.tests)
    zcml.load_config('test.zcml', pmr2.app.exposure.tests)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.app')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.app',))

def mkdummywks(portal, name):
    w = Workspace(name)
    w.storage = 'dummy_storage'
    portal.workspace[name] = w


class ExposureUnitTestCase(WorkspaceDocTestCase):
    # XXX should really inherit from WorspaceUnitTest case, but that
    # doesn't exist since they are the same.

    def setUp(self):
        """\
        Sets up the environment that the exposure unit testing needs.
        """

        super(ExposureUnitTestCase, self).setUp()

        self.pmr2.default_exposure_idgen = 'rand128hex'
        self.pmr2.repo_root = self.tmpdir

        from pmr2.app.workspace.content import WorkspaceContainer, Workspace

        self.portal['workspace'] = WorkspaceContainer()

        mkdummywks(self.portal, 'test')
        mkdummywks(self.portal, 'cake')

        # unassigned
        self.portal.workspace['blank'] = Workspace('blank')

        # legacy test case.
        self.portal.workspace['eggs'] = Workspace('eggs')
        utils.mkreporoot(self.pmr2.createDir(self.portal))
        utils.mkrepo(self.pmr2.dirOf(self.portal.workspace.eggs))


class ExposureDocTestCase(ExposureUnitTestCase):

    def setUp(self):
        """\
        Sets up the environment that the exposure doctest needs.
        """

        super(ExposureDocTestCase, self).setUp()

        from pmr2.app.exposure.content import ExposureContainer
        from pmr2.app.exposure.content import ExposureFileType

        self.portal['exposure'] = ExposureContainer('exposure')

        self.portal['test_type'] = ExposureFileType('test_type')
        self.portal.test_type.title = u'Test Type'
        self.portal.test_type.views = [
            u'edited_note', u'post_edited_note', u'rot13']
        self.portal.test_type.tags = [u'please_ignore']
        self._publishContent(self.portal.test_type)

        # Filename related testing.
        self.portal['docgen_type'] = ExposureFileType('docgen_type')
        self.portal.docgen_type.title = u'Docgen Type'
        self.portal.docgen_type.views = [u'docgen', u'filename_note']
        self.portal.docgen_type.tags = []
        self._publishContent(self.portal.docgen_type)


class ExposureExtendedDocTestCase(ExposureDocTestCase):
    """
    Uses the data that was originally done for pmr2.mercurial without
    using that.
    """

    def setUp(self):
        super(ExposureExtendedDocTestCase, self).setUp()
        targets = ('pmr2hgtest', 'rdfmodel',)
        su = zope.component.getUtility(IStorageUtility, name='dummy_storage')
        for t in targets:
            su._loadDir(t, join(dirname(__file__), 'data', t))
            mkdummywks(self.portal, t)


class CompleteDocTestCase(ExposureDocTestCase):

    def setUp(self):
        """\
        Completes the other data within the portal so that other test
        classes don't have to set up Exposure objects and friends.
        """

        super(CompleteDocTestCase, self).setUp()

        self._mkexposure(u'/plone/workspace/test', u'2', '1')
        self._mkexposure(u'/plone/workspace/eggs', u'1', '2')

    def _mkexposure(self, workspace, commit_id, id_):
        from pmr2.app.settings.interfaces import IPMR2GlobalSettings
        from pmr2.app.workspace.content import Workspace
        from pmr2.app.exposure.content import ExposureContainer, Exposure
        from pmr2.idgen.interfaces import IIdGenerator

        settings = zope.component.queryUtility(IPMR2GlobalSettings)
        idgen = zope.component.queryUtility(IIdGenerator,
            name=settings.default_exposure_idgen)
        if not id_:
            id_ = idgen.next()
        else:
            # call it anyway.
            idgen.next()
        e = Exposure(id_)
        e.workspace = workspace
        e.commit_id = commit_id
        self.portal.exposure[id_] = e
        self.portal.exposure[id_].reindexObject()

    def markLayer(self):
        # Helper method to trigger the mark layer event.
        event = BeforeTraverseEvent(self.portal, self.portal.REQUEST)
        mark_layer(self.portal, event)
