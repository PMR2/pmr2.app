from zope.publisher.browser import BrowserPage
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class SimplePage(BrowserPage):
    """\
    A simple view generator/page/template class.  This is meant to be
    wrapped by the layout.wrap_form from plone.z3cform and its wrapper
    class layout.FormWrapper.
    """

    # override if necessary
    # XXX use adapter to register this instead?
    template = ViewPageTemplateFile('page.pt')

    @property
    def label(self):
        return self.context.title_or_id()

    def subtitle(self):
        return None

    def content(self):
        raise NotImplementedError('need content')

    def __call__(self, *a, **kw):
        return self.template()
