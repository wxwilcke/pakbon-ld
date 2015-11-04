#!/usr/bin/python3

import rdflib


def getID(e, namespace):
    return e.attrib['{' + namespace['sikb'] + '}' + 'id']


def addProperty(g, parent, child, relation):
    g.add((parent, relation, child))


def addType(g, namespace, node, ntype):
    addProperty(g, node, ntype, namespace['rdf'].type)


def addLabel(g, namespace, node, label, lang):
    lnode = rdflib.Literal(label, lang=lang)
    addType(g, namespace, lnode, namespace['xsd'].string)
    addProperty(g, node, lnode, namespace['rdfs'].label)


def genID(g, namespace, pnode):
    uri = ''
    while True:
        uri = rdflib.URIRef(namespace['base']
                            + g.value(pnode, namespace['crm'].P48_has_preferred_identifier, None)
                            + '-'
                            + rdflib.BNode())

        if (uri, None, None) not in g:
            break

    return uri


def setGraphNamespaceIDs(graph, namespace):
    nsmgr = rdflib.namespace.NamespaceManager(graph)

    for k, v in namespace.items():
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


def getNodeClass(graph, namespace, node):
    btnode = graph.value(subject=node,
                         predicate=rdflib.URIRef(namespace['rdf'].type),
                         object=None)

    return btnode


def getNodeFromBaseType(graph, namespace, baseType):
    btnode = graph.value(subject=None,
                         predicate=rdflib.URIRef(namespace['crm'].P48_has_preferred_identifier),
                         object=rdflib.Literal(getID(baseType, namespace)))

    exists = True if btnode else False
    if not exists:
        btnode = rdflib.URIRef(namespace['base'] + getID(baseType, namespace))

    return (btnode, exists)


def getNodeFromElem(graph, namespace, element):
    enode = graph.value(subject=None,
                        predicate=rdflib.URIRef(namespace['crm'].P48_has_preferred_identifier),
                        object=rdflib.Literal(element.text))

    exists = True if enode else False
    if not exists:
        enode = rdflib.URIRef(namespace['base'] + element.text)

    return (enode, exists)

def addRefIfExists(graph, namespace, node, element):
    rnode = None
    if 'codereferentieId' in element.attrib:
        rnode = graph.value(subject=None,
                            predicate=rdflib.URIRef(namespace['crm'].P48_has_preferred_identifier),
                            object=rdflib.Literal(element.attrib['codereferentieId']))
    if rnode is not None:
        addProperty(graph, node, rnode, namespace['crm'].P71i_is_listed_in)

def extractGenericObjectFields(graph, namespace, gnode, tnode):
    attrib = [
        '{' + namespace['sikb'] + '}' + 'id']

    if attrib[0] in tnode.attrib.keys():  # id
        child = rdflib.Literal(tnode.attrib[attrib[0]])
        addProperty(graph, gnode, child, namespace['crm'].P48_has_preferred_identifier)
        addType(graph, namespace, child, namespace['crm'].E42_Identifier)


def extractGeoObjectFields(graph, namespace, gnode, tnode):
    extractGenericObjectFields(graph, namespace, gnode, tnode)


def extractBasisTypeFields(graph, namespace, gnode, tnode):
    extractGenericObjectFields(graph, namespace, gnode, tnode)
    attrib = [
        'bronId',
        '{' + namespace['sikb'] + '}' + 'informatie']

    if attrib[0] in tnode.attrib.keys():  # bronId
        child = rdflib.Literal(tnode.attrib[attrib[0]])
        addProperty(graph, gnode, child, namespace['crm'].P1_is_identified_by)
        addType(graph, namespace, child, namespace['crm'].E42_Identifier)

    for attr in tnode.getchildren():
        if attr.tag == attrib[1]:  # informatie
            child = rdflib.Literal(attr.text)
            addProperty(graph, gnode, child, namespace['crm'].P3_has_note)
            addType(graph, namespace, child, namespace['crm'].E62_String)


def extractBasisNaamTypeFields(graph, namespace, gnode, tnode):
    extractBasisTypeFields(graph, namespace, gnode, tnode)
    attrib = ['{' + namespace['sikb'] + '}' + 'naam']

    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # naam
            child = rdflib.Literal(attr.text)
            addProperty(graph, gnode, child, namespace['crm'].P1_is_identified_by)
            addType(graph, namespace, child, namespace['crm'].E41_Appellation)


def extractBasisLocatieTypeFields(graph, namespace, gnode, tnode):
    extractBasisTypeFields(graph, namespace, gnode, tnode)

    attrib = ['{' + namespace['sikb'] + '}' + 'geolocatieId']

    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # geolocatieId
            child = rdflib.Literal(attr.text)
            addProperty(graph, gnode, child, namespace['crm'].P87_is_identified_by)
            addType(graph, namespace, child, namespace['crm'].E44_Place_Appellation)


def extractBasisLocatieNaamTypeFields(graph, namespace, gnode, tnode):
    extractBasisLocatieTypeFields(graph, namespace, gnode, tnode)

    attrib = ['{' + namespace['sikb'] + '}' + 'naam']

    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # naam
            child = rdflib.Literal(attr.text)
            addProperty(graph, gnode, child, namespace['crm'].P1_is_identified_by)
            addType(graph, namespace, child, namespace['crm'].E41_Appellation)
