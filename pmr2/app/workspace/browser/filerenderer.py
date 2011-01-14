from os.path import join
import zope.interface
from zope.contentprovider.interfaces import IContentProvider
from zope.contentprovider.provider import ContentProviderBase

from zope.app.pagetemplate.viewpagetemplatefile \
    import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from Products.statusmessages.interfaces import IStatusMessage

from pmr2.app.browser import page

from pmr2.app.workspace.interfaces import IWorkspaceFileListProvider
from pmr2.app.workspace import table
from pmr2.app.workspace.browser.interfaces import *
from pmr2.app.workspace.browser.browser import WorkspaceTraversePage
from pmr2.app.workspace.browser.browser import FileInfoPage


class DefaultRendererDictionary(object):

    zope.interface.implements(IRendererDictionary)

    def match(self, data):
        mimetype = data['mimetype']()
        if not mimetype:
            return 'directory'

        if mimetype.startswith('image/'):
            return 'image'
        else:
            return 'default'


class FileRendererProvider(ContentProviderBase):

    def render(self, *a, **kw):
        errors = []
        results = ''
        status = IStatusMessage(self.request)
        data = self.request['_data']

        finder = list(zope.component.getUtilitiesFor(IRendererDictionary))
        if not finder:
            status.addStatusMessage(
                u'No render dictionary installed, please contact site '
                 'administrator.', 'error')
            return
        # get the default (unamed) to be last one
        finder.reverse()  

        for n, u in finder:
            view = u.match(data)
            if view:
                fileview = zope.component.getMultiAdapter(
                    (self.context, self.request), name=view)
                try:
                    results = fileview()
                    break

                except:
                    errors.append(
                        '"%s" selected "%s" but it failed to render.' %
                        (n or '<default>', view))
                    continue

        if errors:
            # probably should only show this info message to users who
            # can deal with this.
            status.addStatusMessage(' '.join(errors), 'info')

        if results:
            return results


class BaseFileRenderer(FileInfoPage):
    zope.interface.implements(IFileRenderer)

    template = ViewPageTemplateFile('file.pt')

    @property
    def contents(self):
        return ''


class DirectoryRenderer(BaseFileRenderer, table.FileManifestTable):
    """\
    Default directory render.  Includes table.
    """

    zope.interface.implements(IDirectoryRenderer)

    def __init__(self, context, request):
        BaseFileRenderer.__init__(self, context, request)
        table.FileManifestTable.__init__(self, context, request)

    @property
    def values(self):
        # ignoring the adapter for now.
        return self._values['contents']()

    def update(self):
        BaseFileRenderer.update(self)
        self._values = self.request['_data']
        table.FileManifestTable.update(self)

    def render(self):
        return table.FileManifestTable.render(self)

    def __call__(self):
        self.update()
        return self.render()


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


class ImageRenderer(BaseFileRenderer):
    """\
    Default file render.
    """

    template = ViewPageTemplateFile('image.pt')

    @property
    def contents(self):
        return self.fullpath
