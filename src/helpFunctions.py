#!/usr/bin/python3

import rdflib
import re
import hashlib


def genHash(s):
    return 'x' + hashlib.sha1().hexdigest(s.encode())

def getID(e, sikbns):
    return e.attrib[sikbns + 'id']


def addProperty(g, parent, child, relation):
    g.add((parent, relation, child))


def addType(g, node, ntype):
    ns = dict(ns for ns in g.namespace_manager.namespaces())
    addProperty(g, node, ntype, rdflib.URIRef(ns['rdf'] + 'type'))


def addSubClassOf(g, subclass, superclass):
    ns = dict(ns for ns in g.namespace_manager.namespaces())
    addProperty(g, subclass, superclass, rdflib.URIRef(ns['rdfs'] + 'subClassOf'))


def addLabel(graph, node, label, lang):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    lnode = rdflib.Literal(label, lang=lang)
    addProperty(graph, node, lnode, rdflib.URIRef(nss['rdfs'] + 'label'))

def getLabel(g, node):
    nss = dict(ns for ns in g.namespace_manager.namespaces())
    label = g.value(subject=node,\
                    predicate=rdflib.URIRef(nss['rdfs'] + 'label'),\
                    object=None)

    return label.value if label is not None else ''

def updateLabel(graph, node, label, lang):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    graph.remove((node, rdflib.URIRef(nss['rdfs'] + 'label'), None))
    addLabel(graph, node, label, lang)


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

    return (raw, gmlid, gmltype.lstrip('gml:').rstrip('Type'))


def getNodeClass(graph, node):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    btnode = graph.value(subject=node,
                         predicate=rdflib.URIRef(nss['rdf'] + 'type'),
                         object=None)

    return btnode


def addSchemaType(graph, ns, node, parentnode, name, parentname):
    addType(graph, node, rdflib.URIRef(ns + 'SIKB0102_Schema_' + parentname.title() + '.' + name.title()))
    addProperty(graph, parentnode, node, rdflib.URIRef(ns + 'SIKB0102_Schema_' + parentname + '_' + name))

def addSubPropertyIfExists(graph, basens, parent, child, subpropname, superprop):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    p = rdflib.URIRef(basens + re.sub('{.*}', '', subpropname))

    if (None, p, None) not in graph:
        addType(graph, p, rdflib.URIRef(nss['rdf'] + 'Property'))
        addProperty(graph, p, superprop, rdflib.URIRef(nss['rdfs'] + 'subPropertyOf'))

    addProperty(graph, parent, child, p)


def getNodeFromBaseType(graph, basens, sikbns, baseType):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    btnode = graph.value(subject=None,
                         predicate=rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'),
                         object=rdflib.Literal(getID(baseType, sikbns), datatype=rdflib.URIRef(nss['xsd'] + 'ID')))

    exists = True if btnode else False
    if not exists:
        btnode = rdflib.URIRef(basens + getID(baseType, sikbns))

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


def extractGenericObjectFields(graph, gnode, tnode, sikbns, label=''):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = [sikbns + 'id']

    if attrib[0] in tnode.attrib.keys():  # id
        child = rdflib.Literal(tnode.attrib[attrib[0]], datatype=rdflib.URIRef(nss['xsd'] + 'ID'))
        addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'))

    label = re.sub(sikbns, '', tnode.tag).title() + ((' ' + label) if label != '' else '')
    if label != '':
        addLabel(graph, gnode, label, 'nl')


def extractGeoObjectFields(graph, gnode, tnode, sikbns):
    extractGenericObjectFields(graph, gnode, tnode, sikbns)


def extractBasisTypeFields(graph, gnode, tnode, sikbns, label=''):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())

    attrib = [
        'bronId',
        sikbns + 'informatie']

    if attrib[0] in tnode.attrib.keys():  # bronId
        child = rdflib.Literal(tnode.attrib[attrib[0]], datatype=rdflib.URIRef(nss['xsd'] + 'ID'))
        addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P1_is_identified_by'))
        label = tnode.attrib[attrib[0]] + ((' ' + '(' + label + ')') if label != '' else '')

    for attr in tnode.getchildren():
        if attr.tag == attrib[1]:  # informatie
            child = rdflib.Literal(attr.text, lang='nl')
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P3_has_note'))

    extractGenericObjectFields(graph, gnode, tnode, sikbns, label)


def extractBasisNaamTypeFields(graph, gnode, tnode, sikbns):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = [sikbns + 'naam']

    label = ''
    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # naam
            child = rdflib.Literal(attr.text, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P1_is_identified_by'))
            label = attr.text

    extractBasisTypeFields(graph, gnode, tnode, sikbns, label)


def extractBasisLocatieTypeFields(graph, gnode, tnode, sikbns, label=''):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = [sikbns + 'geolocatieId']

    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # geolocatieId
            child = rdflib.Literal(attr.text, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P87_is_identified_by'))

    extractBasisTypeFields(graph, gnode, tnode, sikbns, label)


def extractBasisLocatieNaamTypeFields(graph, gnode, tnode, sikbns):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = [sikbns + 'naam']

    label = ''
    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # naam
            child = rdflib.Literal(attr.text, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P1_is_identified_by'))
            label = attr.text

    extractBasisLocatieTypeFields(graph, gnode, tnode, sikbns, label)


def rawString(string):
    return re.sub('\s+', ' ', re.sub(r'\"', r'\\"', re.sub(r'\\', r'\\\\', string)))
