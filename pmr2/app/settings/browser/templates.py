import os.path

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)
