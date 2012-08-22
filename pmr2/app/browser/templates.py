import os.path

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from plone.app.z3cform import templates

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)


class Macros(templates.Macros):
    """\
    Extension to the default macros.
    """

    index = ViewPageTemplateFile(path('macros.pt'))


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
