PMR2 Interfaces
===============

This is the interface to the root repository object.

    >>> import pmr2.app.interfaces
    >>> from pmr2.app.interfaces import IRepositoryRoot
    >>> type(IRepositoryRoot.get('title'))
    <class 'zope.schema._bootstrapfields.TextLine'>
    >>> type(IRepositoryRoot.get('repo_root'))
    <class 'zope.schema._bootstrapfields.TextLine'>

Test out the form.

    >>> from plone.z3cform.tests import setup_defaults
    >>> setup_defaults()

    >>> import z3c.form.testing
    >>> from pmr2.app import browser
    >>> request = z3c.form.testing.TestRequest()
    >>> add_form = browser.RepositoryRootAddForm(None, request)
    >>> html = add_form()
    >>> 'Title' in html
    True
    >>> 'Description' in html
    True
    >>> 'repo_root' in html
    True

