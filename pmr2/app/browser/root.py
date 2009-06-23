import re

import zope.component
from zope.publisher.interfaces import NotFound

import z3c.form.field
import z3c.form.form

from plone.z3cform import layout

from Products.CMFCore.utils import getToolByName

from pmr2.app.interfaces import *
from pmr2.app.content import *

from pmr2.app.browser import form
from pmr2.app.browser import exposure
from pmr2.app.browser import page
from pmr2.app.browser.page import ViewPageTemplateFile
from pmr2.app.browser import widget


class PMR2AddForm(form.AddForm):
    """\
    Repository root add form.
    """

    fields = z3c.form.field.Fields(IPMR2Add).select(
        'id',
        'title',
    )
    clsobj = PMR2

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']

    def post_add(self, ctxobj):
        """\
        Create the required container objects.

        It may be better to move this to profile if possible.
        """

        add_container(ctxobj, WorkspaceContainer)
        add_container(ctxobj, SandboxContainer)
        add_container(ctxobj, ExposureContainer)

PMR2AddFormView = layout.wrap_form(PMR2AddForm, label="Repository Add Form")


class PMR2EditForm(form.EditForm):
    """\
    Repository Edit/Management Form.
    """

    fields = z3c.form.field.Fields(IPMR2).select(
        'repo_root',
    )

# Plone Form wrapper for the EditForm
PMR2EditFormView = layout.wrap_form(
    PMR2EditForm, label="Repository Management")


def add_container(context, clsobj):
    # helper method to construct the PMR2 internal containers
    obj = clsobj()
    context[obj.id] = obj
    # grab object from context
    obj = context[obj.id]
    obj.title = obj.id.title()
    obj.notifyWorkflowCreated()
    obj.reindexObject()
    return obj

re_clean_name = re.compile('_version[0-9]{2}(.*)$')

# also need an exposure_folder_listing that mimics the one below.


class RootFolderListing(layout.FormWrapper):
    """
    A hook for handling PMR1 uris.
    """

    form_instance = ViewPageTemplateFile('migrated.pt')

    def __call__(self):

        if 'request_subpath' not in self.request:
            # since path is empty, we do default things.
            return self.context.folder_listing()

        oid = self.request['request_subpath'][0]
        trail = self.request['request_subpath'][1:]
        o = zope.component.queryAdapter(self.context, name='PMRImportMap')
        if not o or oid not in o.pmrimport_map:
            # adapter has no import map, or id requested is not in
            # the import map we don't know what to do with the extra 
            # bit, so not found is raised.
            raise NotFound(self.context, oid, self.request)
        
        info = o.pmrimport_map[oid]
        # have to compute value of workspace from requested id as it is
        # not saved.
        self.workspace = oid[:oid.find('_version')]
        self.rev = info[1]
        self.oid = oid

        if trail and trail[0] in ['download', 'pmr_model']:
            # we redirect to the original CellML file that should now
            # be in a workspace.
            fn = re_clean_name.sub('\\1.cellml', oid)
            uri = '/'.join([
                self.context.absolute_url(), 
                'workspace', 
                self.workspace,
                '@@rawfile',
                self.rev,
                fn,
            ])
            return self.request.response.redirect(uri)
        else:
            self.workspace_uri = '/'.join([
                self.context.absolute_url(), 
                'workspace', 
                self.workspace,
                '@@file',
                self.rev,
            ])
            # search
            catalog = getToolByName(self.context, 'portal_catalog')
            self.related_exposures = catalog(
                pmr2_exposure_workspace=self.workspace)
            # no border in this case.
            self.request['disable_border'] = True
            return super(RootFolderListing, self).__call__()

    def label(self):
        return u'Model has been moved.'
