import zope.interface
import zope.schema
from pmr2.app.annotation.note import ExposureFileEditableNoteBase


class IEditedNote(zope.interface.Interface):

    note = zope.schema.TextLine(
        title=u'Note',
        description=u'A simple note for this file.',
    )


class EditedNote(ExposureFileEditableNoteBase):

    zope.interface.implements(IEditedNote)
    note = zope.schema.fieldproperty.FieldProperty(IEditedNote['note'])


class IPostEditedNote(zope.interface.Interface):

    chars = zope.schema.Int(
        title=u'Characters',
        description=u'Number of characters to copy from the source file.',
    )

    text = zope.schema.Text(
        title=u'Text',
        description=u'Stores the characters captured from the source file.',
    )


class PostEditedNote(ExposureFileEditableNoteBase):

    zope.interface.implements(IPostEditedNote)
    chars = zope.schema.fieldproperty.FieldProperty(IPostEditedNote['chars'])
    text = zope.schema.fieldproperty.FieldProperty(IPostEditedNote['text'])
