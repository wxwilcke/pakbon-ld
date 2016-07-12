#!/usr/bin/python3

import rdflib
import re
import helpFunctions as hf
from SPARQLWrapper import SPARQLWrapper

def query(endpoint='', query=''):
    sparql = SPARQLWrapper(endpoint, returnFormat="json")
    sparql.setQuery(query)

    try:
        ret = sparql.queryAndConvert()
    except:
        print('Query Error')
        return []

    return ret['results']['bindings']

def queryConstructorA(ctype, attrs = [], limit = -1):
    queryString = "SELECT DISTINCT ?s ?label"
    for i, attr in enumerate(attrs, 1):
        queryString += " ?attribute_{}".format(i)

    queryString += " WHERE {{ ?s a <{}> ; <http://www.w3.org/2000/01/rdf-schema#label> ?label ".format(ctype)
    for i, attr in enumerate(attrs, 1):
        queryString += "; <{}> ?attribute_{} ".format(attr, i)

    queryString += ". }"
    queryString += " LIMIT {}".format(limit) if limit >= 0 else ""

    return queryString

def queryConstructorB(node, limit = -1):
    queryString = "SELECT ?pred ?obj WHERE {{ <{}> ?pred ?obj . }}".format(node)
    queryString += " LIMIT {}".format(limit) if limit >= 0 else ""

    return queryString

def fuzzyTextMatchElseNew(graph, default_graphs, basens, ctype, attrs=[], string='', lang='nl', max_diff=.4, interactive=True,\
                          align='off', endpoint=''):
    exnode = None
    if align == 'local' or align == 'global' or align == 'both':
        (exnode, source) = fuzzyTextMatch(graph, default_graphs, ctype, attrs, string, max_diff, interactive, align, endpoint)

    # guarantee uniqueness within a converted graph
    if source == graph:
        return exnode

    # else ensure complete graph by using 'sameAs'
    nss = dict(ns for ns in graph.namespace_manager.namespaces())
    hid = hf.genHash(None, None, [], salt=string + ctype.toPython())
    node = hf.getNode(graph, hid)
    if node is None:
        node = rdflib.URIRef(basens + hid)
        hf.addType(graph, node, ctype)
        label = rdflib.Literal(string, datatype=rdflib.URIRef(nss['xsd'] + 'string'))
        hf.addLabel(graph, node, label, lang)

    if exnode is not None:
        hf.addProperty(graph, node, exnode, rdflib.URIRef(nss['rdfs'] + 'sameAs'))
        hf.addProperty(graph, exnode, node, rdflib.URIRef(nss['rdfs'] + 'sameAs'))

    return node

def fuzzyTextMatch(graph, default_graphs, ctype, attrs=[], string='', max_diff=.4, interactive=True, align='local', endpoint=''):
    from difflib import SequenceMatcher

    candidates = []

    if align == 'both' or align == 'global':
        qresults = query(endpoint, queryConstructorA(ctype, attrs))
        for entry in qresults:
            dlist = []
            for i, attr in enumerate(attrs, 1):
                dlist.append(SequenceMatcher(None, string.strip().lower(),\
                                             entry['attribute_{}'.format(i)]['value'].strip().lower()).ratio())

            d = sum(dlist)/len(dlist)
            if d >= 1.0 - max_diff:
                candidates.append((d, rdflib.URIRef(entry['s']['value']), entry['label']['value'], endpoint))

    if align == 'both' or align == 'local':
        nss = dict(ns for ns in graph.namespace_manager.namespaces())
        for dgraph in default_graphs:
            for node, _, _ in dgraph.triples((None, rdflib.URIRef(nss['rdf'] + 'type'), ctype)):
                dlist = []
                for attr in attrs:
                    value = dgraph.value(node, attr, None)
                    if value is None:
                        continue

                    dlist.append(SequenceMatcher(None, string.strip().lower(), value.strip().lower()).ratio())

                d = sum(dlist)/len(dlist)
                if d >= 1.0 - max_diff:
                    candidates.append((d, node, dgraph.preferredLabel(node)[0][1], dgraph))

        for node, _, _ in graph.triples((None, rdflib.URIRef(nss['rdf'] + 'type'), ctype)):
            dlist = []
            for attr in attrs:
                value = graph.value(node, attr, None)
                if value is None:
                    continue

                dlist.append(SequenceMatcher(None, string.strip().lower(), value.strip().lower()).ratio())

            d = sum(dlist)/len(dlist)
            if d >= 1.0 - max_diff:
                candidates.append((d, node, graph.preferredLabel(node)[0][1], graph))

    if candidates == []:
        return (None, None)

    candidates.sort(reverse=True) # dublicate entries?
    if not interactive:
        return (candidates[0][1], candidates[0][3])

    return fuzzyTextMatchUI(candidates, ctype, string, align)

def fuzzyTextMatchUI(candidates, ctype, string, align):

    print("\nDetected Possible Alignment on: {} ({})".format(string, re.sub('.*/', '', ctype)))

    candidate = None
    endpoint = None
    for i, (d, candidate, label, endpoint) in enumerate(candidates, 1):
        print(" Candidate Solution ({}% match) {} / {}".format(int(d*100), i, len(candidates)))
        source = endpoint.identifier.toPython() if type(endpoint) is rdflib.graph.Graph else\
                re.sub('http(s)?://(www\.)?([a-zA-Z0-9\.-]*)/.*', r'\3', endpoint)
        print("\tSource: \t{}".format(source))
        print("\tCandidate: \t{}".format(label))

        q = ''
        while True:
            q = input(" Align? (y[es] / n[o] / m[ore info]) / s[kip] (*): ")
            if q == 'y':
                return (candidate, endpoint)
            elif q == 'n':
                break
            elif q == 'm':
                attrs = []
                if type(endpoint) is rdflib.graph.Graph:
                    attrs.extend([(pred, obj) for pred, obj in endpoint.predicate_objects(candidate)])
                else:  # SPARQL
                    qresults = query(endpoint, queryConstructorB(candidate))
                    attrs.extend((entry['pred']['value'], entry['obj']['value']) for entry in qresults)

                ask = True
                for pred, obj in attrs:
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
                return (None, None)

        candidate = None
        endpoint = None

    return (candidate, endpoint)
