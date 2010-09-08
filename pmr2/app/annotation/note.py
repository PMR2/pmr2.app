import zope.interface
import zope.component
from zope.app.container.contained import Contained
from zope.annotation import factory
from zope.annotation.interfaces import IAnnotations
from zope.schema import fieldproperty
from persistent import Persistent
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName

from pmr2.app.interfaces import *
from pmr2.app.exposure.interfaces import *
from pmr2.app.annotation.interfaces import *
import pmr2.app.util


# Basic support for ExposureFileNote annotation adapters.

class ExposureFileNoteBase(Persistent, Contained):
    """\
    The base class for adapter to ExposureFile objects.  Both parent
    classes are required.
    """

    zope.component.adapts(IExposureFile)
    zope.interface.implements(IExposureFileNote)


class ExposureFileEditableNoteBase(ExposureFileNoteBase):
    """\
    Base class for editable notes.
    """

    zope.interface.implements(IExposureFileEditableNote)


class StandardExposureFile(ExposureFileNoteBase):
    """\
    A dummy of sort that will just reuse the ExposureFile that this
    adapts.
    """

    zope.interface.implements(IStandardExposureFile)

StandardExposureFileFactory = factory(StandardExposureFile)


class RawTextNote(ExposureFileNoteBase):
    """\
    See IRawText interface.
    """

    zope.interface.implements(IRawTextNote)
    text = fieldproperty.FieldProperty(IRawTextNote['text'])

    def raw_text(self):
        return self.text


class GroupedNote(ExposureFileNoteBase):
    """\
    See IGroupedNote interface.
    """

    zope.interface.implements(IGroupedNote)
    active_notes = fieldproperty.FieldProperty(IGroupedNote['active_notes']) 


# Exposure Port adapters

class BaseExposurePortDataProvider(object):
    """\
    The base class for adapter to ExposureFile objects.  Both parent
    classes are required.
    """

    def __init__(self, context):
        self.context = context
