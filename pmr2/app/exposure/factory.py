from pmr2.app.workspace import factory

class CreateExposure(factory.WorkspaceFileUtility):
    # XXX replace this with the standard actions.xml file once I figure
    # out how to register that directive.  The goal of this is to not
    # hard code this into the workspace class.
    id = 'create-exposure'
    view = 'create_exposure'
    title = u'Create Exposure'
    description = u'Creates an Exposure of this revision of this Workspace.'
