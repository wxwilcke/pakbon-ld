#!/usr/bin/python3

import os.path


def write(graph=None, filename=None, sformat='turtle', overwrite=True):
    if graph is None:
        raise ValueError('Graph missing')
    elif filename is None:
        raise ValueError('Filename missing')
    elif not overwrite and os.path.isfile(filename):
        raise OSError('File already exists')

    with open(filename, 'w') as f:
        f.write(str(graph.serialize(format=sformat).decode('unicode_escape')))
