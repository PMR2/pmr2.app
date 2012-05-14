# XXX This is duplicated (duplicates) similar class provided by 
# cellml.pmr2, but in a different way.  Consider merging these at some
# point into a common module/egg.

import socket
import urllib2


# try to use the default methods.

class DisabledFileHandler(urllib2.FileHandler):
    def file_open(self, req):
        raise urllib2.URLError('file protocol disabled')


class DisabledFTPHandler(urllib2.FTPHandler):
    def ftp_open(self, req):
        raise urllib2.URLError('ftp protocol disabled')


_opener = None
def urlopen(url, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
    global _opener
    if _opener is None:
        _opener = urllib2.build_opener(
            DisabledFileHandler, DisabledFTPHandler)
    # client headers?
    return _opener.open(url, data, timeout)



