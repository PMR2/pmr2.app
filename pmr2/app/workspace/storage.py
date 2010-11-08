import mimetypes
from magic import Magic
import zope.interface

from pmr2.app.workspace.exceptions import *
from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.interfaces import IStorageUtility


class BaseStorage(object):
    """\
    Basic storage type
    """

    zope.interface.implements(IStorage)

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

    # Default implementation for methods

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
               author='', desc='', *a, **kw):

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
            'file': path,
            'basename': self.basename(path),
            'contents': contents,
            'mimetype': mimetype,
        }

    def listdir(self, path):
        raise NotImplementedError

    def log(self, start, count, branch=None):
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


class StorageUtility(object):
    """\
    Basic storage utility.

    Reason why we have a utility instead of a straight-up adapter to a
    Storage object is two-folds.

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

    def __call__(self, workspace):
        """\
        Converts workspace into a storage object.
        """
        raise NotImplementedError


class BaseStorageAdapter(object):
    """\
    We do need a quick way to adapt any object into its source storage
    mechanism, as not all objects contain reference (name) to its
    storage backend.
    """
