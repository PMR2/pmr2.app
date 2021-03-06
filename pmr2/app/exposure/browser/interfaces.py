import zope.schema
import zope.interface

from pmr2.app.workspace.schema import StorageFileChoice


class IExposureFileGenForm(zope.interface.Interface):
    """\
    Interface for the form that will handle the generation of an
    ExposureFile object.
    """

    filename = StorageFileChoice(
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

    docview_gensource = StorageFileChoice(
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

    # XXX these should be some sort of radio choice; while I have used
    # the table with the custom radio columns, it will be nice to figure
    # out how to integrate the values acquired from there onto some
    # vocabulary that can be placed here.

    commit_id = zope.schema.TextLine(
        title=u'Commit ID',
    )

    exposure_path = zope.schema.ASCIILine(
        title=u'Exposure Path',
        description=u'Absolute path to the exposure object.',
    )


class ICreateExposureForm(zope.interface.Interface):
    """\
    Interface for the CreateExposureForm.
    """


class ICreateExposureGroup(zope.interface.Interface):
    """\
    Interface for the groups for the above form.
    """

    def acquireStructure():
        """\
        CreateExposureForm will call this method on successful creation
        of an exposure, and will use this method to acquire the data
        that will become the initial structure for the wizard.
        """


class IExposureExportImportGroup(zope.interface.Interface):
    """\
    Interface for the form that will handle the generation of an
    ExposureFile object.
    """

    export_uri = zope.schema.ASCIILine(
        title=u'Exposure Export URI',
        description=u'URI of an exported exposure structure, if importing '
                     'from an external PMR2 instance.  This URI can be found '
                     'at the `wizard` tab of the exposure you wish to import '
                     'from.',
        required=False,
    )


class IExposureViewGenGroup(zope.interface.Interface):
    """\
    Group for the root documentation generation.
    """

    docview_generator = zope.schema.Choice(
        title=u'View Generator',
        description=u'The selected generator will be used to generate the '
                     'text and/or view for the exposure index, or the root '
                     'documentation view.',
        vocabulary='pmr2.vocab.DocViewGen',
        required=False,
    )

    docview_gensource = StorageFileChoice(
        title=u'Generator Source',
        description=u'The source for the above generator.  The selected file '
                     'must be compatible with the selected generator.',
        vocabulary='pmr2.vocab.manifest',
        required=False,
    )


class IExposureFileChoiceTypeGroup(zope.interface.Interface):
    """\
    Interface with fields for filename and type.
    """

    filename = StorageFileChoice(
        title=u'File',
        description=u'The file within the workspace that requires special '
                     'processing to be presentable in this exposure.',
        vocabulary='pmr2.vocab.manifest',
        required=False,
    )

    filetype = zope.schema.Choice(
        title=u'File Type',
        description=u'Select the appropriate type for this file if one had '
                     'been defined.  Will override the choices below.',
        vocabulary='pmr2.vocab.eftype',
        required=False,
    )


class IExposureWizardForm(zope.interface.Interface):
    """
    Marker for Exposure Wizard Form.
    """
