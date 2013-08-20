from zope.browsermenu.menu import BrowserSubMenuItem


class NullSubMenuItem(BrowserSubMenuItem):

    def available(self):
        return False
