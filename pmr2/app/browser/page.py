from os.path import join

import zope.interface
from zope.component import getUtilitiesFor, getMultiAdapter
from zope.publisher.browser import BrowserPage
from zope.app.authentication.httpplugins import HTTPBasicAuthCredentialsPlugin

from Products.CMFCore.utils import getToolByName

from zope.app.pagetemplate.viewpagetemplatefile \
    import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from pmr2.app.browser.interfaces import IPublishTraverse


class SimplePage(BrowserPage):
    """\
    A simple view generator/page/template class.
    """

    # override if necessary
    # XXX use adapter to register this instead?
    # XXX when adapter is defined, make this index, have adapter figure
    # what index is
    template = ViewPageTemplateFile('page.pt')

    @property
    def url_expr(self):
        return '%s/@@%s' % (self.context.absolute_url(), self.__name__)

    url_expr_full = url_expr

    @property
    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

    @property
    def label(self):
        return self.context.title_or_id()

    def subtitle(self):
        return None

    def content(self):
        # XXX in the redesign, it should call template directly
        raise NotImplementedError('need content')

    def update(self):
        pass

    def render(self):
        # XXX call index instead.
        return self.template()

    def __call__(self, *a, **kw):
        self.update()
        return self.render()


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
    # XXX use adapter to register this instead?
    template = ViewPageTemplateFile('page_nav.pt')
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
