import zope.interface
import zope.component

from zope.schema.interfaces import IVocabulary, IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName

from pmr2.app.vocab import vocab_factory

from pmr2.app.interfaces import *
from pmr2.app.workspace.interfaces import IWorkspaceListing



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
        obj = context

        helper = zope.component.queryAdapter(obj, IExposureSourceAdapter)
        if not helper:
            raise TypeError('could not acquire source from context')
        obj, wks, path = helper.source()

        # XXX could just adapt wks to the storage adapter from here
        storage = zope.component.getMultiAdapter(
            (obj,),
            name='PMR2ExposureStorageAdapter',
        )

        manifest = storage.raw_manifest()
        values = manifest.keys()
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
