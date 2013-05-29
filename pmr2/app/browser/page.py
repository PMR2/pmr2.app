from os.path import join

import zope.interface
import zope.deprecation
from zope.component import getUtilitiesFor, getMultiAdapter
from zope.publisher.browser import BrowserPage
from zope.pagetemplate.interfaces import IPageTemplate

from Products.CMFCore.utils import getToolByName

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))


try:
    from pmr2.z3cform.page import SimplePage
    zope.deprecation.deprecated('SimplePage', 
        'SimplePage has been moved to pmr2.z3cform.form.  '
        'Please update the import location before pmr2.app-0.7')
except ImportError:
    pass

try:
    from pmr2.z3cform.page import TraversePage
    zope.deprecation.deprecated('TraversePage', 
        'TraversePage has been moved to pmr2.z3cform.form.  '
        'Please update the import location before pmr2.app-0.7')
except ImportError:
    pass


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
