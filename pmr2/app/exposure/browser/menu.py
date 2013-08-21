import zope.component
from zope.browsermenu.menu import BrowserSubMenuItem

from plone.app.contentmenu.menu import WorkflowMenu
from plone.app.contentmenu.menu import WorkflowSubMenuItem

from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.exposure.interfaces import IExposureFile
from pmr2.app.exposure.interfaces import IExposureFolder


class NullSubMenuItem(BrowserSubMenuItem):

    def available(self):
        return False


class ExposureWorkflowMenu(WorkflowMenu):

    def getMenuItems(self, context, request):
        # Have to set the context to the root.
        if (IExposureFile.providedBy(context) or
                IExposureFolder.providedBy(context)):
            helper = zope.component.queryAdapter(
                context, IExposureSourceAdapter)
            exposure, workspace, path = helper.source()
            context = exposure
        return WorkflowMenu.getMenuItems(self, context, request)


class ExposureWorkflowSubMenuItem(WorkflowSubMenuItem):

    def __init__(self, context, request):
        # Have to set the context to the root.
        helper = zope.component.queryAdapter(context, IExposureSourceAdapter)
        exposure, workspace, path = helper.source()
        context = exposure
        WorkflowSubMenuItem.__init__(self, context, request)
