import zope.interface
import zope.component
from collections import OrderedDict
from Products.CMFCore.utils import getToolByName
from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.workspace.interfaces import IStorage, IWorkspace

from pmr2.app.utility.interfaces import ILatestRelatedExposureTool


@zope.interface.implementer(ILatestRelatedExposureTool)
class LatestRelatedExposureTool(object):

    def related_to_context(self, context):
        catalog = getToolByName(context, 'portal_catalog')

        is_workspace = IWorkspace.providedBy(context)
        if is_workspace:
            workspace = context
        else:
            # assume exposure
            _, workspace, _ = zope.component.getAdapter(
                context, IExposureSourceAdapter).source()

        src_workspace = '/'.join(workspace.getPhysicalPath())
        storage = IStorage(workspace)
        try:
            roots = storage.roots()
        except NotImplementedError:
            related_workspaces = [src_workspace]
        else:
            related_workspaces = [b.getPath() for b in catalog(
                portal_type='Workspace',
                pmr2_workspace_storage_roots=roots,
            )]

        query = {}
        query['portal_type'] = 'Exposure'
        query['review_state'] = 'published'
        query['pmr2_exposure_workspace'] = related_workspaces
        query['sort_on'] = 'modified'
        query['sort_order'] = 'reverse'
        exposures = catalog(**query)

        results = OrderedDict()

        for exp in exposures:
            if exp.pmr2_exposure_workspace in results:
                continue

            rec_workspace = {}
            rec_exposure = {}
            results[exp.pmr2_exposure_workspace] = record = {
                'workspace': rec_workspace,
                'exposure': rec_exposure,
                'this': src_workspace == exp.pmr2_exposure_workspace,
            }
            wks = catalog(path=exp.pmr2_exposure_workspace)[0]
            rec_workspace['title'] = wks.Title or wks.id
            rec_workspace['uri'] = wks.getURL()
            rec_workspace['commit_id'] = exp.pmr2_exposure_commit_id
            rec_exposure['title'] = exp.Title or exp.id
            rec_exposure['uri'] = exp.getURL()
            rec_exposure['modified'] = exp.ModificationDate

        return results
