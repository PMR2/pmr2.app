import zope.interface
import zope.component
from zope.app.component.hooks import getSite

import z3c.form.interfaces

from AccessControl import getSecurityManager, Unauthorized
from Products.CMFCore import permissions
from Products.statusmessages.interfaces import IStatusMessage

from pmr2.idgen.interfaces import IIdGenerator

from pmr2.app.annotation.interfaces import IExposureFileEditableNote
from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.app.exposure.interfaces import *


__all__ = [
    'fieldvalues',
    'viewinfo',
    'restrictedGetExposureContainer',
    'getGenerator',
]

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

def restrictedGetExposureContainer():
    # If there is a way to "magically" anchor this form at the
    # target exposure container rather than the workspace, this
    # would be unnecesary.
    settings = zope.component.queryUtility(IPMR2GlobalSettings)
    site = getSite()
    exposure_container = site.restrictedTraverse(
        str(settings.default_exposure_subpath), None)
    if exposure_container is None:
        # assume lack of permission.
        raise Unauthorized('No permission to make exposures.')
    security = getSecurityManager()
    if not security.checkPermission(permissions.AddPortalContent, 
            exposure_container):
        raise Unauthorized('No permission to make exposures.')
    return exposure_container

def getGenerator(form):
    # Using default id generator as specified by global settings. 
    # Will need to change this if exposure containers can specify
    # its own id generation scheme.
    settings = zope.component.queryUtility(IPMR2GlobalSettings)
    name = settings.default_exposure_idgen
    idgen = zope.component.queryUtility(IIdGenerator, name=name)
    if idgen is None:
        status = IStatusMessage(form.request)
        status.addStatusMessage(
            u'The exposure id generator `%s` cannot be found; '
            'please contact site administrator.' % name, 'error')
        raise z3c.form.interfaces.ActionExecutionError(
            ExposureIdGeneratorMissingError())
    return idgen

