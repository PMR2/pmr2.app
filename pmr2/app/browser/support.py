import zope.component

import z3c.form.field
import z3c.form.form

from plone.app.z3cform import layout

from pmr2.app.interfaces import IPMR2Search, IPMR2SearchAdd
from pmr2.app.content import PMR2Search

import form
import page


class PMR2SearchAddForm(form.AddForm):
    """\
    Repository root add form.
    """

    fields = z3c.form.field.Fields(IPMR2SearchAdd).select(
        'id',
        'title',
        'description',
        'catalog_index',
    )
    clsobj = PMR2Search

    # XXX register this as fti factory so the URI of this obj will be
    # used instead of createObject from the Plone menu
    # see: plone.app.contentmenu/plone/app/contentmenu/menu.py:709

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']
        ctxobj.description = self._data['description']
        # doing the long hand way to work around an issue where this
        # somehow results in the unbound object being used instead of
        # ctxobj.  No idea how the unbound object is referenced.
        # Anyway, this explicit call works around the implicit calls
        # as above.
        PMR2Search.catalog_index.__set__(ctxobj, self._data['catalog_index'])

PMR2SearchAddFormView = layout.wrap_form(PMR2SearchAddForm,
    label="PMR2 Custom Search Add Form")


class PMR2SearchEditForm(form.EditForm):
    """\
    Repository Edit/Management Form.
    """

    fields = z3c.form.field.Fields(IPMR2Search)

PMR2SearchEditFormView = layout.wrap_form(
    PMR2SearchEditForm, label="Repository Management")


class PMR2SearchPage(page.TraversePage):
    """\
    Wraps an object around the mathml view.
    """

    filetemplate = \
        zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'pmr2search.pt')

    def __call__(self, *args, **kwargs):
        return self.filetemplate()

PMR2SearchPageView = layout.wrap_form(
    PMR2SearchPage,
    __wrapper_class=page.BorderedTraverseFormWrapper,
)
