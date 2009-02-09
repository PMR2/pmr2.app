from zope.interface import alsoProvides

from zope.schema.interfaces import IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName


class WorkspaceDirObjListVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        values = self.context.get_repository_list()
        terms = [SimpleTerm(i, i[0]) for i in values]
        super(WorkspaceDirObjListVocab, self).__init__(terms)


def WorkspaceDirObjListVocabFactory(context):
    return WorkspaceDirObjListVocab(context)

alsoProvides(WorkspaceDirObjListVocabFactory, IVocabularyFactory)


class ManifestListVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        values = self.context.get_manifest()
        terms = [SimpleTerm(i, i) for i in values]
        super(ManifestListVocab, self).__init__(terms)


def ManifestListVocabFactory(context):
    return ManifestListVocab(context)

alsoProvides(ManifestListVocabFactory, IVocabularyFactory)


class PMR2TransformsVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        pt = getToolByName(context, 'portal_transforms')
        terms = [SimpleTerm(i, getattr(pt, i).get_documentation().strip()) \
                for i in pt.objectIds() if i.startswith('pmr2_processor_')]
        super(PMR2TransformsVocab, self).__init__(terms)


def PMR2TransformsVocabFactory(context):
    return PMR2TransformsVocab(context)

alsoProvides(PMR2TransformsVocabFactory, IVocabularyFactory)
