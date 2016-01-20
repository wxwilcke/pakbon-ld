#!/usr/bin/python3

from xml.etree import ElementTree as ET
import zipfile
import rdflib
import os.path
import re


def read_tree(filename=None, ignore_version=False):
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


def read_zippedTree(filename=None, zippedfilename=None, ignore_version=False):
    if filename is None or zippedfilename is None:
        raise ValueError('Filename missing.')
    elif not os.path.isfile(filename):
        raise OSError('File not found: ' + filename)

    zfile = zipfile.ZipFile(filename, 'r')
    with zfile.open(zippedfilename) as zf:
        troot = ET.fromstring(zf.read())

    if ('version' in troot.attrib and troot.attrib['version'] != '3.1.0' or 'versie' in troot.attrib and
        troot.attrib['versie'] != '3.1.0') and not ignore_version:
        raise TypeError('Unsupported version of SIKB Protocol 0102.\nUse --ignore_version to continue regardless.')

    return troot


def read_graph(filename=None):
    if filename is None:
        raise ValueError('Filename missing.')
    elif not os.path.isfile(filename):
        raise OSError('File not found: ' + filename)

    graph = rdflib.Graph()
    return graph.parse(filename, format=rdflib.util.guess_format(filename))


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
