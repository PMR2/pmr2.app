import zope.interface
import zope.component

from zope.publisher.interfaces import IRequest
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound, Redirect
from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.CMFCore.utils import getToolByName

from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.exposure.interfaces import IExposureFolder
from pmr2.app.exposure.interfaces import IExposureContainer


class RedirectView(BrowserView):

    target = None

    def __call__(self):
        if self.target:
            return self.request.response.redirect(self.target)
        raise NotFound()


class ExposureTraverser(DefaultPublishTraverse):
    """\
    Exposure traverser that catches requests for objects which are not 
    inside zope to pass it into its workspace and commit id to handle.
    """

    zope.component.adapts(IExposureFolder, IRequest)

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
        helper = zope.component.queryAdapter(self.context,
            IExposureSourceAdapter)
        exposure, workspace, ctxpath = helper.source()
        cpf = ctxpath and [ctxpath] or []
        namestack = request['TraversalRequestNameStack']
        request['TraversalRequestNameStack'] = []
        namestack.reverse()
        path = '/'.join(cpf + [name] + namestack)
        target_uri = '%s/@@%s/%s/%s' % (workspace.absolute_url(),
            self.target_view, exposure.commit_id, path)

        view = zope.component.getMultiAdapter((self.context, request),
            zope.interface.Interface, 'redirect_view')
        view.target = target_uri
        return view


class ExposureContainerTraverser(DefaultPublishTraverse):
    """\
    Traverser for the exposure container that will enable the resolution
    of partial subpaths into its full path, when a non-sequential
    exposure id generator is used.
    """

    zope.component.adapts(IExposureContainer, IRequest)

    base_query = {
        'portal_type': 'Exposure',
    }

    def defaultTraverse(self, request, name):
        return super(ExposureContainerTraverser, self).publishTraverse(
            request, name)

    def publishTraverse(self, request, name):
        try:
            return self.defaultTraverse(request, name)
        except AttributeError:
            result = self.customTraverse(request, name)
            if not result:
                raise
            return result

    def customTraverse(self, request, name):
        # While it is possible to get the keys using the name as id 
        # fragment to pass into the self.context._tree.keys() method
        # (the internal OOBTree variable), it can be "dangerous", so
        # we use the catalog since it offers a bit more options, such
        # as whether the object is published or not.

        catalog = getToolByName(self.context, 'portal_catalog')

        # I wish there is a 'between' in place of 'minmax', for the
        # reasons below.
        # 
        # For the range minmax to work, we have two ways:
        # 1) increment the ascii of the last character ('aaa' -> 'aab')
        # 2) append the last known character ('aaa' -> 'aaaz')
        #
        # 1) works, except when an object with the id 'aab' is present,
        # that object will be returned along with results as 'minmax' is
        # inclusive.
        # 2) will not return 'aaazz', even though it also starts with
        # 'aaa'.
        #
        # Normally 1) would be the sane choice because the existence
        # of the exactly named element can be found, it requires a
        # separate query for that lone element.  However, the ids we
        # generate for exposures are hexidecimal, hence even appending
        # a 'g' to the max value will be sufficient to satisfy the
        # requred query, but we are going to use 'z' anyway.

        maxid = name + 'z'

        query = {
            'path': '/'.join(self.context.getPhysicalPath()),
            'id': {
                'query': [name, maxid],
                'range': 'minmax',
            },
        }

        query.update(self.base_query)
        results = catalog(**query)

        if len(results) == 1:
            # exactly one result, we will redirect to this id, and 
            # include the remaining fragments in the namestack.
            fragments = [self.context.absolute_url(), results[0].id]
            namestack = request['TraversalRequestNameStack']
            request['TraversalRequestNameStack'] = []
            namestack.reverse()
            fragments.extend(namestack)
            target = '/'.join(fragments)

            view = zope.component.getMultiAdapter((self.context, request),
                zope.interface.Interface, 'redirect_view')
            view.target = target
            return view

        return None
