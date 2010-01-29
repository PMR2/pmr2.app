import zope.interface
import zope.schema
from pmr2.app.annotation.note import ExposureFileEditableNoteBase


class IEditedNote(zope.interface.Interface):
    """\
    OpenCell Session Note
    """

    note = zope.schema.TextLine(
        title=u'Note',
        description=u'A simple note for this file.',
    )


class EditedNote(ExposureFileEditableNoteBase):
    """\
    Points to the OpenCell session attached to this file.
    """

    zope.interface.implements(IEditedNote)
    note = zope.schema.fieldproperty.FieldProperty(IEditedNote['note'])

