import zope.schema
import zope.interface
import zope.publisher.interfaces
from plone.theme.interfaces import IDefaultPloneLayer
from plone.z3cform.interfaces import IFormWrapper

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from pmr2.app.schema import ObjectId
from pmr2.app.content.interfaces import *


class IUpdatablePageView(zope.interface.Interface):
    """\
    Interface for the Workspace action menu.
    """

    def update():
        """
        Method call to update the internal structure before the view
        is rendered.
        """


class IWorkspaceActionsViewlet(zope.interface.Interface):
    """\
    Interface for the Workspace action menu.
    """


class IWorkspaceFilePageView(IUpdatablePageView):
    """\
    Interface for the Workspace action menu.
    """


class IThemeSpecific(IDefaultPloneLayer):
    """\
    Marker interface that defines a Zope 3 browser layer.
    """


class IPlainLayoutWrapper(IFormWrapper):
    """\
    Interface for the plain layout wrapper.
    """


class IPloneviewLayoutWrapper(IFormWrapper):
    """\
    Interface for the Ploneview layout wrapper.
    """


class IMathMLLayoutWrapper(IFormWrapper):
    """\
    Interface for the MathML layout wrapper.
    """


class IPublishTraverse(zope.publisher.interfaces.IPublishTraverse):
    """\
    Our specialized traversal class with specifics defined.
    """

    traverse_subpath = zope.schema.List(
        title=u'Traverse Subpath',
        description=u'A list of traversal subpaths that got captured.',
    )


class IObjectIdMixin(zope.interface.Interface):
    """\
    For use by any interface that will be used by AddForm; this
    basically gives an 'id' field for the user to input.
    """

    id = ObjectId(
        title=u'Id',
        description=u'The identifier of the object, used for URI.',
    )


class IPMR2Add(IObjectIdMixin, IPMR2):
    """\
    Interface for the use by PMR2AddForm.
    """


class IWorkspaceAdd(IObjectIdMixin, IWorkspace):
    """\
    Interface for the use by WorkspaceAddForm.
    """


class IWorkspaceStorageCreate(IWorkspaceAdd):
    """\
    Interface for the use by WorkspaceStorageCreateForm.
    """

    # We customized the id so validator can discrimate this against
    # the generate mixin id field.
    id = ObjectId(
        title=u'Id',
        description=u'The identifier of the object, used for URI.',
    )


class IWorkspaceBulkAdd(zope.interface.Interface):
    """\
    Interface for the use by WorkspaceAddForm.
    """

    workspace_list = zope.schema.Text(
        title=u'List of Workspaces',
        description=u'List of Mercurial Repositories created by pmr2_mkhg ' \
                     'that are already moved into the workspace directory.',
        required=True,
    )


class IPMR2SearchAdd(IObjectIdMixin, IPMR2Search):
    """\
    Interface for the use by PMR2AddForm.
    """


class IExposureFileGenForm(zope.interface.Interface):
    """\
    Interface for the form that will handle the generation of an
    ExposureFile object.
    """

    filename = zope.schema.Choice(
        title=u'File',
        description=u'The file within the workspace that requires special '\
                     'processing to be presentable in this exposure.',
        vocabulary='ManifestListVocab',
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
        vocabulary='ExposureFileAnnotatorVocab',
        required=True,
    )


class IExposureFileNoteEditForm(zope.interface.Interface):
    """\
    Interface for the note edit form.
    """

    # Lacking fields here because we don't have any fixed fields yet,
    # not to mention the fields are dynamically acquired from the name
    # of the note which is passed into via traversal subpath.


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
        vocabulary='ManifestListVocab',
        required=False,
    )

    docview_generator = zope.schema.Choice(
        title=u'View Generator',
        description=u'The selected generator will be used to attempt to ' \
                     'generate text for the default document view.',
        vocabulary='DocViewGenVocab',
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


