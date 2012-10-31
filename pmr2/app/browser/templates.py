import os.path
import zope.deprecation
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)

from plone.app.z3cform.templates import Macros
