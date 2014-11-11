from zope.interface import implementer
from zope.component import getAdapter

from pmr2.app.exposure.interfaces import IExposureDownloadTool
from pmr2.app.exposure.interfaces import IExposureFile
from pmr2.app.exposure.interfaces import IExposureSourceAdapter


@implementer(IExposureDownloadTool)
class TgzDownloadTool(object):
    """
    Link to the target archive.
    """

    label = u'Complete Archive as .tgz'
    suffix = '.tgz'
    mimetype = 'application/x-tar'

    def get_download_link(self, exposure_object):
        try:
            exposure, workspace, path = getAdapter(exposure_object,
                IExposureSourceAdapter).source()
        except:
            return None

        return '%s/@@archive/%s/tgz' % (
            workspace.absolute_url(), exposure_object.commit_id)

    def download(self, exposure_object, request):
        # Workspace does this...
        raise NotImplementedError


@implementer(IExposureDownloadTool)
class FileDownloadTool(object):
    """
    Per file download.
    """

    label = u'Download This File'
    suffix = None
    mimetype = None

    def get_download_link(self, exposure_object):
        if not IExposureFile.providedBy(exposure_object):
            return

        try:
            exposure, workspace, path = getAdapter(exposure_object,
                IExposureSourceAdapter).source()
        except:
            return

        return '%s/@@%s/%s/%s' % (
            workspace.absolute_url(), 'rawfile', exposure.commit_id, path
        )

    def download(self, exposure_object, request):
        # The link does what needs to be done.
        raise NotImplementedError
