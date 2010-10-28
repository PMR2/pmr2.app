from os.path import join
import zope.interface

from zope.app.pagetemplate.viewpagetemplatefile \
    import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from pmr2.app.browser import page

from pmr2.app.workspace.browser.interfaces import *


class BaseFileRenderer(page.BrowserPage):
    zope.interface.implements(IWorkspaceFileRenderer)

    index = ViewPageTemplateFile('file.pt')

    def _getpath(self, view='rawfile', path=None):
        result = [
            self.context.absolute_url(),
            view,
            self.context.rev,
        ]
        if path:
            result.append(path)
        return result

    @property
    def rooturi(self):
        """the root uri."""
        return '/'.join(self._getpath())

    @property
    def fullpath(self):
        """permanent uri."""
        return '/'.join(self._getpath(path=self.context.data['file']))

    @property
    def viewpath(self):
        """view uri."""
        return '/'.join(self._getpath(view='file',
            path=self.context.data['file']))

    @property
    def contents(self):
        return ''

    def __call__(self):
        return self.index()


class DefaultFileRenderer(BaseFileRenderer):
    """\
    Default file render.
    """

    @property
    def contents(self):
        contents = self.context.data['contents']()
        if '\0' in contents:
            return '(%s)' % self.context.data['mimetype']()
        else:
            return contents
