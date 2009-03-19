import zope.interface
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces import IPublishTraverse
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from plone.z3cform import layout

import pmr2.mercurial.exceptions


class BorderedFormWrapper(layout.FormWrapper):
    """\
    A customized layout wrapper that sets enable_border on request
    to short circuit the permission checking.
    """

    def __init__(self, *a, **kw):
        super(BorderedFormWrapper, self).__init__(*a, **kw)
        self.request['enable_border'] = True


class StorageFormWrapper(layout.FormWrapper):
    """\
    If cmd is present, pass control to the storage object, let it 
    generate the result from the request sent by client.
    """

    def __call__(self, *a, **kw):
        storage = self.context.get_storage()
        try:
            return storage.process_request(self.request)
        except pmr2.mercurial.exceptions.UnsupportedCommand:
            return super(StorageFormWrapper, self).__call__(*a, **kw)


class BorderedStorageFormWrapper(StorageFormWrapper):
    """\
    Workspace default view uses this for the menu.
    """

    def __init__(self, *a, **kw):
        super(BorderedStorageFormWrapper, self).__init__(*a, **kw)
        self.request['enable_border'] = True


class TraverseFormWrapper(layout.FormWrapper):
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


class SimplePage(BrowserPage):
    """\
    A simple view generator/page/template class.  This is meant to be
    wrapped by the layout.wrap_form from plone.z3cform and its wrapper
    class layout.FormWrapper.
    """

    # override if necessary
    # XXX use adapter to register this instead?
    template = ViewPageTemplateFile('page.pt')

    # XXX need to figure out how to automatically link this together
    # with the real template.
    url_expr = None

    @property
    def label(self):
        return self.context.title_or_id()

    def subtitle(self):
        return None

    def content(self):
        raise NotImplementedError('need content')

    def __call__(self, *a, **kw):
        return self.template()


class TraversePage(SimplePage):
    """\
    A simple page class that supports traversal.
    """

    zope.interface.implements(IPublishTraverse)

    def __init__(self, *a, **kw):
        super(TraversePage, self).__init__(*a, **kw)
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        self.traverse_subpath.append(name)
        return self


class NavPage(TraversePage):

    # override if necessary
    # XXX use adapter to register this instead?
    template = ViewPageTemplateFile('page_nav.pt')
    navtemplate = ViewPageTemplateFile('default_nav.pt')

    topnav = True  # show nav above content
    botnav = True  # show nav below content

    def navcontent(self):
        return self.navtemplate()

    def navlist(self):
        raise NotImplementedError('need navigation elements')
