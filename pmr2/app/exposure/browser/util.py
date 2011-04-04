import zope.interface
import zope.component

from pmr2.app.annotation.interfaces import IExposureFileEditableNote

def fieldvalues(obj):
    inf = zope.interface.providedBy(obj).interfaces().next()
    # XXX no error notification on missing fields.
    return dict([(fn, getattr(obj, fn, None)) for fn in inf.names()])

def viewinfo(obj):
    # maybe make this into generator in the future.
    v = []
    for vname in obj.views:
        note = zope.component.queryAdapter(obj, name=vname)
        if not note:
            # We can't export this
            # do we need error reporting? the actual page
            # is probably broken...
            continue
        if not IExposureFileEditableNote.providedBy(note):
            # assuming standard note, just get none.
            v.append((vname, None,))
            continue
        # this should be editable, grab the fields, build
        # dictionary.
        # XXX see: ExposureFileNoteEditForm

        v.append((vname, fieldvalues(note),))
    return v
