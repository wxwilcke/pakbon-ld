#!/usr/bin/python3

import rdflib
import re


def getID(e, namespace):
    return e.attrib['{' + str(namespace['sikb']) + '}' + 'id']


def addProperty(g, parent, child, relation):
    g.add((parent, relation, child))


def addType(g, node, ntype):
    ns = dict(ns for ns in g.namespace_manager.namespaces())
    addProperty(g, node, ntype, rdflib.URIRef(ns['rdf'] + 'type'))


def addLabel(graph, node, label, lang):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    lnode = rdflib.Literal(label, lang=lang)
    addProperty(graph, node, lnode, rdflib.URIRef(nss['rdfs'] + 'label'))


def genID(graph, pnode, basens):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    uri = ''
    while True:
        uri = rdflib.URIRef(basens
                            + 'SIKBID_' + graph.value(pnode, rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'), None)
                            + '-'
                            + rdflib.BNode())

        if (uri, None, None) not in graph:
            break

    return uri


def setGraphNamespaceIDs(graph, namespace):
    nsmgr = rdflib.namespace.NamespaceManager(graph)

    for k, v in namespace.items():
        if k != 'base':
            nsmgr.bind(k, v)


def gmlLiteralOf(et, tnode):
    gmlns = 'http://www.opengis.net/gml/3.2'
    xsins = 'http://www.w3.org/2001/XMLSchema-instance'

    attribs = tnode.attrib

    gmltype = tnode.attrib.pop('{' + xsins + '}' + 'type')
    gmlid = tnode.attrib.pop('{' + gmlns + '}' + 'id')
    raw = '<' + gmltype + ' xmlns:gml=' + '\\\"' + gmlns + '\\\" gml:id=\\\"' + gmlid + '\\\"'
    for k, v in attribs.items():
        raw += ' ' + k + '=\\\"' + v + '\\\"'
    raw += '>'

    for element in tnode:
        raw += et.tostring(element).decode('unicode_escape').replace('"', '\\\"').rstrip()

    raw += '</' + gmltype + '>'

    return raw


def getNodeClass(graph, node):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    btnode = graph.value(subject=node,
                         predicate=rdflib.URIRef(nss['rdf'] + 'type'),
                         object=None)

    return btnode


def addSubPropertyIfExists(graph, basens, parent, child, subpropname, superprop):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    p = rdflib.URIRef(basens + re.sub('{.*}', '', subpropname))

    if (None, p, None) not in graph:
        addType(graph, p, rdflib.URIRef(nss['rdf'] + 'Property'))
        addProperty(graph, p, superprop, rdflib.URIRef(nss['rdfs'] + 'subPropertyOf'))
        info = rdflib.Literal('Nederlandstalig equivalent (of specifieker) van externe relatie zoals vastgelegd in SIKB Protocol 0102', 'nl')
        addProperty(graph, p, info, rdflib.URIRef(nss['rdfs'] + 'comment'))

    addProperty(graph, parent, child, p)


def getNodeFromBaseType(graph, basens, baseType):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    btnode = graph.value(subject=None,
                         predicate=rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'),
                         object=rdflib.Literal(getID(baseType, nss), datatype=rdflib.URIRef(nss['xsd'] + 'ID')))

    exists = True if btnode else False
    if not exists:
        btnode = rdflib.URIRef(basens + getID(baseType, nss))

    return (btnode, exists)


def getNodeFromElem(graph, basens, element):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    enode = graph.value(subject=None,
                        predicate=rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'),
                        object=rdflib.Literal(element.text, datatype=rdflib.URIRef(nss['xsd'] + 'ID')))

    exists = True if enode else False
    if not exists:
        enode = rdflib.URIRef(basens + element.text)

    return (enode, exists)


def addRefIfExists(graph, node, element):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    rnode = None
    if 'codereferentieId' in element.attrib:
        rnode = graph.value(subject=None,
                            predicate=rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'),
                            object=rdflib.Literal(element.attrib['codereferentieId']))
    if rnode is not None:
        addProperty(graph, node, rnode, rdflib.URIRef(nss['crm'] + 'P71i_is_listed_in'))


def extractGenericObjectFields(graph, gnode, tnode, label=''):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = [
        '{' + str(nss['sikb']) + '}' + 'id']

    if attrib[0] in tnode.attrib.keys():  # id
        child = rdflib.Literal(tnode.attrib[attrib[0]], datatype=rdflib.URIRef(nss['xsd'] + 'ID'))
        addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'))

    label = re.sub('{' + str(nss['sikb']) + '}', '', tnode.tag).title() + ((' ' + label) if label != '' else '')
    if label != '':
        addLabel(graph, gnode, label, 'nl')


def extractGeoObjectFields(graph, gnode, tnode):
    extractGenericObjectFields(graph, gnode, tnode)


def extractBasisTypeFields(graph, gnode, tnode, label=''):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())

    attrib = [
        'bronId',
        '{' + str(nss['sikb']) + '}' + 'informatie']

    if attrib[0] in tnode.attrib.keys():  # bronId
        child = rdflib.Literal(tnode.attrib[attrib[0]], datatype=rdflib.URIRef(nss['xsd'] + 'ID'))
        addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P1_is_identified_by'))
        label = tnode.attrib[attrib[0]] + ((' ' + '(' + label + ')') if label != '' else '')

    for attr in tnode.getchildren():
        if attr.tag == attrib[1]:  # informatie
            child = rdflib.Literal(attr.text, lang='nl')
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P3_has_note'))

    extractGenericObjectFields(graph, gnode, tnode, label)


def extractBasisNaamTypeFields(graph, gnode, tnode):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = ['{' + str(nss['sikb']) + '}' + 'naam']

    label = ''
    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # naam
            child = rdflib.Literal(attr.text, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P1_is_identified_by'))
            label = attr.text

    extractBasisTypeFields(graph, gnode, tnode, label)


def extractBasisLocatieTypeFields(graph, gnode, tnode, label=''):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = ['{' + str(nss['sikb']) + '}' + 'geolocatieId']

    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # geolocatieId
            child = rdflib.Literal(attr.text, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P87_is_identified_by'))

    extractBasisTypeFields(graph, gnode, tnode, label)


def extractBasisLocatieNaamTypeFields(graph, gnode, tnode):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = ['{' + str(nss['sikb']) + '}' + 'naam']

    label = ''
    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # naam
            child = rdflib.Literal(attr.text, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P1_is_identified_by'))
            label = attr.text

    extractBasisLocatieTypeFields(graph, gnode, tnode, label)


def rawString(string):
    return re.sub('\s+', ' ', re.sub(r'\\', r'\\\\', string))
