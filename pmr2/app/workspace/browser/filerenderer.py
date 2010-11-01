from os.path import join
import zope.interface
from zope.contentprovider.interfaces import IContentProvider
from zope.contentprovider.provider import ContentProviderBase

from zope.app.pagetemplate.viewpagetemplatefile \
    import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from pmr2.app.browser import page

from pmr2.app.workspace.interfaces import IWorkspaceFileListProvider
from pmr2.app.workspace import table
from pmr2.app.workspace.browser.interfaces import *
from pmr2.app.workspace.browser.browser import WorkspaceTraversePage
from pmr2.app.workspace.browser.browser import FileInfoPage


class FileRendererProvider(ContentProviderBase):

    def render(self, *a, **kw):
        data = self.request['_data']
        mimetype = data['mimetype']()
        if mimetype:
            view = 'default'
            for u in zope.component.getAllUtilitiesRegisteredFor(
                    IWorkspaceFileRenderer):
                render = u.match(mimetype)
                if render:
                    view = render
                    break
        else:
            view = 'directory'

        fileview = zope.component.getMultiAdapter(
            (self.context, self.request), name=view)
        return fileview()


class BaseFileRenderer(FileInfoPage):
    zope.interface.implements(IWorkspaceFileRenderer)

    template = ViewPageTemplateFile('file.pt')

    @property
    def contents(self):
        return ''


class DirectoryRenderer(BaseFileRenderer):
    """\
    Default file render.
    """

    zope.interface.implements(IWorkspaceFileListProvider)

    @property
    def values(self):
        # this is a callable object, or what the table class expects.
        return self._values['contents']

    def __call__(self):
        # this is a dictionary with a contents key, which is a
        # method that will return the values expected by the table
        # rendering class.
        self._values = self.request['_data']
        tbl = table.FileManifestTable(self, self.request)
        tbl.update()
        return tbl.render()


class DefaultFileRenderer(BaseFileRenderer):
    """\
    Default file render.
    """

    @property
    def contents(self):
        data = self.request['_data']
        contents = data['contents']()
        if '\0' in contents:
            return '(%s)' % data['mimetype']()
        else:
            return contents
