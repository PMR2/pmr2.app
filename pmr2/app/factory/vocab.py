import zope.interface
from zope.schema.interfaces import IVocabularyFactory

def vocab_factory(vocab):
    def _vocab_factory(context):
        return vocab(context)
    zope.interface.alsoProvides(_vocab_factory, IVocabularyFactory)
    return _vocab_factory
