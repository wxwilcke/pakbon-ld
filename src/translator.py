#!/usr/bin/python3

from schema.protocol0102 import Protocol0102
import rdflib


# compatible with SIKB protocol 0102 - version 3.1.0

def translate(et=None, tree=None, version=None, nsDefault=None):
    if tree is None or et is None:
        raise ValueError()

    genTreeNamespaces(et, version)
    nss = genGraphNamespaces(version, nsDefault)
    return convert(et, tree, nss)


def genTreeNamespaces(et, version):
    et.register_namespace('sikb', 'http://www.sikb.nl/sikb0102/{0}'.format(version))
    et.register_namespace('gml', 'http://www.opengis.net/gml/3.2')
    et.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')


def genGraphNamespaces(version, nsDefault):
    return dict([
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
        ('sikb', rdflib.Namespace('http://www.sikb.nl/sikb0102/{0}'.format(version))),
        ('xsd', rdflib.namespace.XSD)])


def convert(et, tree, ns):
    p0102 = Protocol0102(et, tree, ns)
    return p0102.graph

if __name__ == "__main__":
    pass
