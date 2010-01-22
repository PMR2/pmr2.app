import os
from os.path import join, isdir

def mkreporoot(path):
    # creates the directory in repository root
    os.mkdir(join(path, 'workspace'))
    os.mkdir(join(path, 'sandbox'))

def mkrepo(root, count=1):
    def mk(path):
        # XXX fake method, and assumes mercurial
        os.mkdir(path)
        os.mkdir(join(path, '.hg'))

    if count == 1:
        mk(root)
        return

    for i in xrange(count):
        name = prefix + str(i)
        mk(join(root, name))
