#!/usr/bin/python3

from schema.protocol0102 import Protocol0102
import data.reader
import rdflib
import re


# compatible with SIKB protocol 0102 - version 3.1.0

def translate(et=None, tree=None, version=None, nsDefault=None, sikb_zip=None, gen_ontology=False):
    if tree is None or et is None:
        raise ValueError()

    types = ('artefacttype', 'materiaalcategorie', 'periode', 'verzamelwijze', 'complextype', 'verwerving',
             'tekeningfototype', 'monstertype', 'gemeente', 'provincie', 'kaartblad', 'documenttype', 'contexttype',
             'grondspoortype', 'archistype', 'hoogtemetingmethode', 'waarnemingmethode', 'objectrelatietype',
             'papierformaat', 'plaats', 'planumtype', 'structuurtype', 'waardetype', 'uitvoerder')

    vocab = {vtype: None for vtype in types}
    schema0102 = dict()
    # enrich ontology
    if sikb_zip is not None:
        schema0102_raw = data.reader.read_zippedTree(sikb_zip, 'sikb/0102/3.1.0/sikb0102.xsd')
        xmlns = re.sub(r'(\{.*\})schema', r'\1', schema0102_raw.tag)

        schema0102 = {e.attrib['name']:attr.text \
                      for e in schema0102_raw.iter(xmlns + 'element') \
                      for attr in e.iter(xmlns + 'documentation')}

        lookup0102_raw = data.reader.read_zippedTree(sikb_zip, 'SIKB0102_Lookup.xml')
        xmlns = re.sub(r'(\{.*\})lookup', r'\1', lookup0102_raw.tag)
        for t in vocab.keys():
            vocab[t] = {codex[0].text: codex[1].text for codex in lookup0102_raw.iter(xmlns+t)}

    genTreeNamespaces(et, version)
    nss = genGraphNamespaces(version, nsDefault)
    return convert(et, tree, nss, gen_ontology, schema0102, vocab)


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


def convert(et, tree, ns, gen_ontology, schema0102, vocab):
    p0102 = Protocol0102(et, tree, ns, gen_ontology, schema0102, vocab)
    return (p0102.graph, p0102.ontology)

if __name__ == "__main__":
    pass
