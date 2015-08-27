import zope.interface
import zope.component

from zope.schema.interfaces import IVocabulary, IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component.hooks import getSite

from Products.CMFCore.utils import getToolByName

from pmr2.app.interfaces import *
from pmr2.app.annotation.interfaces import *

from pmr2.app.factory import vocab_factory


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
                zope.component.getUtilitiesFor(IExposureFileAnnotator)]

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


class ExposureFileNoteViewVocab(ExposureFileAnnotatorVocab):
    """\
    This is for the Note View listing, where the label of the annotator
    is used to generate the title.
    """

    def _getValues(self):
        return [(i[0], i[0], i[1].label) for i in 
                zope.component.getUtilitiesFor(IExposureFileAnnotator)]


class ExposureFileNotesAvailableVocab(ExposureFileAnnotatorVocab):
    """\
    This is for an ExposureFile object, where it checks for the list of
    views available within the note listing.
    """

    def _getValues(self):
        views = self.context.views or []
        return [(i[0], i[0], i[1].label) for i in 
                zope.component.getUtilitiesFor(IExposureFileAnnotator) if
                i[0] in views]

ExposureFileNotesAvailableVocabFactory = \
    vocab_factory(ExposureFileNotesAvailableVocab)


class DocViewGenVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        values = [(i[0], i[0], i[1].title) for i in 
                  zope.component.getUtilitiesFor(IDocViewGen)]
        # sort by title
        values.sort(cmp=lambda x, y: cmp(x[2], y[2]))
        terms = [SimpleTerm(*i) for i in values]
        super(DocViewGenVocab, self).__init__(terms)

    def getTerm(self, value):
        try:
            return super(DocViewGenVocab, self).getTerm(value)
        except LookupError:
            # can be triggered by various cases
            return SimpleTerm(value)

DocViewGenVocabFactory = vocab_factory(DocViewGenVocab)


class EFTypeBaseVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        self.pt = getToolByName(context, 'portal_catalog', None)
        if self.pt is None:
            # fallback
            self.pt = getToolByName(getSite(), 'portal_catalog', None)

        if self.pt is None:
            terms = []
        else:
            results = self.pt(
                portal_type='ExposureFileType',
                review_state='published',
            )
            terms = [self._makeTerm(brain) for brain in results]
        super(EFTypeBaseVocab, self).__init__(terms)

    def _makeTerm(self, brain):
        """
        Subclasses that actually provide the implementation need to
        override this.
        """

        raise NotImplementedError

    def getTerm(self, value):
        if self.pt is None:
            # no portal tool, see __init__
            return SimpleTerm(value)
        else:
            return super(EFTypeBaseVocab, self).getTerm(value)

    def __contains__(self, terms):
        if self.pt is None:
            # no portal tool as  __init__ didn't initialize.  Since
            # there may be cases where one might test where the term
            # that had already been assigned is in the vocab, we use
            # this assumption as the fallback.
            return True
        else:
            return super(EFTypeBaseVocab, self).__contains__(terms)


class EFTypeVocab(EFTypeBaseVocab):
    """
    Standard (legacy?) exposure file type vocab.
    """

    def _makeTerm(self, brain):
        return SimpleTerm(brain.getPath(), brain.Title, brain.Title)

EFTypeVocabFactory = vocab_factory(EFTypeVocab)


class EFTypeExportVocab(SimpleVocabulary):
    """
    The version for export purposes that will provide the tokens as URLs
    for web-service based access.  Future internal wizard usage may need
    to make use of this.
    """

    def _makeTerm(self, brain):
        return SimpleTerm(brain.getPath(), brain.getURL(), brain.Title)

EFTypeExportVocabFactory = vocab_factory(EFTypeExportVocab)

