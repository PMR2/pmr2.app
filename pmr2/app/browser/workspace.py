import zope.component

import z3c.form.interfaces
import z3c.form.field
import z3c.form.form
import z3c.form.value

from z3c.form.browser import textarea

import zope.publisher.browser
from plone.app.z3cform import layout

from pmr2.app.interfaces import *
from pmr2.app.content import *

from widget import WorkspaceListingWidgetFactory

import form


class WorkspaceContainerAddForm(form.AddForm):
    """\
    Workspace container add form.
    """

    fields = z3c.form.field.Fields(IWorkspaceContainer).select(
        'title',
    )
    clsobj = WorkspaceContainer

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']

WorkspaceContainerAddFormView = layout.wrap_form(
    WorkspaceContainerAddForm, label="Workspace Container Add Form")


class WorkspaceContainerEditForm(form.EditForm):
    """\
    Workspace Container Edit form
    """

    fields = z3c.form.field.Fields(IWorkspaceContainer).select(
        'title',
    )

# Plone Form wrapper for the EditForm
WorkspaceContainerEditFormView = layout.wrap_form(
    WorkspaceContainerEditForm, label="Workspace Container Management")


class WorkspaceContainerRepoListingForm(z3c.form.form.Form):
    """\
    Workspace Container Edit form
    """

    mode = z3c.form.interfaces.DISPLAY_MODE

    fields = z3c.form.field.Fields(IWorkspaceContainer).select(
        'get_repository_list',
    )
    fields['get_repository_list'].widgetFactory = WorkspaceListingWidgetFactory

# Plone Form wrapper for the EditForm
WorkspaceContainerRepoListingFormView = layout.wrap_form(
    WorkspaceContainerRepoListingForm, label="Workspace Container Management")
