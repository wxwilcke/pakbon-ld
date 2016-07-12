#!/usr/bin/python3

import rdflib
import re
import hashlib
import geoSolv as geos


def genHash(tnode, sikbns, features=[], salt='', pre='R'):
    while len(features) > 0:
        tag = features.pop()
        if type(tag) is str:
            salt += ''.join([value.text for value in tnode.iter(sikbns + tag)])
        elif type(tag) is dict:
            for k, v in tag.items():
                subnode = tnode.find(sikbns + k)
                if subnode is not None:
                    salt += ''.join([value.text for subtag in v for value in subnode.iter(sikbns + subtag)])

    return pre + hashlib.sha1(salt.encode()).hexdigest()

def getID(e, sikbns):
    return e.attrib[sikbns + 'id']

def getTID(g, node):
    nss = dict(ns for ns in g.namespace_manager.namespaces())
    tid = g.value(subject=node,\
                    predicate=rdflib.URIRef(nss['crm'] + 'P1_is_identified_by'),\
                    object=None)

    return tid if tid is not None else ''

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


def updateLabel(graph, node, label, lang, delimiter=' ', checkDoubleEntries=True):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())

    oldLabel = graph.value(subject=node,\
                    predicate=rdflib.URIRef(nss['rdfs'] + 'label'),\
                    object=None)

    if oldLabel is None or (checkDoubleEntries and label in oldLabel):
        return

    graph.remove((node, rdflib.URIRef(nss['rdfs'] + 'label'), oldLabel))
    addLabel(graph, node, oldLabel.value + delimiter + label, lang)


def genID(graph, pnode, basens):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    uri = ''
    while True:
        uri = rdflib.URIRef(basens
                            + graph.value(pnode, rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'), None)
                            + rdflib.BNode())

        if (uri, None, None) not in graph:
            break

    return uri

def getNodeID(graph, node):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    ident = graph.value(node, rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'), None)

    return '' if ident is None else ident

def getNode(graph, ident):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    return graph.value(None, rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'),\
                       rdflib.Literal(ident, datatype=rdflib.URIRef(nss['xsd'] + 'ID')))


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

def getTreeNodeByID(troot, sikbns, uuid):
    for elem in troot.iter():
        if sikbns + 'id' in elem.attrib and elem.attrib[sikbns + 'id'] == uuid:
            return elem

    return None

def addRefIfExists(protocol, cnode, element):
    if 'codereferentieId' in element.attrib:
        treeNode = getTreeNodeByID(protocol.troot, protocol.sikbns, element.attrib['codereferentieId'])
        crnode = protocol.codereferentieHandler(treeNode).node
        if crnode is not None:
            addProperty(protocol.graph, cnode, crnode, rdflib.URIRef(protocol.nss['crm'] + 'P71i_is_listed_in'))


def extractGenericObjectFields(graph, gnode, tnode, sikbns, label='', nolabel=False):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    """
    attrib = [sikbns + 'id']

    if attrib[0] in tnode.attrib.keys():  # id
        child = rdflib.Literal(tnode.attrib[attrib[0]], datatype=rdflib.URIRef(nss['xsd'] + 'ID'))
        addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'))
    """
    idnode = rdflib.Literal(re.sub('.*/', '', gnode.toPython()), datatype=rdflib.URIRef(nss['xsd'] + 'ID'))
    addProperty(graph, gnode, idnode, rdflib.URIRef(nss['crm'] + 'P48_has_preferred_identifier'))

    if nolabel:
        return

    label = re.sub(sikbns, '', tnode.tag).title() + ((' ' + label) if label != '' else '')
    if label != '':
        addLabel(graph, gnode, label, 'nl')


def extractGeoObjectFields(graph, gnode, tnode, sikbns):
    extractGenericObjectFields(graph, gnode, tnode, sikbns)


def extractBasisTypeFields(graph, gnode, tnode, sikbns, label='', nolabel=False, gpnode=None, gid=''):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())

    attrib = [
        'bronId',
        sikbns + 'informatie']

    if attrib[0] in tnode.attrib.keys():  # bronId
        sourceID = tnode.attrib[attrib[0]]
        if gid != '':
            sourceID = gid
        elif gpnode is not None:
            sourceID = "{}:{}".format(getTID(graph, gpnode), sourceID)

        child = rdflib.Literal(sourceID, datatype=rdflib.URIRef(nss['xsd'] + 'ID'))
        addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P1_is_identified_by'))
        label = '(' + label + ')' if label != '' else ''

    for attr in tnode.getchildren():
        if attr.tag == attrib[1]:  # informatie
            child = rdflib.Literal(attr.text, lang='nl')
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P3_has_note'))

    extractGenericObjectFields(graph, gnode, tnode, sikbns, label, nolabel)


def extractBasisNaamTypeFields(graph, gnode, tnode, sikbns, nolabel=False, gpnode=None):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = [sikbns + 'naam']

    label = ''
    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # naam
            gpid = getTID(graph, gpnode)
            nid = "{}:{}".format(gpid, attr.text) if gpid != '' else attr.text
            child = rdflib.Literal(nid, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P1_is_identified_by'))
            label = nid

    extractBasisTypeFields(graph, gnode, tnode, sikbns, label, nolabel, gpnode=gpnode, gid=nid)


def extractBasisLocatieTypeFields(graph, gnode, tnode, sikbns, label='', gpnode=None, gid=''):
    """nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = [sikbns + 'geolocatieId']

    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # geolocatieId # TODO ?
            child = rdflib.Literal(attr.text, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P87_is_identified_by'))
    """

    extractBasisTypeFields(graph, gnode, tnode, sikbns, label, gpnode=gpnode, gid=gid)


def extractBasisLocatieNaamTypeFields(graph, gnode, tnode, sikbns, gpnode=None):
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    attrib = [sikbns + 'naam']

    label = ''
    for attr in tnode.getchildren():
        if attr.tag == attrib[0]:  # naam
            gpid = getTID(graph, gpnode)
            nid = "{}:{}".format(gpid, attr.text) if gpid != '' else attr.text
            child = rdflib.Literal(nid, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
            addProperty(graph, gnode, child, rdflib.URIRef(nss['crm'] + 'P1_is_identified_by'))
            label = nid

    extractBasisLocatieTypeFields(graph, gnode, tnode, sikbns, label, gpnode=gpnode, gid=nid)

def genGeoRef(graph, basens, housenumber='', streetname='', placename='', countryname='Netherlands', postalcode='',\
              interactive=True):
    wgs84 = geos.fuzzyTextMatch(housenumber=housenumber, streetname=streetname, placename=placename, countryname=countryname,\
                 postalcode=postalcode, interactive=interactive)

    if wgs84 is None:
        return None

    nss = dict(ns for ns in graph.namespace_manager.namespaces())

    # unique ID because we dont know elevation wrt address
    bhid = genHash(None, None, [], salt=str(wgs84[0]) + str(wgs84[1]) + 'POINT')
    node = getNode(graph, bhid)
    if node is not None:
       return node

    point = rdflib.URIRef(basens + bhid)
    addType(graph, point, rdflib.URIRef(nss['locn'] + 'Geometry'))
    addType(graph, point, rdflib.URIRef(nss['wgs84'] + 'Point'))
    streethouse = ' '.join([streetname, housenumber]) if housenumber != '' else streetname
    label = ', '.join([term for term in [streethouse, postalcode, placename, countryname]\
                       if term != ''])
    addLabel(graph, point, "WGS84 puntcoordinaat van '{}'".format(label), 'nl')

    addProperty(graph, point, rdflib.Literal(wgs84[0]), rdflib.URIRef(nss['wgs84'] + 'lat'))
    addProperty(graph, point, rdflib.Literal(wgs84[1]), rdflib.URIRef(nss['wgs84'] + 'long'))

    return point

def rawString(string):
    return re.sub('\s+', ' ', re.sub(r'\"', r'\\"', re.sub(r'\\', r'\\\\', string)))
