import os
from os.path import join

def mkreporoot(path):
    # creates the directory in repository root
    os.mkdir(join(path, 'workspace'))
    os.mkdir(join(path, 'sandbox'))

def mkrepo(root, name):
    # XXX fake method, and assumes mercurial
    path = join(root, name)
    os.mkdir(path)
    os.mkdir(join(path, '.hg'))

