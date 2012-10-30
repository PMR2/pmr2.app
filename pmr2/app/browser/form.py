import zope.deprecation

try:
    from pmr2.z3cform.form import Form
    zope.deprecation.deprecated('Form', 
        'Form has been moved to pmr2.z3cform.form.  '
        'Please update the import location before pmr2.app-0.7')
except ImportError:
    pass

try:
    from pmr2.z3cform.form import DisplayForm
    zope.deprecation.deprecated('DisplayForm', 
        'DisplayForm has been moved to pmr2.z3cform.form.  '
        'Please update the import location before pmr2.app-0.7')
except ImportError:
    pass

try:
    from pmr2.z3cform.form import AuthenticatedForm
    zope.deprecation.deprecated('AuthenticatedForm', 
        'AuthenticatedForm has been moved to pmr2.z3cform.form.  '
        'Please update the import location before pmr2.app-0.7')
except ImportError:
    pass

try:
    from pmr2.z3cform.form import PostForm
    zope.deprecation.deprecated('PostForm', 
        'PostForm has been moved to pmr2.z3cform.form.  '
        'Please update the import location before pmr2.app-0.7')
except ImportError:
    pass

try:
    from pmr2.z3cform.form import AddForm
    zope.deprecation.deprecated('AddForm', 
        'AddForm has been moved to pmr2.z3cform.form.  '
        'Please update the import location before pmr2.app-0.7')
except ImportError:
    pass

try:
    from pmr2.z3cform.form import EditForm
    zope.deprecation.deprecated('EditForm', 
        'EditForm has been moved to pmr2.z3cform.form.  '
        'Please update the import location before pmr2.app-0.7')
except ImportError:
    pass

try:
    from pmr2.z3cform.form import Group
    zope.deprecation.deprecated('Group', 
        'Group has been moved to pmr2.z3cform.form.  '
        'Please update the import location before pmr2.app-0.7')
except ImportError:
    pass
