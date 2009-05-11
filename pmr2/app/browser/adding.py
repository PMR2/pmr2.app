from zope.app import zapi

import Products.Five.browser.adding


class Adding(Products.Five.browser.adding.Adding):

    def addPMR2Search(self):
        redir = zapi.absoluteURL(self.context, self.request
                                ) + '/@@pmr2search_add_form'
        self.request.response.redirect(redir)

    def addWorkspace(self):
        redir = zapi.absoluteURL(self.context, self.request
                                ) + '/@@workspace_create'
        self.request.response.redirect(redir)
