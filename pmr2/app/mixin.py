from zope.component import queryMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from ZPublisher.BaseRequest import DefaultPublishTraverse

class TraversalCatchAll(object):

    def __before_publishing_traverse__(self, ob, request, view=None):
        """\
        This captures any unknown path and pass control to the default
        view via request_subpath variable.  Known paths will continue 
        through without issues.

        ob - object that is being traversed
        request - the request object
        view - optional, if specified this view will be used, it should
            handle the request_subpath.
        """

        # XXX Complications can happen if a content class inherits this!
        #
        # There are two ways to handle this.
        #
        # allow or disallow the overriding of features of this object
        # accessed via URI, such as object_delete.
        #
        # If the features are overridden, actioning on this object
        # will be required to be done elsewhere, but it will prevent
        # potential path clashes with internal relative references
        # this document may contain, and may actually be safer.

        stack = request['TraversalRequestNameStack']
        key = stack and stack[-1] or None
        if key is not None:
            # test whether this object can be published.

            # XXX if we want to neuter everything, just go skip this
            # check and neuter TraversalRequestNameStack
            adapter = queryMultiAdapter((ob, request), IPublishTraverse)
            if adapter is None:
                ## Zope2 doesn't set up its own adapters in a lot of cases
                ## so we will just use a default adapter.
                adapter = DefaultPublishTraverse(ob, request)

            adapter = DefaultPublishTraverse(ob, request)

            # XXX
            # There are special identifiers that are "not checked", so
            # they must be weeded out and let the standard traversal
            # handle all of them.
            special = ['@@', '++',]
            for s in special:
                if key.startswith(s):
                    return

            try:
                adapter.publishTraverse(request, key)
            except:
                # guess nothing, neuter TraversalRequestNameStack
                request['request_subpath'] = \
                    request['TraversalRequestNameStack']
                # this was reversed, reverse it back.
                request['request_subpath'].reverse()
                request['TraversalRequestNameStack'] = []
                if view:
                    request['TraversalRequestNameStack'].append(view)
