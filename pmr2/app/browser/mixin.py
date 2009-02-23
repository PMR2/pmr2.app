from zope.publisher.interfaces import NotFound
import pmr2.mercurial.exceptions


class PMR2MercurialPropertyMixin(object):
    """\
    Concept mixin, not really usable.
    """

    @property
    def storage(self):
        self._storage = self.context.get_storage()
        return self._storage

    @property
    def manifest(self):
        rev = self.rev
        path = self.path
        storage = self.storage
        if not hasattr(self, '_manifest'):
            try:
                self._manifest = storage.manifest(rev, path).next()
            except pmr2.mercurial.exceptions.PathNotFound:
                self._manifest = None
            except pmr2.mercurial.exceptions.RevisionNotFound:
                # XXX should return/redirect to an informative warning
                # page?
                self._manifest = None
        return self._manifest

    @property
    def fileinfo(self):
        rev = self.rev
        path = self.path
        storage = self.storage
        if not hasattr(self, '_fileinfo'):
            try:
                self._fileinfo = storage.fileinfo(rev, path).next()
                self._fileinfo['date'] = pmr2.mercurial.utils.filter(
                    self._fileinfo['date'], 'isodate')
            except pmr2.mercurial.exceptions.PathNotFound:
                self._fileinfo = None
            except pmr2.mercurial.exceptions.RevisionNotFound:
                # XXX should return/redirect to an informative warning
                # page?
                self._fileinfo = None
        return self._fileinfo


