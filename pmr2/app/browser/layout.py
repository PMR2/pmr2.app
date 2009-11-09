import os.path

import zope.interface
from zope.app.authentication.httpplugins import HTTPBasicAuthCredentialsPlugin
from zope.component import getUtilitiesFor, getMultiAdapter
from plone.app.workflow.interfaces import ISharingPageRole
import plone.z3cform
from plone.z3cform import layout
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
from paste.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import url_quote

import pmr2.mercurial.exceptions

import pmr2.app.browser
from pmr2.app.browser.interfaces import IUpdatablePageView
from pmr2.app.browser.interfaces import IPlainLayoutWrapper
from pmr2.app.browser.interfaces import IPloneviewLayoutWrapper
from pmr2.app.browser.interfaces import IMathMLLayoutWrapper
from pmr2.app.browser.interfaces import IPublishTraverse
import pmr2.app.security.roles

path = lambda p: os.path.join(os.path.dirname(pmr2.app.browser.__file__), 
                              'templates', p)

ploneview_layout_factory = ZopeTwoFormTemplateFactory(
    path('ploneview_layout.pt'), form=IPloneviewLayoutWrapper)

plain_layout_factory = ZopeTwoFormTemplateFactory(
    path('plain_layout.pt'), form=IPlainLayoutWrapper)

mathml_layout_factory = ZopeTwoFormTemplateFactory(
    path('mathml_layout.pt'), form=IMathMLLayoutWrapper)


class FormWrapper(layout.FormWrapper):
    """\
    Wrapper that will call a update method of the form_instance within
    when called, if present.

    Not calling update because it is used by actual forms.
    """

    def __call__(self):
        if IUpdatablePageView.providedBy(self.form_instance):
            # only this interface is known to require updating.
            self.form_instance.update()
        return layout.FormWrapper.__call__(self)


class PloneviewLayoutWrapper(FormWrapper):
    """\
    A customized layout wrapper that also renders the viewlet managers
    defined in the default plone views.
    (rendered inside an h1) like the default plone.z3cform.
    """

    zope.interface.implements(IPloneviewLayoutWrapper)


class PlainLayoutWrapper(FormWrapper):
    """\
    A customized layout wrapper that does not have the title element
    (rendered inside an h1) like the default plone.z3cform.
    """

    zope.interface.implements(IPlainLayoutWrapper)


class BorderedFormWrapper(FormWrapper):
    """\
    A customized layout wrapper that sets enable_border on request
    to short circuit the permission checking.
    """

    def __init__(self, *a, **kw):
        super(BorderedFormWrapper, self).__init__(*a, **kw)
        self.request['enable_border'] = True


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

    def __call__(self, *a, **kw):

        # XXX manual permissions checking.
        if self.request.REQUEST_METHOD != 'GET':
            user_roles = self.request['AUTHENTICATED_USER'].getRolesInContext(
                self.context)
            if u'WorkspacePusher' not in user_roles:
                raise HTTPForbidden()

        try:
            storage = getMultiAdapter((self.context,), name='PMR2Storage')
        except pmr2.mercurial.exceptions.PathInvalidError:
            # This is raised in the case where a Workspace object exists
            # without a corresponding Hg repo on the filesystem.
            # XXX this error page does not say what really happened.
            raise HTTPNotFound(self.context.title_or_id())

        try:
            # Note: this method can be used to manipulate the repo, use
            # with caution.
            return storage.process_request(self.request)
        except pmr2.mercurial.exceptions.UnsupportedCommandError:
            return super(StorageFormWrapper, self).__call__(*a, **kw)


class BorderedStorageFormWrapper(StorageFormWrapper):
    """\
    Workspace default view uses this for the menu.
    """

    def __init__(self, *a, **kw):
        super(BorderedStorageFormWrapper, self).__init__(*a, **kw)
        self.request['enable_border'] = True


class TraverseFormWrapper(FormWrapper):
    """\
    A customized layout wrapper that implements traversal.

    This also passes in the subpath into the subform.
    """

    zope.interface.implements(IPublishTraverse)

    def __init__(self, *a, **kw):
        super(TraverseFormWrapper, self).__init__(*a, **kw)
        self.traverse_subpath = []
        if self.form is not None:
            assert IPublishTraverse.providedBy(self.form_instance)
            # sharing subpath list with instance of form.
            self.form_instance.traverse_subpath = self.traverse_subpath

    def publishTraverse(self, request, name):
        self.traverse_subpath.append(name)
        return self


class BorderedTraverseFormWrapper(TraverseFormWrapper):

    def __init__(self, *a, **kw):
        super(BorderedTraverseFormWrapper, self).__init__(*a, **kw)
        self.request['enable_border'] = True


class MathMLLayoutWrapper(FormWrapper):
    """\
    This layout wrapper provides XML stylesheet declarations for the
    rendering of MathML.
    """

    zope.interface.implements(IMathMLLayoutWrapper)

    def xml_stylesheet(self):
        """Returns a stylesheet with all content styles"""

        registry = getToolByName(aq_inner(self.context), 'portal_css')
        registry_url = registry.absolute_url()
        context = aq_inner(self.context)

        styles = registry.getEvaluatedResources(context)
        skinname = url_quote(aq_inner(self.context).getCurrentSkinName())
        result = []

        for style in styles:
            if style.getMedia() not in ('print', 'projection') \
                    and style.getRel()=='stylesheet':
                src = '<?xml-stylesheet href="%s/%s/%s" type="text/css"?>' % \
                    (registry_url, skinname, style.getId())
                result.append(src)
        return "\n".join(result)

    def __call__(self):
        result = super(MathMLLayoutWrapper, self).__call__()
        self.request.response.setHeader(
            'Content-Type', 'application/xhtml+xml')
        return result
