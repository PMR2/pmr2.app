import os.path

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from plone.app.z3cform import templates

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)


class Macros(templates.Macros):
    """\
    Extension to the default macros.
    """

    index = ViewPageTemplateFile(path('macros.pt'))
