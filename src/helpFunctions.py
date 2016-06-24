#!/usr/bin/python3

import rdflib
import re
import hashlib


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

def fuzzyTextMatchElseNew(graph, basens, ctype, attrs=[], string='', lang='nl', max_diff=.4, interactive=True):
    node = fuzzyTextMatch(graph, ctype, attrs, string, max_diff, interactive)

    if node is None:
        hid = genHash(None, None, [], salt=string + ctype.toPython())
        node = getNode(graph, hid)
        if node is None:
            nss = dict(ns for ns in graph.namespace_manager.namespaces())
            node = rdflib.URIRef(basens + hid)
            addType(graph, node, ctype)
            label = rdflib.Literal(string, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
            addLabel(graph, node, label, lang)

    return node

def fuzzyTextMatch(graph, ctype, attrs=[], string='', max_diff=.4, interactive=True):
    from difflib import SequenceMatcher

    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    candidates = []
    for node, _, _ in graph.triples((None, rdflib.URIRef(nss['rdf'] + 'type'), ctype)):
        dlist = []
        for attr in attrs:
            value = graph.value(node, attr, None)
            if value is None:
                continue

            dlist.append(SequenceMatcher(None, string.strip().lower(), value.strip().lower()).ratio())

        d = sum(dlist)/len(dlist)
        if d >= 1.0 - max_diff:
            candidates.append((d, node))

    if candidates == []:
        return None

    candidates.sort(reverse=True)
    if not interactive:
        return candidates[0][1]

    print("\nDetected Possible Alignment on: {} ({})".format(string, re.sub('.*/', '', ctype)))

    candidate = None
    for i, (d, candidate) in enumerate(candidates, 1):
        print(" Candidate Solution ({}% match) {} / {}".format(int(d*100), i, len(candidates)))
        print("\tCandidate: \t{}".format(graph.preferredLabel(candidate)[0][1]))

        q = ''
        while True:
            q = input(" Align? (y[es] / n[o] / m[ore info]) / s[kip] (*): ")
            if q == 'y':
                return candidate
            elif q == 'n':
                break
            elif q == 'm':
                ask = True
                for pred, obj in graph.predicate_objects(candidate):
                    pred = re.sub('.*/', '', pred)
                    obj = re.sub('.*/', '', obj)
                    n = 50 - len(pred)
                    if n <= 0:
                        obj = obj[:len(obj)+n-3] + '...'
                        n = 1
                    m = 50 - len(obj)
                    if m <= 0:
                        obj = obj[:len(obj)+m-3] + '...'
                        m = 1
                    print(" < {} >{:>{}}< {} >".format(pred, '', n, obj), end="{:>{}}".format('', m))
                    if ask:
                        q = input("[(n)ext], (u)ntil end, (a)bort ")
                        if q == 'a':
                            break
                        elif q == 'u':
                            ask = False
                    else:
                        print()
            else:
                return None

        candidate = None

    return candidate

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


def rawString(string):
    return re.sub('\s+', ' ', re.sub(r'\"', r'\\"', re.sub(r'\\', r'\\\\', string)))
