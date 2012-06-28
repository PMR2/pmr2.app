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
    field = field.bind(form)
    terms = field.vocabulary
    return zope.component.queryMultiAdapter(
        (context, request, form, field, terms, widget),
        z3c.form.interfaces.ITerms)
