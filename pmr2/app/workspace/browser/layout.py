from zope.component import getMultiAdapter
from paste.httpexceptions import HTTPNotFound

from AccessControl import Unauthorized
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

from pmr2.app.workspace.exceptions import *
from pmr2.app.browser.layout import FormWrapper


# XXX rename this into ProtocolFormWrapper or the like.
# XXX Make this generic.

class StorageFormWrapper(FormWrapper):
    """\
    This is a form wrapper is specific for interaction with the hgweb 
    objects.  Since Mercurial had its own permission controls that is
    disabled (since Zope/Plone manages its own), the methods to access/
    manipulate the repo is called directly.  
    
    As a result, permissions need to be defined, but storage exposes a
    process_request method that will handle the protocol requests.  Most
    protocol requests are reads (clones, pulls) so they should be
    allowed, leaving push to be the only one that needs restrictions.

    Another thing, protocol requests have to be handled here as this is 
    the object that gets called first, so no output of the wrapper HTML 
    should be generated.

    We would like to rely on the default Plone permissions to manage
    that specific case (specifically a POST to this object), but I 
    haven't figured this out yet, so I thought about making the
    __call__ method below that redirects non GETs to a specific view,
    however that will still result in duplicate code, so below we have
    manual authentication.
    """

    def authorized(self):
        if self.request.REQUEST_METHOD == 'GET':
            # This request method should have been authorized and not
            # required further processing.
            return True

        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            # Definitely not allowing anonymous pushes.
            return False

        user = pm.getAuthenticatedMember() 
        user_roles = user.getRolesInContext(self.context)
        # user either requires a role granted via @@sharing or has the
        # permission set manually under management.
        return u'WorkspacePusher' in user_roles or \
               user.has_permission('Mercurial Push', self.context)

    def __call__(self, *a, **kw):

        # XXX manual permissions checking.
        if not self.authorized():
            raise Unauthorized('user unauthorized to push to this workspace')

        try:
            storage = getMultiAdapter((self.context,), name='PMR2Storage')
        except PathInvalidError:
            # This is raised in the case where a Workspace object exists
            # without a corresponding Hg repo on the filesystem.
            # XXX this error page does not say what really happened.
            raise HTTPNotFound(self.context.title_or_id())

        try:
            # Note: this method can be used to manipulate the repo, use
            # with caution.
            results = storage.process_request(self.request)
            if self.request.REQUEST_METHOD in ['POST']:
                # update modification date if it was one of 
                # modification methods.
                self.context.setModificationDate(DateTime())
                self.context.reindexObject()
            return results
        except UnsupportedCommandError:
            return super(StorageFormWrapper, self).__call__(*a, **kw)


class BorderedStorageFormWrapper(StorageFormWrapper):
    """\
    Workspace default view uses this for the menu.
    """

    def __init__(self, *a, **kw):
        super(BorderedStorageFormWrapper, self).__init__(*a, **kw)
        self.request['enable_border'] = True
