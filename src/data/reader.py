#!/usr/bin/python3

from xml.etree import ElementTree as ET
import os.path
import re


def read(filename=None, ignore_version=False):
    if filename is None:
        raise ValueError('Filename missing.')
    elif not os.path.isfile(filename):
        raise OSError('File not found: ' + filename)

    tree = ET.parse(filename)
    if not isProtocol0102(tree):
        raise TypeError('Not a valid instantation of SIKB Protocol 0102.')
    if not isSupportedVersion(tree) and not ignore_version:
        raise TypeError('Unsupported version of SIKB Protocol 0102.\nUse --ignore_version to continue regardless.')

    return (ET, tree, versionOf(tree))


def versionOf(tree=None):
    if tree is None:
        raise ValueError('Missing Value.')

    return tree.getroot().attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'].split('/')[-2]


def isProtocol0102(tree=None):
    ns_base = 'http://www.sikb.nl/sikb0102'
    rootElement = 'sikb0102'

    if tree is None:
        raise ValueError('Missing Value.')

    return re.sub('(/(\d\.)+(\d)+){1}', '', tree.getroot().tag) == '{' + ns_base + '}' + rootElement


def isSupportedVersion(tree=None):
    if tree is None:
        raise ValueError('Missing Value.')

    return re.search('/3\.1\.0\}[a-z]+[0-9]+$', tree.getroot().tag) is not None
