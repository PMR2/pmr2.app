from zope.interface import alsoProvides

from zope.schema.interfaces import IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class WorkspaceDirObjListVocab(SimpleVocabulary):

    def __init__(self, context):
        self.context = context
        values = self.context.get_repository_list()
        terms = [SimpleTerm(i, i[0]) for i in values]
        super(WorkspaceDirObjListVocab, self).__init__(terms)


def WorkspaceDirObjListVocabFactory(context):
    return WorkspaceDirObjListVocab(context)

alsoProvides(WorkspaceDirObjListVocabFactory, IVocabularyFactory)
