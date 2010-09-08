import zope.schema
import zope.interface

from pmr2.app.schema import ObjectId, WorkspaceList, CurationDict, TextLineList


class IExposureContainer(zope.interface.Interface):
    """\
    Container for all exposure pages.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        default=u'Exposure',
    )


class IExposureObject(zope.interface.Interface):
    """\
    Any object within an exposure need to implement this.
    """


class IExposure(zope.interface.Interface):
    """\
    Container for all exposure pages.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        required=False,
    )

    workspace = zope.schema.TextLine(
        title=u'Workspace',
        description=u'The model workspace this exposure encapsulates.',
    )

    commit_id = zope.schema.TextLine(
        title=u'Commit ID',
        description=u'The specific commit identifier of the model.',
    )

    curation = CurationDict(
        title=u'Curation',
        description=u'Curation of this model.',
        required=False,
    )

    # this is not a Choice because the manifest list generation can be
    # a performance hit as this object gets hit a lot, and we don't have
    # caching yet... not to mention users won't be changing this.
    docview_gensource = zope.schema.TextLine(
        title=u'Generated From',
        description=u'The source file which the documentation or data is '
                     'generated from.',
        required=False,
    )

    # sometimes generator can become depcrecated and removed, thus no
    # longer in the vocabulary, plain text field again.
    docview_generator = zope.schema.TextLine(
        title=u'Generator Name',
        description=u'The name of the generator used to make this view.',
        required=False,
    )


class IExposureFolder(zope.interface.Interface):
    """\
    Interface for a folder within an exposure (supports unknwon subpath
    capturing for redirection to path within its workspace).
    """

    # for reason why these two fields are TextLine, please see IExposure
    docview_gensource = zope.schema.TextLine(
        title=u'Generated From',
        description=u'The source file which the documentation or data is '
                     'generated from.',
        required=False,
    )

    docview_generator = zope.schema.TextLine(
        title=u'Generator Name',
        description=u'The name of the generator used to make this view.',
        required=False,
    )


class IExposureFile(zope.interface.Interface):
    """\
    Interface for a basic exposure page.

    This has the use_view field because the default document view may
    not be enough to describe/visualize the data present.
    """

    views = TextLineList(
        title=u'Views',
        description=u'List of views available.',
        required=False,
        default=[],
    )

    file_type = zope.schema.ASCIILine(
        title=u'File Type',
        description=u'The path to the ExposureFileType that was used to '
                     'generate this file.',
        required=False,
    )

    docview_gensource = zope.schema.TextLine(
        title=u'Documentation File',
        description=u'The file where the documentation for this file reside '
                     'in, for files that do not have any method of specifying '
                     'one.',
        required=False,
    )

    docview_generator = zope.schema.TextLine(
        title=u'Documentation Generator',
        description=u'The documentation generator utility that was used to ' \
                     'generate the contents viewed via document_view.',
        required=False,
    )

    selected_view = zope.schema.TextLine(
        title=u'Selected View',
        description=u'Use this view as default instead of the generated ' \
                     'by the generator.',
        required=False,
    )


class IExposureFileRawText(zope.interface.Interface):
    """\
    Interface that will allow the returning of raw text.
    """

    def raw_text():
        """\
        returns a raw text representation of this adapter.
        """


class IExposureFileType(zope.interface.Interface):
    """\
    Profile to use for Exposure File Views.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        required=False,
    )

    views = TextLineList(
        title=u'Views',
        description=u'The list of views to be created.',
        required=False,
        default=[],
    )

    select_view = zope.schema.TextLine(
        title=u'Select View',
        description=u'If defined, select this view if the generation is '
                     'successful.',
        required=False,
    )

    tags = TextLineList(
        title=u'Tags',
        description=u'List of tags to be assigned to this file.',
        required=False,
        default=[],
    )


# Browser interfaces

class IExposureFileGenForm(zope.interface.Interface):
    """\
    Interface for the form that will handle the generation of an
    ExposureFile object.
    """

    filename = zope.schema.Choice(
        title=u'File',
        description=u'The file within the workspace that requires special '\
                     'processing to be presentable in this exposure.',
        vocabulary='pmr2.vocab.manifest',
    )   # this will become the id of an ExposureFile object.


class IExposureFileAnnotatorForm(zope.interface.Interface):
    """\
    Interface for the form and utility that that allows notes to be
    annotated to the ExposureFile.
    """

    annotators = zope.schema.Choice(
        title=u'Annotators Available',
        description=u'The selected annotators will annotate the current ' \
                     'file and enable the view.',
        vocabulary='pmr2.vocab.ExposureFileAnnotators',
        required=True,
    )


class IExposureFileTypeChoiceForm(zope.interface.Interface):
    """\
    Interface for the form and utility that that allows notes to be
    annotated to the ExposureFile based on an ExposureFileType
    """

    eftypes = zope.schema.Choice(
        title=u'File Type',
        description=u'Select the appropriate type for this file if one had '
                     'been defined.  Will override the choices below.',
        vocabulary='pmr2.vocab.eftype',
        required=False,
    )

    annotators = zope.schema.Set(
        title=u'Annotators Enabled',
        description=u'The selected views will be enabled if the data has been '
                     'generated its annotator.',
        value_type=zope.schema.Choice(
            vocabulary='pmr2.vocab.ExposureFileAnnotators',
        ),
        required=False,
    )


class IExposureFileNoteEditForm(zope.interface.Interface):
    """\
    Interface for the note edit form.
    """

    # Lacking fields here because we don't have any fixed fields yet,
    # not to mention the fields are dynamically acquired from the name
    # of the note which is passed into via traversal subpath.


class IExposureFileView(zope.interface.Interface):
    """\
    Interface that will view an exposure file.  Usually they will need/
    acquire an ExposureFileNote object, and this is a marker interface
    that will assist in doing so.
    """


class IExposureDocViewGenForm(zope.interface.Interface):
    """\
    For the form and utility that handles the generation of the text for
    the ExposureFile default document_view.
    """

    docview_gensource = zope.schema.Choice(
        title=u'Documentation File',
        description=u'The file where the documentation resides in.  If this '
                     'object is already a file, leaving this field unselected '
                     'means the current file will provide the data from which '
                     'the document will be generated from.',
        vocabulary='pmr2.vocab.manifest',
        required=False,
    )

    docview_generator = zope.schema.Choice(
        title=u'View Generator',
        description=u'The selected generator will be used to attempt to ' \
                     'generate text for the default document view.',
        vocabulary='pmr2.vocab.DocViewGen',
        required=False,
    )


class IExposureFileSelectView(zope.interface.Interface):
    """\
    Exposure files now have the option to select a generated view as the
    default view that will be presented to users.
    """

    views = zope.schema.List(
        title=u'Views',
        required=False,
    )

    selected_view = zope.schema.Choice(
        title=u'Selected View',
        description=u'If specified, the selected note will be used as the '
                     'landing page for this file, instead of the generated '
                     'default view.',
        vocabulary='pmr2.vocab.ExposureFileNotesAvailable',
        required=False,
    )


class IExposureRolloverForm(zope.interface.Interface):
    """
    """

    # XXX this should be some sort of radio choice, but I haven't
    # figured out how to integrate the radio widgets with the table.

    commit_id = zope.schema.TextLine(
        title=u'Commit ID'
    )

    exposure_id = zope.schema.TextLine(
        title=u'Exposure ID'
    )


