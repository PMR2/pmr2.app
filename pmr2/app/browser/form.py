import os.path

import zope.deprecation
from plone.z3cform.interfaces import IForm, IWrappedForm
from plone.z3cform.templates import ZopeTwoFormTemplateFactory

from pmr2.app.interfaces import IPMR2AppLayer
import pmr2.app.browser

path = lambda p: os.path.join(os.path.dirname(pmr2.app.browser.__file__), 
                              'templates', p)

wrapped_form_factory = ZopeTwoFormTemplateFactory(path('wrapped_form.pt'),
    form=IWrappedForm, request=IPMR2AppLayer)

form_factory = ZopeTwoFormTemplateFactory(path('form.pt'), 
    form=IForm, request=IPMR2AppLayer)

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
