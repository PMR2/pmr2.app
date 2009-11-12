import zope.interface
from zope.interface import alsoProvides
from zope.component import getUtilitiesFor, queryMultiAdapter

from zope.schema.interfaces import IVocabulary, IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName

from pmr2.app.interfaces import *


def vocab_factory(vocab):
    def _vocab_factory(context):
        return vocab(context)
    alsoProvides(_vocab_factory, IVocabularyFactory)
    return _vocab_factory


class WorkspaceDirObjListVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        values = self.context.get_repository_list()
        terms = [SimpleTerm(i, i[0]) for i in values]
        super(WorkspaceDirObjListVocab, self).__init__(terms)

WorkspaceDirObjListVocabFactory = vocab_factory(WorkspaceDirObjListVocab)


class ManifestListVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context

        storage = queryMultiAdapter(
            (context,),
            name='PMR2ExposureStorageAdapter',
        )

        manifest = storage.raw_manifest()
        values = manifest.keys()
        values.sort()
        terms = [SimpleTerm(i, i) for i in values]
        super(ManifestListVocab, self).__init__(terms)

ManifestListVocabFactory = vocab_factory(ManifestListVocab)


class PMR2TransformsVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        pt = getToolByName(context, 'portal_transforms')
        transforms = [(i, getattr(pt, i).get_documentation().strip()) \
                for i in pt.objectIds() if i.startswith('pmr2_processor_')]
        transforms.sort()
        terms = [SimpleTerm(*i) for i in transforms]
        super(PMR2TransformsVocab, self).__init__(terms)

PMR2TransformsVocabFactory = vocab_factory(PMR2TransformsVocab)


class PMR2IndexesVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        self.pt = None
        try:
            # If the context passed into here is unbounded, it won't have
            # a catalog to valudate against.
            self.pt = getToolByName(context, 'portal_catalog')
            values = self.pt.indexes()
        except:
            values = []
        terms = [SimpleTerm(i) for i in values if i.startswith('pmr2_')]
        super(PMR2IndexesVocab, self).__init__(terms)

    def getTerm(self, value):
        if self.pt is None:
            # no portal tool, see __init__
            return SimpleTerm(value)
        else:
            return super(PMR2IndexesVocab, self).getTerm(value)

    def __contains__(self, terms):
        if self.pt is None:
            # no portal tool, see __init__
            return True
        else:
            return super(PMR2IndexesVocab, self).__contains__(terms)

PMR2IndexesVocabFactory = vocab_factory(PMR2IndexesVocab)


class PMR2ExposureDocumentFactoryVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        values = [(i[0], i[1].description) for i in 
                  getUtilitiesFor(IExposureDocumentFactory)]
        # sort by description
        values.sort(cmp=lambda x, y: cmp(x[1], y[1]))
        terms = [SimpleTerm(*i) for i in values]
        super(PMR2ExposureDocumentFactoryVocab, self).__init__(terms)

PMR2ExposureDocumentFactoryVocabFactory = \
    vocab_factory(PMR2ExposureDocumentFactoryVocab)


class PMR2ExposureMetadocFactoryVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        values = [(i[0], i[1].description) for i in 
                  getUtilitiesFor(IExposureMetadocFactory)]
        # sort by description
        values.sort(cmp=lambda x, y: cmp(x[1], y[1]))
        terms = [SimpleTerm(*i) for i in values]
        super(PMR2ExposureMetadocFactoryVocab, self).__init__(terms)

PMR2ExposureMetadocFactoryVocabFactory = \
    vocab_factory(PMR2ExposureMetadocFactoryVocab)


class ExposureFileAnnotatorVocab(SimpleVocabulary):

    zope.interface.implements(IVocabulary)

    def __init__(self, context=None):
        """\
        This can be registered without a context since the utilities are
        generally not inserted during runtime (thus no need to 
        regenerate this list all the time).
        """

        self.context = context
        terms = self._buildTerms()
        super(ExposureFileAnnotatorVocab, self).__init__(terms)

    def _getValues(self):
        return [(i[0], i[0], i[1].title) for i in 
                getUtilitiesFor(IExposureFileAnnotator)]

    def _buildTerms(self):
        # sort by title
        values = self._getValues()
        values.sort(cmp=lambda x, y: cmp(x[2], y[2]))
        terms = [SimpleTerm(*i) for i in values]
        return terms

    def getTerm(self, value):
        """
        As this vocabulary will be used for querying the title of
        """

        try:
            return super(ExposureFileAnnotatorVocab, self).getTerm(value)
        except LookupError:
            # XXX a little trickery here.
            # this *might* be the default singleton instance; if that's
            # the case then self.context must be None, and it may not
            # contain all possible terms.
            # this vocab should have been initalized at the right place
            # such that this special treatment is not needed
            # doing it only on failure because this isn't normally used
            # to generate a list.
            if self.context is None:
                values = self._getValues()
                if len(self) != len(values):
                    # so we are not offering the full list here, reinitialize
                    self.__init__(self.context)
                    # try this again.
                    try:
                        return super(ExposureFileAnnotatorVocab,
                            self).getTerm(value)
                    except LookupError:
                        pass
        # default option.
        return SimpleTerm(value, value, value)

ExposureFileAnnotatorVocabFactory = vocab_factory(ExposureFileAnnotatorVocab)


class DocViewGenVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        values = [(i[0], i[0], i[1].title) for i in 
                  getUtilitiesFor(IDocViewGen)]
        # sort by title
        values.sort(cmp=lambda x, y: cmp(x[2], y[2]))
        terms = [SimpleTerm(*i) for i in values]
        super(DocViewGenVocab, self).__init__(terms)

DocViewGenVocabFactory = vocab_factory(DocViewGenVocab)
