from pmr2.app.exposure.interfaces import IExposure, IExposureFolder

def catalog_content(obj, event):
    # for the subscriber event.
    obj.reindexObject()

def recursive_recatalog_content(obj, event):
    # for exposure state changes.
    # we are going to be restrictive in what we do.
    obj.reindexObject()
    if IExposure.providedBy(obj) or IExposureFolder.providedBy(obj):
        for id_, subobj in obj.items():
            recursive_recatalog_content(subobj, event)
