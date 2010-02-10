from zope.component import queryUtility, getSiteManager

from pmr2.app.settings import IPMR2GlobalSettings


def create_user_workspace(user, event):
    """\
    Create a user workspace upon user logging in.  Create the dummies.

        >>> import zope.interface
        >>> import zope.component
        >>>
        >>> class User(object):
        ...     def __init__(self, name):
        ...         self.name = name
        ...     def getName(self):
        ...         return self.name
        ...
        >>> class WorkspaceContainer(object):
        ...     def __init__(self, id):
        ...         self.id = id
        ...
        >>> class Settings(object):
        ...     zope.interface.implements(IPMR2GlobalSettings)
        ...     create_user_workspace = True
        ...     workspace = {}
        ...     def createWorkspaceContainer(self, name=None):
        ...         self.workspace[name] = WorkspaceContainer(name)
        ...     def getWorkspaceContainer(self, name=None):
        ...         if name is None:
        ...             return self.workspace
        ...         return self.workspace.get(name, None)
        ...
        >>> settings = Settings()
        >>> zope.component.getSiteManager().registerUtility(settings,
        ...     IPMR2GlobalSettings)
        >>> name = 'tester'
        >>> user = User(name)

    Then call our method.

        >>> create_user_workspace(user, None)
        >>> settings.workspace[name].id
        'tester'

    Should not crash on subsequent calls.

        >>> create_user_workspace(user, None)
        >>> settings.workspace[name].id
        'tester'

    Cleanup.

        >>> zope.component.getSiteManager().unregisterUtility(settings,
        ...     IPMR2GlobalSettings)
        True
    """

    settings = queryUtility(IPMR2GlobalSettings)
    if settings is None or not settings.create_user_workspace:
        return
    workspace = settings.getWorkspaceContainer()
    if workspace is None:
        # toss a warning?
        return
    name = user.getName()
    # check whether it's already created
    userdir = settings.getWorkspaceContainer(name)
    if userdir is not None:
        # already exists, don't do anything, maybe check for type later.
        return

    # create the container
    settings.createWorkspaceContainer(name)
