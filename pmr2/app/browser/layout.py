import os.path

import zope.interface
from zope.app.authentication.httpplugins import HTTPBasicAuthCredentialsPlugin
import zope.app.pagetemplate.viewpagetemplatefile
from zope.component import getUtilitiesFor, getMultiAdapter
import z3c.form.interfaces
from plone.app.workflow.interfaces import ISharingPageRole
import plone.z3cform
from plone.z3cform import layout
from plone.z3cform.templates import FormTemplateFactory
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
from paste.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden

from Acquisition import aq_inner
from AccessControl import Unauthorized
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import url_quote

from pmr2.app.workspace.exceptions import *

import pmr2.app.browser
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

__all__ = [
    'ploneview_layout_factory',
    'plain_layout_factory',
    'mathml_layout_factory',

    'FormWrapper',
    'PloneviewLayoutWrapper',
    'PlainLayoutWrapper',
    'BorderedFormWrapper',
    'TraverseFormWrapper',
    'PlainTraverseLayoutWrapper',
    'PlainTraverseOverridableWrapper',
    'BorderedTraverseFormWrapper',
    'MathMLLayoutWrapper',
]


class Macros(plone.z3cform.templates.Macros):
    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        path('macros.pt'))

    def __getitem__(self, key):
        return self.template.macros[key]


class FormWrapper(layout.FormWrapper):
    """\
    This used to partially enable the update/render pattern for our
    forms/views that required it.
    """


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
            self.traverse_subpath = self.form_instance.traverse_subpath

    def publishTraverse(self, request, name):
        self.form_instance.publishTraverse(request, name)
        return self


class PlainTraverseLayoutWrapper(TraverseFormWrapper):
    zope.interface.implements(IPlainLayoutWrapper)


class PlainTraverseOverridableWrapper(PlainTraverseLayoutWrapper):
    """\
    This wrapper, if traversal elements are included, skip itself and
    use the internal form only.
    """

    def __call__(self):
        if self.traverse_subpath:
            return self.form_instance()
        return super(PlainTraverseOverridableWrapper, self).__call__()


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
