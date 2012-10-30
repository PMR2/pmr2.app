import os.path
import zope.deprecation
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)

from plone.app.z3cform.templates import Macros

from plone.app.z3cform import templates


class PMR2PlainMacros(templates.Macros):
    """\
    Trying to make life easier for general testing
    """

    index = ViewPageTemplateFile(path('pmr2-plain-macros.pt'))


class PMR2MainMacros(templates.Macros):
    """\
    The main macros, including templates.
    """

    index = ViewPageTemplateFile(path('pmr2-main-macros.pt'))
