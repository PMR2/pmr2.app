import os.path
import plone.z3cform
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
import pmr2.app.browser
from pmr2.app.browser.interfaces import IPlainLayoutWrapper
from pmr2.app.browser.interfaces import IMathMLLayoutWrapper

path = lambda p: os.path.join(os.path.dirname(pmr2.app.browser.__file__), p)

plain_layout_factory = ZopeTwoFormTemplateFactory(
    path('plain_layout.pt'), form=IPlainLayoutWrapper)

mathml_layout_factory = ZopeTwoFormTemplateFactory(
    path('mathml_layout.pt'), form=IMathMLLayoutWrapper)
