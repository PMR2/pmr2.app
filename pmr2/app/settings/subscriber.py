import zope.component
from pmr2.app.settings.interfaces import IPMR2GlobalSettings


def object_delete_cleanup_dir(obj, event):
    settings = zope.component.queryUtility(IPMR2GlobalSettings)
    settings.orphanDir(obj)
