import re

import zope.component
from paste.httpexceptions import HTTPNotFound

import z3c.form.field
import z3c.form.form

from plone.z3cform import layout

from Products.CMFCore.utils import getToolByName

from pmr2.app.interfaces import *
from pmr2.app.content import *
from pmr2.app.browser.interfaces import *

from pmr2.app.browser import form
from pmr2.app.browser import exposure
from pmr2.app.browser import page
from pmr2.app.browser.page import ViewPageTemplateFile
from pmr2.app.browser import widget


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
