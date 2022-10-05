from collections import namedtuple
import mimetypes
import urlparse
from magic import Magic
import zope.interface
import zope.component
from zope.component.hooks import getSite
from plone.registry.interfaces import IRegistry

from pmr2.app.workspace.exceptions import *
from pmr2.app.workspace.interfaces import IStorage, IStorageUtility
from pmr2.app.workspace.interfaces import IWorkspace


ProtocolResult = namedtuple('ProtocolResult', ('result', 'event'))


class BaseStorage(object):
    """\
    Basic storage type
    """

    zope.interface.implements(IStorage)

    def __init__(self, context):
        # context will always be the immediate object that leads to the
        # creation of this storage object, or the final object that is
        # resolved.
        # 
        # example 1: if we have an exposure of a workspace, and we adapt
        # an exposure to a storage, its context will be the workspace
        # and not the exposure
        #
        # example 2: if we have an exposure file that sits within an
        # exposure, context will again be the workspace that the 
        # exposure references.
        # 
        # to get to an individual file, just specify the path.

        self.context = context

    # Parameters

    @property
    def rev(self):
        raise NotImplementedError

    @property
    def shortrev(self):
        return self.rev

    # Datetime implementation

    # We assume UTC for all datetime.

    __default_datefmt = {
        'rfc2822': '%a, %d %b %Y %H:%M:%S +0000',
        'rfc3339': '%Y-%m-%dT%H:%M:%SZ',
        'iso8601': '%Y-%m-%d %H:%M:%S',
    }

    __datefmt = 'iso8601'

    # this stores the types of archive available, with its key the 
    # method name with a 3-tuple value that stores the human readable
    # name, file name extension and mimetype.  See tests/storage.py for
    # the example.
    _archiveFormats = {}
    __archiveFormatInfoKeys = ('name', 'ext', 'mimetype')

    def _getDatefmt(self):
        return self.__datefmt

    def _setDatefmt(self, datefmt):
        if datefmt in BaseStorage.__default_datefmt:
            self.__datefmt = datefmt
        else:
            raise ValueError('unsupported datetime format')

    datefmt = property(_getDatefmt, _setDatefmt)

    @property
    def datefmtstr(self):
        return BaseStorage.__default_datefmt[self.datefmt]

    @property
    def builtin_archive_formats(self):
        # should return a list of builtins available, could be
        # automatically generated.
        archiveFormats = {}
        return archiveFormats

    @property
    def archiveFormats(self):
        return sorted(self._archiveFormats.keys() +
            self.builtin_archive_formats.keys())

    # Navigational list

    _lastnav = None

    @property
    def lastnav(self):
        if self._lastnav is None:
            return []
        else:
            return self._lastnav

    # Default implementation for methods

    def archiveInfo(self, format):
        info = self._archiveFormats.get(format,
            self.builtin_archive_formats.get(format, None))
        if not info:
            raise ValueError('format `%s` not supported' % format)
        return dict(zip(self.__archiveFormatInfoKeys, info))

    def archive(self, format):
        archivePrefix = 'archive_'
        if format not in self.archiveFormats:
            raise ValueError('format `%s` not supported' % format)
        archiver = getattr(self, archivePrefix + format, None)
        if not (archiver and callable(archiver)):
            # Well someone screwed up by forgetting to implement the
            # appropriate method with the correct name.
            raise NotImplementedError
        return archiver()

    def basename(self, name):
        raise NotImplementedError

    def checkout(self, rev=None):
        raise NotImplementedError

    def file(self, path):
        raise NotImplementedError

    def fileinfo(self, path):
        raise NotImplementedError

    def files(self):
        raise NotImplementedError

    def format(self, permissions, node, date, size, path, contents,
               contenttype=None, author='', desc='', external=None, *a, **kw):

        # need a way to derive the correct baseview.
        baseview = 'file'

        def mimetype():
            # use the built-in mimetypes, then use magic library
            # XXX performance penalty here getting the entire file?
            # XXX should provide a way to allow other packages to add
            # more mimetypes.
            data = contents()
            if not isinstance(data, basestring):
                return None
            mt = mimetypes.guess_type(path)[0]
            if mt is None or mt.startswith('text/'):
                magic = Magic(mime=True)
                mt = magic.from_buffer(data[:4096])
            return mt

        return {
            'permissions': permissions,
            'author': author,
            'desc': desc,
            'node': node,
            'date': date,
            'size': size,
            'baseview': baseview,
            'file': path,
            'fullpath': None,
            'contenttype': contenttype,
            'basename': self.basename(path),
            'contents': contents,
            'mimetype': mimetype,
            'external': external,
        }

    def listdir(self, path):
        raise NotImplementedError

    def log(self, start, count, branch=None, *a, **kw):
        raise NotImplementedError

    def pathinfo(self, path):
        """\
        This is a default implementation.  If a specific backend 
        supports other types of path resolution, this method can be
        safely overridden provided the correct data is returned.
        """

        try:
            listing = self.listdir(path)
            # consider using an iterator?
            contents = lambda: listing
            data = self.format(**{
                'permissions': 'drwxr-xr-x',
                'node': self.rev,
                'date': '',
                'size': '',
                'path': path,
                'contents': contents,
                'author': '',
                'desc': '',
            })
        except PathNotDirError:
            # then path must be a file
            data = self.fileinfo(path)
        return data

    def roots(self, rev=None):
        raise NotImplementedError

    def clonecmd(self):
        # Default to an empty string to denote a default; the original
        # implementation only has this visible via the portlet, so this
        # tells it to use the default handler.
        return ''

    def resolve_file(self, path):
        """
        This default implementation relies on the underlying file() and
        pathinfo() method in working order, and that the relevant
        registry settings to resolve hostnames for local subrepos be
        available, as this method will not attempt to resolve or fetch
        any external resources hosted outside of this instance.
        """

        def external_file(location, rev, subpath):
            p = urlparse.urlparse(location)
            if not p.netloc in mappings:
                raise SubrepoPathUnsupportedError(
                    'requested path at %r requires subrepo at unsupported '
                    'netloc %r when trying to resolve subpath %r' % (
                        path, p.netloc, subpath))

            objpath = mappings[p.netloc] + p.path
            workspace = portal.restrictedTraverse(objpath.split('/'))
            storage = IStorage(workspace)
            return file(storage, subpath)

        def file(storage, subpath):
            pathinfo = storage.pathinfo(subpath)
            if pathinfo.get('external'):
                external = pathinfo['external']
                return external_file(
                    external['location'], external['rev'], external['path'])
            # Using this instead of contents to ignore directories.
            return storage.file(subpath)

        registry = zope.component.queryUtility(IRegistry)
        if not registry:
            # no registry, so no resolution
            return self.file(path)

        mappings = registry.get('pmr2.app.settings.prefix_maps') or {}
        portal = getSite()
        return file(self, path)


class StorageUtility(object):
    """\
    Basic storage utility.

    Reasons why we have this instead of straight up adapter follows:

    Usage in vocabularies with a context.  The given context may be of a
    type that cannot be adapted into a Storage object.  As the storage
    types are provided globally, it makes more sense to make this a 
    globally available utility.  While the subclass of BaseStorage can
    be used instead, this serves as a more lightweight utility rather
    than registering the implementation of the whole storage class.

    Second, this allows the other classes to subclass Storage without
    worrying about including this for cases where independence from the
    Workspace concept is desired.

    Third, initialization for the base storage class is now independent
    of implementation of the utility.
    """

    zope.interface.implements(IStorageUtility)

    def create(self, context):
        raise NotImplementedError

    def acquireFrom(self, context):
        raise NotImplementedError

    def isprotocol(self, request):
        raise NotImplementedError

    def validateExternalURI(self, uri):
        # hardcoding these as default valid for now.
        validURI = ['http://', 'https://', ]
        for i in validURI:
            if uri.startswith(i):
                return True
        return False

    def protocol(self, context, request):
        raise NotImplementedError

    def syncWorkspace(self, context, workspace):
        raise NotImplementedError

    def syncIdentifier(self, context, identifier):
        raise NotImplementedError

    def sync(self, context, source):
        if IWorkspace.providedBy(source):
            return self.syncWorkspace(context, source)
        return self.syncIdentifier(context, source)

    def __call__(self, context):
        return self.acquireFrom(context)
