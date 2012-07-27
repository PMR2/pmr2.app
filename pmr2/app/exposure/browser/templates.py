import os.path

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from pmr2.app.interfaces import IPMR2AppLayer
from pmr2.app.browser import templates

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)


class Macros(templates.Macros):
    """\
    Extension to the default macros.
    """

    index = ViewPageTemplateFile(path('macros.pt'))
