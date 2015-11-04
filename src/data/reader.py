#!/usr/bin/python3

from xml.etree import ElementTree as ET
import os.path


def read(filename=None):
    if filename is None:
        raise ValueError('Filename missing.')
    elif not os.path.isfile(filename):
        raise OSError('File not found')

    tree = ET.parse(filename)
    if not isProtocol0102(tree):
        raise TypeError('Not a valid instantation of SIKB Protocol 0102.')

    return (ET, ET.parse(filename))


def isProtocol0102(tree=None):
    ns = 'http://www.sikb.nl/sikb0102/3.1.0'
    rootElement = 'sikb0102'

    if tree is None:
        raise ValueError('Missing Value.')

    return tree.getroot().tag == '{' + ns + '}' + rootElement
