import zope.schema
import zope.interface

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

# need to be here as we provide the file listing.
from pmr2.app.workspace.schema import StorageFileChoice


class IExposureFileAnnotator(zope.interface.Interface):
    """\
    Interface for the ExposureFile annotation utility, which provides
    automated generation of data to be added to the note.

    It will annotate standard notes, but must not be used to annotate
    editable notes.
    """

    # ef_note is the name/key of storage class to use

    title = zope.schema.Text(
        title=u'Title',
        description=u'Title of this annotator',
        required=False,
    )

    description = zope.schema.Text(
        title=u'Description',
        description=u'A brief note about what this annotator does.',
        required=False,
    )

    for_interface = zope.schema.InterfaceField(
        title=u'For Interface',
        description=u'This annotator is for this interface',
    )

    # we may need an annotator that is defined to NOT have a view, but
    # serve as a "hidden" value store for other views.
    # omit_view = zope.schema.Bool

    # alternately, the view is generated but it should not be listed on
    # the portlet panel.
    # no_view_entry = zope.schema.Bool

    def generate(context):
        """\
        Process the input context to return a list of tuples in the
        form (name, value) where name is the name of the field for the
        respective note class to store the value in.
        """


class IExposureFilePostEditAnnotator(IExposureFileAnnotator):
    """\
    Interface for the ExposureFile annotation utility for editable notes
    that require further automated processing (i.e. notes that had been
    edited (post-edit) to contain data such as preferences).
    """

    edited_names = zope.schema.Set(
        title=u'Names that are edited',
        value_type=zope.schema.ASCIILine(),
    )


class IExposureFileEditAnnotator(IExposureFileAnnotator):
    """\
    Marker interface for the ExposureFile annotation utility for fully 
    editable notes.
    """


class IExposureFileNote(zope.interface.Interface):
    """\
    Interface for notes attached to ExposureFile objects.
    """


class IExposureFileEditableNote(zope.interface.Interface):
    """\
    Interface for notes attached to ExposureFile objects that are 
    editable by users.
    """


class IStandardExposureFile(zope.interface.Interface):
    """\
    An adapter that really isn't one, it just a marker to reuse the
    original context.
    """


class IRawTextNote(zope.interface.Interface):
    """\
    For an annotation adapter to the ExposureFile that will store raw
    text representation generated by its respective annotator.
    """

    text = zope.schema.Text(
        title=u'Text',
        required=False,
    )


class IGroupedNote(zope.interface.Interface):
    """\
    For an annotation adapter to the ExposureFile that will store a
    list of references to other notes.
    """

    active_notes = zope.schema.List(
        title=u'Active Notes',
        description=u'The list of notes that are active at this list of notes',
        default=[],
    )


class IDocViewGen(zope.interface.Interface):
    """\
    For the utilities that will generate the text for the document_view
    of exposure type objects.
    """

    title = zope.schema.Text(
        title=u'Title',
        description=u'Title of this generator',
        required=False,
    )

    description = zope.schema.Text(
        title=u'Description',
        description=u'A brief note about what this generator does.',
        required=False,
    )

    def generateTitle():
        """\
        The method that will generate the title.
        """

    def generateDescription():
        """\
        The method that will generate the description.
        """

    def generateText():
        """\
        The method that will generate the text.
        """


class IDocGenNote(zope.interface.Interface):
    """\
    For the storage of sources and the generator used for the 
    documentation of exposure type objects.
    """

    source = StorageFileChoice(
        title=u'Documentation File',
        description=u'The file where the documentation resides in.  If this '
                     'object is already a file, leaving this field unselected '
                     'means the current file will provide the data from which '
                     'the document will be generated from.',
        vocabulary='pmr2.vocab.manifest',
        required=False,
    )

    generator = zope.schema.Choice(
        title=u'View Generator',
        description=u'The selected generator will be used to attempt to ' \
                     'generate text for the default document view.',
        vocabulary='pmr2.vocab.DocViewGen',
        required=False,
    )


class IExposurePortDataProvider(zope.interface.Interface):
    """\
    Provides generator whenever unknown datatypes are encountered.
    """


class IExposureDocViewGenSourceAdapter(zope.interface.Interface):
    """\
    Specific for DocViewGen, which has one exception case for IExposure
    types.
    """
