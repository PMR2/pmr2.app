import zope.component
from zope.contentprovider.interfaces import IContentProvider
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class AboveContentBodyPortletsViewlet(ViewletBase):
    index = ViewPageTemplateFile('above_content_body_portlets.pt')

    def render(self):
        adapter = zope.component.queryMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, self.__name__)
        if not adapter:
            # PMR2 is probably not installed as no content provider is
            # available.
            return u''
        return super(AboveContentBodyPortletsViewlet, self).render()
