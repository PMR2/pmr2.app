from os.path import join

import zope.interface
from zope.component import getUtilitiesFor, getMultiAdapter
from zope.publisher.browser import BrowserPage
from zope.pagetemplate.interfaces import IPageTemplate

from Products.CMFCore.utils import getToolByName

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from pmr2.z3cform.page import SimplePage
from pmr2.z3cform.page import TraversePage


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

    index = ViewPageTemplateFile('rss.pt')

    def items(self):
        raise NotImplementedError('need items')
