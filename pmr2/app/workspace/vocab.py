import zope.interface
import zope.component

from zope.schema.interfaces import IVocabulary, IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName

from pmr2.app.vocab import vocab_factory

from pmr2.app.interfaces import *
from pmr2.app.workspace.interfaces import IWorkspace
from pmr2.app.workspace.interfaces import IWorkspaceListing
from pmr2.app.workspace.interfaces import IStorageUtility
from pmr2.app.workspace.interfaces import IStorage


class WorkspaceDirObjListVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        listing = zope.component.getAdapter(context, IWorkspaceListing)
        values = listing()
        terms = [SimpleTerm(i, i[0]) for i in values]
        super(WorkspaceDirObjListVocab, self).__init__(terms)

WorkspaceDirObjListVocabFactory = vocab_factory(WorkspaceDirObjListVocab)


class ManifestListVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = wks = context

        # XXX this part need to be subclassed away into exposure module
        if not IWorkspace.providedBy(self.context):
            helper = zope.component.queryAdapter(self.context, 
                IExposureSourceAdapter)
            if not helper:
                raise TypeError('could not acquire source from context')
            obj, wks, path = helper.source()

        self.storage = zope.component.getAdapter(wks, IStorage)
        values = self.storage.files()
        values.sort()

        terms = [SimpleTerm(i, i) for i in values]
        super(ManifestListVocab, self).__init__(terms)

    def getTerm(self, value):
        if value is None:
            # unspecified, let this slide...
            return SimpleTerm(value)
        else:
            return super(ManifestListVocab, self).getTerm(value)

ManifestListVocabFactory = vocab_factory(ManifestListVocab)


class StorageVocab(SimpleVocabulary):

    zope.interface.implements(IVocabulary)

    _missing = ' (not found)'

    def __init__(self, context=None):

        self.context = context
        terms = self._buildTerms()
        super(StorageVocab, self).__init__(terms)

    def _getValues(self):
        return [(i[0], i[0], i[1].title) for i in 
                zope.component.getUtilitiesFor(IStorageUtility)]

    def _buildTerms(self):
        # sort by title
        values = self._getValues()
        values.sort(cmp=lambda x, y: cmp(x[2], y[2]))
        terms = [SimpleTerm(*i) for i in values]
        return terms

    def getTerm(self, value):
        try:
            return super(StorageVocab, self).getTerm(value)
        except LookupError:
            pass
        # no utility is found
        # XXX implement null utility maybe?  try some test cases first.
        return SimpleTerm(None, None, value + self._missing)

StorageVocabFactory = vocab_factory(StorageVocab)
