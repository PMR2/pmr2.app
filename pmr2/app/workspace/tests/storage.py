import os
from os.path import join
from os.path import dirname
from os.path import relpath
from glob import glob

from datetime import datetime
from cPickle import dumps
import zope.interface

from pmr2.app.workspace.interfaces import IWorkspace
from pmr2.app.workspace.exceptions import *

from pmr2.app.workspace.storage import StorageUtility
from pmr2.app.workspace.storage import BaseStorage
from pmr2.app.workspace.storage import ProtocolResult


def readfile(fn):
    fd = open(fn)
    result = fd.read()
    fd.close()
    return result

test_png = readfile(join(dirname(__file__), 'test.png'))


class DummyStorageUtility(StorageUtility):

    title = u'Dummy'
    command = u'dummy'
    clone_verb = u'clone'

    _dummy_storage_data = {

        'test': [
            {
                'file1': 'file1-rev0\nThis is a test.\n',
                'file2': 'file2-rev0\nThis is also a test.\n',
            },
            {
                'file1': 'file1-rev1\nThis test has changed.\n',
                'file2': 'file2-rev1\nThis is also a test.\n',
                'file3': 'A new test file.\n',
            },
            {
                'file2': 'file2-rev1\nThis is also a test.\n',
                'file3': 'Yes file1 is removed\n',
                'dir1/f1': 'first file in dir1\n',
                'dir1/f2': 'second file in dir1\n',
            },
            {
                'file1': 'file1-rev1\nThis file re-added.\n',
                'file3': 'Yes file1 is removed\n',
                'dir1/f1': 'first file in dir1\n',
                'dir1/f2': 'second file in dir1\n',
                'dir1/dir2/f1': 'first file in dir2\n',
                'dir1/dir2/f2': 'second file in dir2\n',
                'dir1/nested/file': 'some three level deep file\n',
            },
        ],

        'cake': [
            {
                'null': '\0',
                'status': 'is a lie.',
                'test.png': test_png,
                'test.xml':
                    '<?xml version="1.0"?>\n'
                    '<ex xmlns="http://ns.example.com/">\n'
                    '  <node>Some text</node>\n'
                    '</ex>\n',
                'dir1/dir2/file.xml':
                    '<?xml version="1.0"?>\n'
                    '<ex xmlns="http://ns.example.com/">\n'
                    '  <node>Some file</node>\n'
                    '</ex>\n',
            },
            {
                'null': '\0',
                'status': 'is a lie.',
                'test.png': test_png,
                'test.xml':
                    '<?xml version="1.0"?>\n'
                    '<ex xmlns="http://ns.example.com/">\n'
                    '  <node>Some text</node>\n'
                    '</ex>\n',
                'dir1/dummy.txt': 'Dummy txt file\n',
                'dir1/dir2/file.xml':
                    '<?xml version="1.0"?>\n'
                    '<ex xmlns="http://ns.example.com/">\n'
                    '  <node>Some file</node>\n'
                    '</ex>\n',
            },
        ],

        'blank': [
            {
            },
        ],

        'external_root': [
            {
                'readme': 'external test root.\n',
                'external_test': {
                    '': '_subrepo',
                    'rev': '0',
                    'location': 'http://nohost/plone/workspace/external_test',
                },
            },
        ],

        'external_test': [
            {
                'test.txt': 'external test file.\n',
            },
        ],

    }

    title = 'Dummy Storage'
    valid_cmds = ['revcount', 'update',]

    def create(self, context):
        # creates the datastore for a dummy storage
        if context.id in self._dummy_storage_data:
            # don't overwrite existing data
            return
        self._dummy_storage_data[context.id] = [{}]

    def acquireFrom(self, context):
        return DummyStorage(context)

    def validateExternalURI(self, uri):
        # Nothing sensitive here, nope.
        return True

    def isprotocol(self, request):
        return request.form.get('cmd', None) is not None

    def protocol(self, context, request):
        storage = self.acquireFrom(context)
        cmd = request.form.get('cmd', '')
        if cmd == 'revcount':
            return ProtocolResult(str(len(storage._data())), None)
        elif cmd == 'update':
            # doesn't do anything, but check that the request is indeed
            # a push
            if request.method == 'GET':
                raise Exception('bad request method')
            return ProtocolResult('Updated', 'push')
        raise UnsupportedCommandError('%s unsupported' % cmd)

    def syncIdentifier(self, context, identifier):
        # as this is a local test, we are not going to bother with going
        # over any kind of protocol.  Resolve workspace at path:

        # This is also a more advance version where we make use of the
        # path if it's available.
        id_ = context.id
        if hasattr(context, 'getPhysicalPath'):
            id_ = context.getPhysicalPath()
        self._dummy_storage_data[id_] = self._dummy_storage_data[identifier]
        return True, None

    def syncWorkspace(self, context, source):
        identifier = source.id
        return self.syncIdentifier(context, identifier)

    def _loadDir(self, id_, root):
        def readfile(fullpath):
            with open(fullpath) as fd:
                c = fd.read()
            return c

        result = [
            {
                relpath(join(r, f), p): readfile(join(r, f))
                    for r, _, files in os.walk(p)
                        for f in files
            }
            for p in sorted(glob(join(root, '*')))
        ]

        self._dummy_storage_data[id_] = result



class LegacyDummyStorageUtility(DummyStorageUtility):
    """
    Emulate the legacy protocol "naked" result.
    """

    def protocol(self, context, request):
        return DummyStorageUtility.protocol(self, context, request).result


class DummyStorage(BaseStorage):

    _archiveFormats = {
        'dummy': ('Dummy Archive', '.dummy', 'application/x-dummy'),
    }
    
    def __init__(self, context):
        self.context = context
        self.__id = context.id
        self.checkout()

    def _datetime(self, rev=None):
        i = rev
        if rev is None:
            i = self.__rev
        ts = datetime.utcfromtimestamp(i * 9876 + 1111111111 + 46800)
        return ts.strftime(self.datefmtstr)

    def _data(self):
        rawdata = DummyStorageUtility._dummy_storage_data
        if hasattr(self.context, 'getPhysicalPath') and \
                self.context.getPhysicalPath() in rawdata:
            return rawdata[self.context.getPhysicalPath()]
        return rawdata[self.__id]

    def _changeset(self, rev=None):
        if rev is None:
            rev = self.__rev

        try:
            return self._data()[rev]
        except IndexError:
            raise RevisionNotFoundError()

    def _dirinfo(self, path):
        contents = lambda: self.listdir(path)
        return self.format(**{
            'author': '',
            'desc': '',
            'permissions': 'drwxr-xr-x',
            'node': self.rev,
            'date': '',
            'size': '',
            'path': path,
            'contents': contents,
        })

    def _validrev(self, rev):
        # valid type
        if not isinstance(rev, (int, basestring)):
            raise RevisionNotFoundError()
        # valid value
        try:
            rev = int(rev)
        except:
            raise RevisionNotFoundError()
        # valid revision
        self._changeset(rev)
        return rev

    @property
    def rev(self):
        return str(self.__rev)

    def archive_dummy(self):
        return dumps(self._changeset())

    def basename(self, path):
        return path.split('/')[-1]

    def checkout(self, rev=None):
        # set current revision
        if rev is None:
            rev = len(self._data()) - 1
        self.__rev = self._validrev(rev)

    def files(self):
        result = self._changeset().keys()
        result.sort()
        return result

    def file(self, path):
        try:
            return self._changeset()[path]
        except KeyError:
            # check if the first element resolves into a "subrepo"
            frags = path.split('/')
            if len(frags) > 1:
                result = self.file(frags[0])
                if isinstance(result, dict):
                    # only allow "subrepos"
                    return result
            raise PathNotFoundError()

    def fileinfo(self, path):
        result = self.file(path)
        if not isinstance(result, basestring):
            # assume dict, format external result
            keys = {'path': '/'.join(path.split('/')[1:])}
            keys.update(result)
            return self.format_external(path, keys)

        # this is done because contents may not be needed at all times
        contents = lambda: self.file(path)
        return self.format(**{
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'desc': '',
            'permissions': '-rw-r--r--',
            'node': self.rev,
            'date': self._datetime(),
            'size': str(len(result)),
            'path': path,
            'contents': contents,
        })

    def format_external(self, path, keys):
        return self.format(**{
            'permissions': 'lrwxrwxrwx',
            'contenttype': None,  # XXX unnecessary for now
            'node': self.rev,
            'date': '',
            'size': '',
            'path': path,
            'desc': '',
            'contents': '',
            'external': keys,
        })

    def listdir(self, path):
        # root is '', zero length
        try:
            self.file(path)
            # we have a file, not a directory
            raise PathNotDirError()
        except PathNotFoundError:
            # check to see if path is a directory in a bit
            pass
        except:
            # raise other exceptions
            raise
        parts = tuple([p for p in path.split('/') if p])
        length = len(parts)

        depth = len(parts) + 1
        # probably don't have to do this for every single one, but this
        # makes the algorithm a bit easier to understand.
        fileparts = [tuple(f.split('/')) for f in self.files()]
        fileparts = [f for f in fileparts if f[:length] == parts]
        if not fileparts:
            # not a single fragment was found.
            raise PathNotFoundError
        dirs = set()
        files = []
        for f in fileparts:
            if len(f) > depth:
                # nested too deep, but we should record the fragment up
                # to the depth.
                dirs.add(f[:depth])
                continue
            # we can add info for this file
            files.append(self.fileinfo('/'.join(f)))

        # finish processing dirs
        dirs = list(dirs)
        dirs.sort()
        results = [self._dirinfo('/'.join(d)) for d in dirs]
        results.extend(files)
        return results

    def _logentry(self, rev):
        if rev < 0:
            return
        if rev == 0:
            files = self._changeset(0).keys()
            files.sort()
            return '\n'.join(['A:%s' % i for i in files])

        newcs = self._changeset(rev)
        oldcs = self._changeset(rev - 1)
        results = []
        files = set(oldcs.keys() + newcs.keys())

        for f in files:
            if f not in oldcs:
                results.append('A:%s' % f)
            elif f not in newcs:
                results.append('D:%s' % f)
            elif not oldcs[f] == newcs[f]:
                results.append('C:%s' % f)

        results.sort()
        return '\n'.join(results)

    def log(self, start, count, branch=None, *a, **kw):
        def buildnav(nav):
            # mock navigation
            result = []
            for i in xrange(1, nav+1):
                result.append(
                    {
                        'href': 'p%d' % i,
                        'label': 'page %d' % i,
                    }
                )
            return result

        start = self._validrev(start)
        results = []
        for i in xrange(start, start - count, -1):
            # the keys are based on mercurial.hgweb
            entry = self._logentry(i)
            if not entry:
                break
            results.append({
                'node': str(i),
                'date': self._datetime(i),
                'author': 'pmr2.teststorage <pmr2.tester@example.com>',
                'desc': entry,
            })
        self._lastnav = buildnav(2)
        return results


class DummyWorkspace(object):
    """\
    To avoid dealing with the vocab and the rest of Plone Archetypes.
    """

    zope.interface.implements(IWorkspace)

    def __init__(self, id_):
        self.id = id_
        self.storage = None

    def restrictedTraverse(self, path):
        # dummy
        return DummyWorkspace(path)
