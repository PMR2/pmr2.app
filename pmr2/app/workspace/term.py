import zope.interface
import zope.component

import z3c.form

from pmr2.app.workspace.schema.interfaces import IStorageFileChoice


@zope.interface.implementer(z3c.form.interfaces.ITerms)
@zope.component.adapter(
    zope.interface.Interface,
    z3c.form.interfaces.IFormLayer,
    zope.interface.Interface,
    IStorageFileChoice,
    z3c.form.interfaces.IWidget)
def StorageFileChoiceTerms(context, request, form, field, widget):
    # naively reuse the cached vocabulary; this may become an issue if
    # a particular form references two distinct commits, but this would
    # likely need a different terms/vocab provider anyway, so caching
    # the vocabulary on the request object by vocabularyName should be
    # fine?
    field.vocabulary = request.get('vocab:' + field.vocabularyName)
    field = field.bind(form)
    request['vocab:' + field.vocabularyName] = terms = field.vocabulary
    return zope.component.queryMultiAdapter(
        (context, request, form, field, terms, widget),
        z3c.form.interfaces.ITerms)
