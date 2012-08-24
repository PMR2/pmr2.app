from os.path import join

import zope.interface
from zope.component import getUtilitiesFor, getMultiAdapter
from zope.publisher.browser import BrowserPage
from zope.pagetemplate.interfaces import IPageTemplate
from zope.app.authentication.httpplugins import HTTPBasicAuthCredentialsPlugin

from Products.CMFCore.utils import getToolByName

from zope.app.pagetemplate.viewpagetemplatefile \
    import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from pmr2.app.browser.interfaces import IPublishTraverse


class BasePage(BrowserPage):
    """\
    A simple view generator/page/template class.
    """

    # override if necessary
    # XXX use adapter to register this instead?
    # XXX when adapter is defined, make this index, have adapter figure
    # what index is

    index = ViewPageTemplateFile('basepage.pt')
    template = ''

    @property
    def url_expr(self):
        return '%s/@@%s' % (self.context.absolute_url(), self.__name__)

    url_expr_full = url_expr

    @property
    def portal_url(self):
        portal_url = getToolByName(self.context, 'portal_url', None)
        if portal_url:
            portal = portal_url.getPortalObject()
            return portal.absolute_url()

    @property
    def label(self):
        label = getToolByName(self.context, 'title_or_id', None)
        if label:
            return label()

    def update(self):
        pass

    def render(self):
        # render content template
        # XXX probably adapter base could work
        return self.index()

    def __call__(self, *a, **kw):
        self.update()
        return self.render()


class SimplePage(BasePage):
    """\
    A simple view that only requires a very simple template (without the
    boiler plates).
    """

    def subtitle(self):
        return None

    def render(self):
        # XXX not properly documented feature:
        # Setting index to None will disable the rendering of the 
        # site boilerplate defined in the index.
        if self.index:
            return super(SimplePage, self).render()
        return self.template()


class TraversePage(SimplePage):
    """\
    A simple page class that supports traversal.
    """

    zope.interface.implements(IPublishTraverse)

    def __init__(self, *a, **kw):
        super(TraversePage, self).__init__(*a, **kw)
        if not self.request.environ.get('pmr2.traverse_subpath', None):
            self.request.environ['pmr2.traverse_subpath'] = []

    @property
    def url_expr_full(self):
        return '/'.join((self.context.absolute_url(), self.__name__) +
                        tuple(self.traverse_subpath))

    def publishTraverse(self, request, name):
        self.traverse_subpath.append(name)
        return self

    def _get_traverse_subpath(self):
        return self.request.environ['pmr2.traverse_subpath']

    def _set_traverse_subpath(self, value):
        self.request.environ['pmr2.traverse_subpath'] = value

    traverse_subpath = property(_get_traverse_subpath, _set_traverse_subpath)


class NavPage(TraversePage):

    # override if necessary
    index = ViewPageTemplateFile('page_nav.pt')
    navtemplate = ViewPageTemplateFile('default_nav.pt')

    topnav = True  # show nav above content
    botnav = True  # show nav below content

    def navcontent(self):
        return self.navtemplate()

    def navlist(self):
        raise NotImplementedError('need navigation elements')


class RssPage(SimplePage):
    """\
    RSS page.
    """

    template = ViewPageTemplateFile('rss.pt')

    def items(self):
        raise NotImplementedError('need items')
