#!/usr/bin/python3

import rdflib


def getID(e, namespace):
    return e.attrib['{' + namespace['sikb'] + '}' + 'id']


def addProperty(g, parent, child, relation):
    g.add((parent, relation, child))


def addType(g, namespace, node, ntype):
    addProperty(g, node, ntype, namespace['rdf'].type)


def extractBasisTypeFields(graph, namespace, gnode, tnode):
    attrib = [
        '{' + namespace['sikb'] + '}' + 'id',
        'bronId',
        '{' + namespace['sikb'] + '}' + 'informatie']

    if attrib[0] in tnode.attrib.keys():  # id
        child = rdflib.Literal(tnode.attrib[attrib[0]])
        addProperty(graph, gnode, child, namespace['crm'].P48_has_preferred_identifier)
        addType(graph, namespace, child, namespace['crm'].E42_Identifier)
    if attrib[1] in tnode.attrib.keys():  # bronId
        child = rdflib.Literal(tnode.attrib[attrib[1]])
        addProperty(graph, gnode, child, namespace['crm'].P48_has_preferred_identifier)
        addType(graph, namespace, child, namespace['crm'].E42_Identifier)

    for attr in tnode.getchildren():
        if attr.tag == attrib[2]:  # informatie
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
