import zope.interface
from zope.annotation.interfaces import IAnnotations
from zope.annotation import factory
from zope.location import Location, locate
from pmr2.app.interfaces import INamedUtilBase
from pmr2.app.annotation.interfaces import IExposureFileNote

PREFIX = 'pmr2.annotation.notes-'

def note_factory(klass, key):
    """\
    Named Annotation Factory maker specific for PMR2 annotations
    """

    key = PREFIX + key
    return factory(klass, key)

def get_annotated(context):
    # in the future we may want to work directly on the __annotation__ 
    # attribute to get back a generator based on the PREFIX instead.

    items = [i for i in IAnnotations(of).items() 
        if IExposureFileNote.providedBy(i[1])]
    return items

def del_note(context, key):
    # purges ExposureFileNotes
    ann = IAnnotations(context)
    k = PREFIX + key
    if k in ann and IExposureFileNote.providedBy(ann[k]):
        del ann[k]

def rebuild_note(context):
    """\
    Cleans up exposure file notes.
    """

    if not IExposureFile.providedBy(context):
        raise TypeError('context does not provide IExposureFile')

    # Get all annotations that provides IExposureFileNote
    annotations = IAnnotation(context)

    # XXX save data first

    # delete

    for key in annotations.keys():
        if IExposureFileNote.providedBy(annotations[key]):
            del annotations[key]
    
    # recreate data
