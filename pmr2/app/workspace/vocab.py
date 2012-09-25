import zope.interface
import zope.component

from zope.schema.interfaces import IVocabulary, IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName

from pmr2.app.factory import vocab_factory

from pmr2.app.workspace.interfaces import IWorkspace, IWorkspaceListing
from pmr2.app.workspace.interfaces import IStorageUtility, IStorage
from pmr2.app.workspace.interfaces import ICurrentCommitIdProvider


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
        self.context = context
        wks = self.acquireWorkspace()
        self.storage = zope.component.getAdapter(wks, IStorage)

        commit_id = self.acquireCommitId()
        if commit_id:
            self.storage.checkout(commit_id)

        values = self.storage.files()
        values.sort()

        terms = [SimpleTerm(i, i) for i in values]
        super(ManifestListVocab, self).__init__(terms)

    def acquireCommitId(self):
        if ICurrentCommitIdProvider.providedBy(self.context):
            return self.context.current_commit_id()
        id_provider = zope.component.queryAdapter(
            self.context, ICurrentCommitIdProvider)
        return id_provider and id_provider.current_commit_id()

    def acquireWorkspace(self):
        if not IWorkspace.providedBy(self.context):
            wks = None
            obj = aq_inner(self.context)
            while obj and not wks and not IWorkspace.providedBy(obj):
                wks = zope.component.queryAdapter(obj, IWorkspace)
                if not wks:
                    # The object that can adapted to the workspace can
                    # be nested, i.e. a form adapter object.
                    obj = aq_parent(obj)
                    if IWorkspace.providedBy(obj):
                        # We actually have one.
                        wks = obj
            if not wks:
                raise Exception("Unable to adapt to a workspace; will not be "
                                "able to acquire file listing.")
        else:
            wks = self.context

        return wks

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
