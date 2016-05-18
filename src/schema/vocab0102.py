#!/usr/bin/python3

import rdflib
import helpFunctions as hf
import re


class Vocabulary0102:

    def __init__(self, troot, namespace):
        self.troot = troot
        self.basens = namespace['base'] + 'voc/'
        self.nss = namespace
        self.ns = re.sub(r'(\{.*\})lookup', r'\1', troot.tag)

        types = {'archistypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_type'),
               'artefacttypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'complextypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'contexttypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'documenttypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'gemeenteCodelijst': rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'),
               'grondspoortypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'hoogtemetingmethodeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'kaartbladCodelijst': rdflib.URIRef(self.nss['crm'] + 'E46_Section_Definition'),
               'materiaalcategorieCodelijst': rdflib.URIRef(self.nss['crmeh'] + 'EHE0030_ContextFindMaterial'),
               'monstertypeCodelijst': self.nss['crmeh'] + 'EHE0053_ContextSampleType',
               'objectrelatietypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'papierformaatCodelijst': rdflib.URIRef(self.nss['crmeh'] + 'EHE0079_RecordDrawingNote'),
               'periodeCodelijst': rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'),
               'plaatsCodelijst': rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'),
               'planumtypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'provincieCodelijst': rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'),
               'structuurtypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'tekeningfototypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'uitvoerderCodelijst': rdflib.URIRef(self.nss['crm'] + 'E42_Identifier'),
               'verwervingCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'verzamelwijzeCodelijst': rdflib.URIRef(self.nss['crmeh'] + 'EHE0046_ContextNote'),
               'waardetypeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type'),
               'waarnemingmethodeCodelijst': rdflib.URIRef(self.nss['crm'] + 'E55_Type')}

        # new graph
        self.graph = rdflib.Graph(identifier='SIKB0102_' + 'Vocabulary')

        hf.setGraphNamespaceIDs(self.graph, namespace)
        self.nss = dict(ns for ns in self.graph.namespace_manager.namespaces())

        self.groot = rdflib.URIRef(self.basens + 'SIKB0102_' + 'Vocabulary')

        # set type of protocol
        hf.addType(self.graph, self.groot, rdflib.URIRef(self.nss['skos'] + 'ConceptScheme'))

        # root attributes
        child = rdflib.Literal('Codelijsten SIKB Archaeologisch Protocol 0102', 'nl')
        hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['dcterms'] + 'title'))
        hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['skos'] + 'prefLabel'))
        if 'versie' in self.troot.attrib.keys():  # versie
            child = rdflib.Literal(self.troot.attrib['versie'], datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
            hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['prism'] + 'versionIdentifier'))
        if 'datum' in self.troot.attrib.keys():  # datum
            child = rdflib.Literal(self.troot.attrib['datum'], datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
            hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['dcterms'] + 'issued'))

        # for each codelist
        for codelist in list(self.troot) :
            label = re.sub(r'\{.*\}([a-zA-Z]*)', r'\1', codelist.tag)
            node = rdflib.URIRef(self.basens + 'SIKB_' + label.title())
            hf.addType(self.graph, node, rdflib.URIRef(self.nss['skos'] + 'Concept'))
            hf.addProperty(self.graph, node, self.groot, rdflib.URIRef(self.nss['skos'] + 'inScheme'))

            lnode = rdflib.Literal(label.title(), lang='nl')
            hf.addProperty(self.graph, node , lnode, rdflib.URIRef(self.nss['skos'] + 'prefLabel'))
            hf.addProperty(self.graph, node , lnode, rdflib.URIRef(self.nss['rdfs'] + 'label'))

            hf.addProperty(self.graph, node, self.groot, rdflib.URIRef(self.nss['skos'] + 'topConceptOf'))
            hf.addProperty(self.graph, self.groot, node, rdflib.URIRef(self.nss['skos'] + 'hasTopConcept'))

            if 'versie' in codelist.attrib.keys():  # versie
                child = rdflib.Literal(codelist.attrib['versie'], datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, node, child, rdflib.URIRef(self.nss['prism'] + 'versionIdentifier'))
            if 'datum' in codelist.attrib.keys():  # datum
                child = rdflib.Literal(codelist.attrib['datum'], datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                hf.addProperty(self.graph, node , child, rdflib.URIRef(self.nss['dcterms'] + 'issued'))
            if 'omschrijving' in codelist.attrib.keys():  # omschrijving
                child = rdflib.Literal(hf.rawString(codelist.attrib['omschrijving']), 'nl')
                hf.addProperty(self.graph, node , child, rdflib.URIRef(self.nss['skos'] + 'scopeNote'))

            # for each entry in the codelist
            for entry in list(codelist):
                clabel = re.sub('/', '-', entry[0].text)
                code = rdflib.URIRef(self.basens + 'SIKB_Code_' \
                                     + codelist.attrib['naam'].title() \
                                     + '_' + clabel)
                lcnode = rdflib.Literal(codelist.attrib['naam'].title() + ' ' + clabel.upper(), lang='nl')
                hf.addProperty(self.graph, code, lcnode, rdflib.URIRef(self.nss['skos'] + 'prefLabel'))
                hf.addProperty(self.graph, code, lcnode, rdflib.URIRef(self.nss['rdfs'] + 'label'))
                hf.addProperty(self.graph, code, node, rdflib.URIRef(self.nss['skos'] + 'inScheme'))
                hf.addType(self.graph, code, rdflib.URIRef(self.nss['skos'] + 'Concept'))
                hf.addType(self.graph, code, rdflib.URIRef(types[label]))

                definition = rdflib.Literal(hf.rawString(entry[1].text), 'nl')
                hf.addProperty(self.graph, code, definition, rdflib.URIRef(self.nss['skos'] + 'scopeNote'))

                if 'versie' in entry.attrib.keys():  # versie
                    child = rdflib.Literal(entry.attrib['versie'], datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                    hf.addProperty(self.graph, code, child, rdflib.URIRef(self.nss['prism'] + 'versionIdentifier'))
                if 'datum' in entry.attrib.keys():  # datum
                    child = rdflib.Literal(entry.attrib['datum'], datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                    hf.addProperty(self.graph, code , child, rdflib.URIRef(self.nss['dcterms'] + 'issued'))
                if 'status' in entry.attrib.keys():  # status
                    child = rdflib.Literal(entry.attrib['status'], 'nl')
                    hf.addProperty(self.graph, code , child, rdflib.URIRef(self.nss['skos'] + 'note'))

                lablist = re.split('\.', clabel)
                if len(lablist) >= 2:
                    broadcode = rdflib.URIRef(self.basens + 'SIKB_Code_' \
                                         + codelist.attrib['naam'].title() \
                                         + '_' + lablist[0])
                    hf.addProperty(self.graph, code, broadcode, rdflib.URIRef(self.nss['skos'] + 'broader'))
                    hf.addProperty(self.graph, broadcode, code, rdflib.URIRef(self.nss['skos'] + 'narrower'))
                    # TODO: only do for existing broader relation
                else:
                    hf.addProperty(self.graph, code, node, rdflib.URIRef(self.nss['skos'] + 'topConceptOf'))
                    hf.addProperty(self.graph, node, code, rdflib.URIRef(self.nss['skos'] + 'hasTopConcept'))

                if len(entry) > 2 and re.sub(r'\{.*\}([a-z][A-Z]*)', r'\1', entry[2].tag) == 'nieuweCode':
                    altlabel = re.sub('/', '-', entry[2].text)
                    altcode = rdflib.URIRef(self.basens + 'SIKB_Code_' \
                                     + codelist.attrib['naam'].title() \
                                     + '_' + altlabel)

                    altlabelnode = rdflib.Literal(codelist.attrib['naam'].title() + ' ' + altlabel.upper(), lang='nl')
                    hf.addProperty(self.graph, altcode, altlabelnode, rdflib.URIRef(self.nss['skos'] + 'prefLabel'))
                    hf.addProperty(self.graph, altcode, node, rdflib.URIRef(self.nss['skos'] + 'inScheme'))
                    hf.addType(self.graph, altcode, rdflib.URIRef(self.nss['skos'] + 'Concept'))
                    hf.addType(self.graph, altcode, rdflib.URIRef(types[label]))

                    hf.addProperty(self.graph, altcode, node, rdflib.URIRef(self.nss['skos'] + 'topConceptOf'))
                    hf.addProperty(self.graph, node, altcode, rdflib.URIRef(self.nss['skos'] + 'hasTopConcept'))

                    note = rdflib.Literal('Nieuwe code van {} {}'.format(re.sub(r'\{.*\}([a-z]*)[A-Za-z]*', r'\1',\
                                                                                codelist.tag).title(), clabel), 'nl')
                    hf.addProperty(self.graph, altcode, note, rdflib.URIRef(self.nss['skos'] + 'note'))

                    note = rdflib.Literal('Heeft nieuwe code {}'.format(altlabel), 'nl')
                    hf.addProperty(self.graph, code, note, rdflib.URIRef(self.nss['skos'] + 'note'))

                    hf.addProperty(self.graph, altcode, code, rdflib.URIRef(self.nss['owl'] + 'sameAs'))
                    hf.addProperty(self.graph, code, altcode, rdflib.URIRef(self.nss['owl'] + 'sameAs'))

