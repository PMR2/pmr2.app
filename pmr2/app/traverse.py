from zope.component import queryAdapter, adapts
from zope.publisher.interfaces import IRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse

from pmr2.app.interfaces import IExposureSourceAdapter
from pmr2.app.content.interfaces import IExposureFolder


class ExposureTraverser(DefaultPublishTraverse):
    """\
    Exposure traverser that catches requests for objects which are not 
    inside zope to pass it into its workspace and commit id to handle.
    """

    adapts(IExposureFolder, IRequest)

    # the workspace view that will return the raw content.
    target_view = 'rawfile'

    def defaultTraverse(self, request, name):
        return super(ExposureTraverser, self).publishTraverse(request, name)

    def publishTraverse(self, request, name):
        try:
            return self.defaultTraverse(request, name)
        except AttributeError:
            pass
        # construct redirection
        helper = queryAdapter(self.context, IExposureSourceAdapter)
        exposure, workspace, ctxpath = helper.source()
        cpf = ctxpath and [ctxpath] or []
        path = '/'.join(cpf + [name] + request['TraversalRequestNameStack'])
        target_uri = '%s/@@%s/%s/%s' % (workspace.absolute_url(),
            self.target_view, exposure.commit_id, path)
        request['TraversalRequestNameStack'] = []
        return request.response.redirect(target_uri)

