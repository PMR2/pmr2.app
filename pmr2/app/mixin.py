from ZPublisher.BaseRequest import DefaultPublishTraverse

class TraversalCatchAll(object):

    def __before_publishing_traverse__(self, ob, request):
        """\
        This captures any unknown path and pass control to the default
        view via request_subpath variable.  Known paths will continue 
        through without issues.
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
            pubtest = DefaultPublishTraverse(ob, request)
            try:
                pubtest.publishTraverse(request, key)
            except:
                # guess nothing, neuter TraversalRequestNameStack
                request['request_subpath'] = \
                    request['TraversalRequestNameStack']
                request['TraversalRequestNameStack'] = []
