#!/usr/bin/python3

from schema.protocol0102 import Protocol0102
from schema.vocab0102 import Vocabulary0102
from schema.schema0102 import Schema0102
import data.reader
import rdflib
import re


# compatible with SIKB protocol 0102 - version 3.1.0

def translate(ifile='', default_graphs=[], nsDefault=None, sikb_zip=None, gen_ontology=False, gen_vocabulary=False, ignore_version=False,\
             align='off', endpoint='', geosolv=False, interactive=True):
    et = data_raw = None
    gversion = ''
    if ifile != '':
        (et, data_raw, gversion) = data.reader.read_tree(ifile, ignore_version)
        genTreeNamespaces(et, gversion)

    schema0102_raw = None
    vocab0102_raw = None
    sversion = vversion = ''
    # enrich ontology
    if sikb_zip is not None:
        (schema0102_raw, sversion) = data.reader.read_zippedTree(sikb_zip, 'sikb/0102/3.1.0/sikb0102.xsd') \
                if gen_ontology else (None, '')
        (vocab0102_raw, vversion) = data.reader.read_zippedTree(sikb_zip, 'SIKB0102_Lookup.xml') \
                if gen_vocabulary else (None, '')

    if not ignore_version and ((ifile != '' and gen_ontology and gversion != sversion) or (ifile != '' and gen_vocabulary and gversion != vversion)):
        print('Warning: Version discrepancy between sources.')

    if len(default_graphs) > 0:
        default_graphs = graphImport(default_graphs)

    (nss, sikbns) = genGraphNamespaces(gversion, nsDefault)
    return convert(et, data_raw, default_graphs, nss, sikbns, schema0102_raw, vocab0102_raw, align, endpoint, geosolv,\
                   interactive)

def graphImport(graphs=[]):
    importedGraphs = []
    for i, path in enumerate(graphs, 1):
        print("Importing graph {} of {}...".format(i, len(graphs)), end="\r", flush=True)
        g = rdflib.Graph(identifier=re.sub('(.*/)?(.*)\..*', r'\2', path))
        importedGraphs.append(g.parse(path, format=rdflib.util.guess_format(path)))

    print()

    return importedGraphs


def genTreeNamespaces(et, version):
    et.register_namespace('sikb', 'http://www.sikb.nl/sikb0102/{0}'.format(version))
    et.register_namespace('gml', 'http://www.opengis.net/gml/3.2')
    et.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')


def genGraphNamespaces(version, nsDefault):
    return (dict([
        ('base', rdflib.Namespace(nsDefault)),
        ('bibo', rdflib.Namespace('http://purl.org/ontology/bibo/')),
        ('crm', rdflib.Namespace('http://www.cidoc-crm.org/cidoc-crm/')),
        ('crmeh', rdflib.Namespace('http://purl.org/crmeh#')),
        ('dc', rdflib.namespace.DC),
        ('dcterms', rdflib.namespace.DCTERMS),
        ('foaf', rdflib.namespace.FOAF),
        ('gn', rdflib.Namespace('http://www.geonames.org/ontology#')),
        ('geosparql', rdflib.Namespace('http://www.opengis.net/ont/geosparql#')),
        ('locn', rdflib.Namespace('http://www.w3.org/ns/locn#')),
        ('owl', rdflib.namespace.OWL),
        ('prism', rdflib.Namespace('http://prismstandard.org/namespaces/basic/2.1/')),
        ('rdf', rdflib.namespace.RDF),
        ('rdfs', rdflib.namespace.RDFS),
        ('skos', rdflib.namespace.SKOS),
        ('wgs84', rdflib.Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')),
        ('xsd', rdflib.namespace.XSD)]),\
        'http://www.sikb.nl/sikb0102/{0}'.format(version))


def convert(et, data_raw, default_graphs, nss, sikbns, schema0102_raw, vocab0102_raw, align, endpoint, geosolv,\
            interactive):
    s0102 = Schema0102(schema0102_raw, nss) if schema0102_raw is not None else None
    schmGraph = s0102.graph if s0102 is not None else None

    v0102 = Vocabulary0102(vocab0102_raw, nss) if vocab0102_raw is not None else None
    vocbGraph = v0102.graph if v0102 is not None else None

    p0102 = Protocol0102(et, data_raw, default_graphs, nss, sikbns, vocbGraph, align, endpoint, geosolv, interactive)\
            if data_raw is not None else None
    dataGraph = p0102.graph if p0102 is not None else None

    return (dataGraph, schmGraph, vocbGraph)

if __name__ == "__main__":
    pass
