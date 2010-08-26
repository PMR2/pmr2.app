from os.path import join

import zope.interface
from zope.component import getUtilitiesFor, getMultiAdapter
from zope.publisher.browser import BrowserPage
from zope.app.authentication.httpplugins import HTTPBasicAuthCredentialsPlugin

from zope.app.pagetemplate.viewpagetemplatefile \
    import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from z3c.form.interfaces import IForm

from plone.z3cform import layout

from pmr2.app.browser.interfaces import IPublishTraverse


class SimplePage(BrowserPage):
    """\
    A simple view generator/page/template class.  This is meant to be
    wrapped by the layout.wrap_form from plone.z3cform and its wrapper
    class layout.FormWrapper.
    """

    # marker to allow this to use the z3c form wrap_form method
    zope.interface.implements(IForm)

    # override if necessary
    # XXX use adapter to register this instead?
    template = ViewPageTemplateFile('page.pt')

    @property
    def url_expr(self):
        return '%s/@@%s' % (self.context.absolute_url(), self.__name__)

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
        raise NotImplementedError('need content')

    def update(self):
        pass

    def render(self):
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
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        self.traverse_subpath.append(name)
        return self


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
