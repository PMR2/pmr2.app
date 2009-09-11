import os.path

import zope.interface
from zope.app.authentication.httpplugins import HTTPBasicAuthCredentialsPlugin
from zope.publisher.interfaces import IPublishTraverse
from zope.component import getUtilitiesFor, getMultiAdapter
from plone.app.workflow.interfaces import ISharingPageRole
import plone.z3cform
from plone.z3cform import layout
from plone.z3cform.templates import ZopeTwoFormTemplateFactory

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import url_quote

import pmr2.mercurial.exceptions

import pmr2.app.browser
from pmr2.app.browser.interfaces import IUpdatablePageView
from pmr2.app.browser.interfaces import IPlainLayoutWrapper
from pmr2.app.browser.interfaces import IMathMLLayoutWrapper
import pmr2.app.security.roles

path = lambda p: os.path.join(os.path.dirname(pmr2.app.browser.__file__), 
                              'templates', p)

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
    If cmd is present, pass control to the storage object, let it 
    generate the result from the request sent by client.
    """

    # XXX how to unit test this?

    def __call__(self, *a, **kw):
        if self.request.REQUEST_METHOD != 'GET':
            # if request is POST, we are changing things so we need
            # authentication.

            # authenticate the role - there must be a better way than 
            # this and probably should be done at much higher levels 
            # (if possible)

            # XXX need to directly involve pmr2.app.security.roles
            # somehow, eventually, to authenticate, such as:
            #roles = dict([(i[1], i[0]) for i in 
            #    getUtilitiesFor(ISharingPageRole)])

            user_roles = self.request['AUTHENTICATED_USER'].\
                getRolesInContext(self.context)

            if u'WorkspacePusher' not in user_roles:
                # request for authentication.
                auth = HTTPBasicAuthCredentialsPlugin()
                auth.challenge(self.request)
                return False

        storage = getMultiAdapter((self.context,), name='PMR2Storage')
        try:
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
            # XXX should probably check whether self.form implements
            # IPublishTraverse
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
