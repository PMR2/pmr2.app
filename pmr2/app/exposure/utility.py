import logging
import urllib
import zope.interface
import zope.component
from urlparse import urlparse
from plone.registry.interfaces import IRegistry
from pmr2.app.interfaces import IRegistrySettings
from pmr2.app.exposure.interfaces import IExposureFileTool
from pmr2.app.exposure.interfaces import IExposureSourceAdapter

logger = logging.getLogger(__name__)
# XXX magic string should be imported
prefix = 'pmr2.app.settings'


@zope.interface.implementer(IExposureFileTool)
class GithubIssueTool(object):
    """
    Provide a filled out template link to report an issue on Github.
    """

    label = u'Report a problem with this resource'

    def get_tool_link(self, exposure_object):
        registry = zope.component.getUtility(IRegistry)
        try:
            settings = registry.forInterface(IRegistrySettings, prefix=prefix)
        except KeyError:
            logger.warning(
                "settings for '%s' not found; pmr2.app may need to be "
                "reactivated", prefix,
            )
            return
        if not settings.github_issue_repo:
            return

        try:
            exposure, workspace, path = zope.component.getAdapter(
                exposure_object, IExposureSourceAdapter).source()
        except Exception:
            title = exposure_object.title_or_id()
        else:
            title = exposure.title_or_id()

        arguments = {
            'labels': 'exposure',
            'template': 'exposure.yml',
            'title': '[Exposure]: ' + title,
            'exposure-url': exposure_object.absolute_url(),
        }
        target = '%s/issues/new?%s' % (
            settings.github_issue_repo, urllib.urlencode(arguments))

        return target
