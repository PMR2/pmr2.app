import zope.interface
import zope.component

from pmr2.app.workspace.browser.interfaces import IFileAction


@zope.interface.implementer(IFileAction)
class BaseFileAction(object):
    title = None
    description = None

    def href(self, view):
        return None


class SourceFileAction(BaseFileAction):

    title = u'Source'
    description = u'View this file'

    def href(self, view):
        return view.fullpath


class DownloadFileAction(BaseFileAction):

    title = u'Download'
    description = u'Download this file'

    def href(self, view):
        return view.downloadpath
