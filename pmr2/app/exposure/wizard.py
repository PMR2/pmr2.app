import zope.component
import zope.interface
from zope.schema import fieldproperty
from zope.app.container.contained import Contained
from zope.annotation.interfaces import IAnnotations
from zope.annotation import factory
from persistent import Persistent

from pmr2.app.workspace.schema import StorageFileChoice
from pmr2.app.exposure.interfaces import IExposure, IExposureWizard


class ExposureWizard(Persistent, Contained):
    """\
    Exposure wizard.
    """

    zope.component.adapts(IExposure)
    zope.interface.implements(IExposureWizard)
    structure = fieldproperty.FieldProperty(IExposureWizard['structure'])

    def updateFromExposure(self):
        """\
        Generate a new structure from the exposure.
        """

        pass

ExposureWizardFactory = factory(ExposureWizard)


class IFileEntry(zope.interface.Interface):
    """\
    Interface for the wizard subform.
    """

    # should omit this by default.
    filename = StorageFileChoice(
        title=u'File',
        description=u'The file within the workspace that requires special '
                     'processing to be presentable in this exposure.',
        vocabulary='pmr2.vocab.manifest',
        required=True,
    )

    filetype = zope.schema.Choice(
        title=u'File Type',
        description=u'Select the appropriate type for this file if one had '
                     'been defined.  Will override the choices below.',
        vocabulary='pmr2.vocab.eftype',
        required=False,
    )


class IDirectoryEntry(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'Title for the object',
        required=False,
    )

    docgen_generator = zope.schema.Choice(
        title=u'View Generator',
        description=u'The selected generator will be used to generate the '
                     'text and/or view for the exposure index, or the root '
                     'documentation view.',
        vocabulary='pmr2.vocab.DocViewGen',
        required=False,
    )

    docgen_source = StorageFileChoice(
        title=u'Generator Source',
        description=u'The source for the above generator.  The selected file '
                     'must be compatible with the selected generator.',
        vocabulary='pmr2.vocab.manifest',
        required=False,
    )


class IViewEntry(zope.interface.Interface):
    """\
    Interface for the wizard subform.
    """

    view_id = zope.schema.TextLine(
        title=u'View ID',
        required=True,
    )

    # fields are determined by the adaptation of the annotator 
    # identified by the view_id
