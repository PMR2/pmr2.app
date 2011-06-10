import zope.schema
import zope.interface

from pmr2.app.schema import ObjectId, WorkspaceList, CurationDict, TextLineList


class IPMR2ExposureLayer(zope.interface.Interface):
    """\
    Marker interface for PMR2 Exposures.
    """


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
        # can't be `None` as the value is directly assigned to a field
        # that cannot accept `None`.
        missing_value=[],
    )
