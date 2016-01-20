#!/usr/bin/python3

import rdflib
import helpFunctions as hf
import re


class Protocol0102:

    def __init__(self, et, tree, namespace, gen_ontology, schema, vocab):
        self.et = et
        self.sikbns = '{' + namespace['sikb'] + '}'
        self.basens = namespace['base']
        self.ontology = None
        self.schema = schema
        self.vocab = vocab

        # export ontology if requested
        if gen_ontology:
            self.ontology = rdflib.Graph(identifier='SIKB_Protocol0102_Ontology')
            hf.setGraphNamespaceIDs(self.ontology, namespace)

        # root of protocol
        self.troot = tree.getroot()
        self.graph = rdflib.Graph(identifier='SIKBID_' + self.troot.attrib[self.sikbns + 'id'])

        hf.setGraphNamespaceIDs(self.graph, namespace)
        self.nss = dict(ns for ns in self.graph.namespace_manager.namespaces())

        self.groot = rdflib.URIRef(self.basens + 'SIKBID_' + hf.getID(self.troot, self.nss))

        # set type of protocol
        hf.addType(self.graph, self.groot, rdflib.URIRef(self.nss['crm'] + 'E31_Document'))

        # root attributes
        if self.sikbns + 'id' in self.troot.attrib.keys():  # id
            child = rdflib.Literal(self.troot.attrib[self.sikbns + 'id'], datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
            hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, self.groot, child, 'id', rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
        if 'versie' in self.troot.attrib.keys():  # versie
            child = rdflib.Literal(self.troot.attrib['versie'], datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
            hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, self.groot, child, 'versie', rdflib.URIRef(self.nss['prism'] + 'versionIdentifier'))
        if 'timestamp' in self.troot.attrib.keys():  # timestamp
            child = rdflib.Literal(self.troot.attrib['timestamp'], datatype=rdflib.URIRef(self.nss['xsd'] + 'dateTime'))
            hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, self.groot, child, 'timestamp', rdflib.URIRef(self.nss['dcterms'] + 'issued'))

        # root elements
        self.conceptHandler()

        (gproject, onode) = self.projectHandler(self.troot.find(self.sikbns + 'project'))
        for child in self.troot.iter(self.sikbns + 'projectlocatie'):
            self.projectlocatieHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'vindplaats'):
            self.vindplaatsHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'organisatie'):
            self.organisatieHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'persoon'):
            self.persoonHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'geolocatie'):
            self.geolocatieHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'dossier'):
            self.dossierHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'document'):
            self.documentHandler(child)
        for child in self.troot.iter(self.sikbns + 'bestand'):
            self.bestandHandler(onode, child)
        for child in self.troot.iter(self.sikbns + 'digitaalmedium'):
            self.digitaalmediumHandler(child)
        for child in self.troot.iter(self.sikbns + 'tekening'):
            self.tekeningHandler(child)
        for child in self.troot.iter(self.sikbns + 'foto'):
            self.fotoHandler(child)
        for child in self.troot.iter(self.sikbns + 'doos'):
            self.doosHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'verpakkingseenheid'):
            self.verpakkingseenheidHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'monster'):
            self.monsterHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'vondst'):
            self.vondstHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'veldvondst'):
            self.veldvondstHandler(child)
        for child in self.troot.iter(self.sikbns + 'vondstcontext'):
            self.vondstcontextHandler(child)
        for child in self.troot.iter(self.sikbns + 'boring'):
            self.boringHandler(child)
        for child in self.troot.iter(self.sikbns + 'vulling'):
            self.vullingHandler(child)
        for child in self.troot.iter(self.sikbns + 'structuur'):
            self.structuurHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'segment'):
            self.segmentHandler(child)
        for child in self.troot.iter(self.sikbns + 'spoor'):
            self.spoorHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'vak'):
            self.vakHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'stort'):
            self.stortHandler(child)
        for child in self.troot.iter(self.sikbns + 'planum'):
            self.planumHandler(child)
        for child in self.troot.iter(self.sikbns + 'put'):
            self.putHandler(child)
        for child in self.troot.iter(self.sikbns + 'hoogtemeting'):
            self.hoogtemetingHandler(gproject, child)
        #  for child in self.troot.iter(self.sikbns + 'waarneming'):
            #  self.waarnemingHandler(child)
        for child in self.troot.iter(self.sikbns + 'attribuut'):
            self.attribuutHandler(child)
        #  for child in self.troot.iter(self.sikbns + 'archis'):
            #  self.archisHandler(child)
        # for child in self.troot.iter(self.sikbns + 'attribuuttype'):
            #  self.attribuuttypeHandler(child)
        for child in self.troot.iter(self.sikbns + 'objectrelatie'):
            self.objectrelatieHandler(child)
        for child in self.troot.iter(self.sikbns + 'codereferentie'):
            self.codereferentieHandler(self.groot, child)

    def projectHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0001_EHProject'))
            hf.addProperty(self.graph, self.groot, gnode, rdflib.URIRef(self.nss['crm'] + 'P70_documents'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'projectnaam':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E41_Appellation'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by'))

            if child.tag == self.sikbns + 'startdatum':
                    bnode = hf.genID(self.graph, gnode, self.basens)
                    hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0021_EHProjectTimespan'))
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P4_has_time-span'))
                    hf.addLabel(self.graph, bnode, 'Time Span', 'nl')

                    cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                    hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, cnode, 'startdatum', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range

                    snode = tnode.find(self.sikbns + 'einddatum')
                    if snode is not None:
                        cnode = rdflib.Literal(hf.rawString(snode.text), datatype=rdflib.URIRef(self.nss['crm'] + 'EHE0091_Timestamp'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, cnode, 'einddatum', rdflib.URIRef(self.nss['crmeh'] + 'EXP2'))  # wrong range

            if child.tag == self.sikbns + 'onderzoeksmeldingsnummber':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E42_Identifier'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))

            if child.tag == self.sikbns + 'onderzoektype':
                key = 'verwerving'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E55_Type'))

                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)

            if child.tag == self.sikbns + 'omschrijving':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P3_has_note'))

            if child.tag == self.sikbns + 'bevoegdGezag':
                bnode = hf.genID(self.graph, gnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P11_had_participant'))
                hf.addLabel(self.graph, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for element in child:
                    if element.tag == self.sikbns + 'organisatieId':
                        (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, element)
                        if not exists:
                            hf.extractBasisTypeFields(self.graph, enode, element)
                            hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))

                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))
                    if element.tag == self.sikbns + 'persoonId':
                        (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, element)
                        if not exists:
                            hf.extractBasisTypeFields(self.graph, enode, element)
                            hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))

            if child.tag == self.sikbns + 'uitvoerder':
                bnode = hf.genID(self.graph, gnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P14_carried_out_by'))
                hf.addLabel(self.graph, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for element in child:
                    if element.tag == self.sikbns + 'uitvoerdercode':  #
                        key = 'uitvoerder'  # needed for inconsistent labeling by SIKB
                        enode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(element.text))
                        if self.ontology is not None:
                            hf.addLabel(self.ontology, enode, self.vocab[key][hf.rawString(element.text)], 'nl')
                            hf.addType(self.ontology, enode, rdflib.URIRef(self.nss['crm'] + 'E42_Identifier'))

                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by'))
                        hf.addRefIfExists(self.graph, enode, element)
                    if element.tag == self.sikbns + 'opgravingsleiderPersoonId':
                        (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, element)
                        if not exists:
                            hf.extractBasisTypeFields(self.graph, enode, element)
                            hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))
                    if element.tag == self.sikbns + 'depotContactPersoonId':
                        (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, element)
                        if not exists:
                            hf.extractBasisTypeFields(self.graph, enode, element)
                            hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))

        # add unexisting concept: 'production' and 'bestanden'
        bnode = hf.genID(self.graph, gnode, self.basens)
        hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E12_Production'))
        hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P9_consists_of'))
        hf.addLabel(self.graph, bnode, 'Documenteren (Digitaal)', 'nl')

        onode = hf.genID(self.graph, gnode, self.basens)
        hf.addType(self.graph, onode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))
        hf.addProperty(self.graph, bnode, onode, rdflib.URIRef(self.nss['crm'] + 'P108_has_produced'))
        hf.addLabel(self.graph, onode, 'Bestanden', 'nl')

        return (gnode, onode)

    def projectlocatieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0003_AreaOfInvestigation'))

        hf.addProperty(self.graph, pnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P7_took_place_at'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'provinciecode':
                key = 'provincie'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'gemeentecode':
                key = 'gemeente'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'plaatscode':
                key = 'plaats'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'toponiem':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0002_ArchaeologicalSite'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P59i_is_located_on_or_within'))
            if child.tag == self.sikbns + 'kaartblad':
                key = 'kaartblad'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E46_Section_Definition'))

                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'geolocatieId':
                (cnode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.addType(self.graph, cnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))

    def vindplaatsHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0004_SiteSubDivision'))

        hf.addProperty(self.graph, pnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P7_took_place_at'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'vondstmeldingsnummer':  # until direct linking in Archis is possible
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E42_Identifier'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by'))
            if child.tag == self.sikbns + 'waarnemingsnummer':  # until direct linking in Archis is possible
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E42_Identifier'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by'))
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P4_has_time-span'))
                    hf.addLabel(self.graph, bnode, 'Time Span', 'nl')

                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                    if self.ontology is not None:
                        hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                        hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                    hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, cnode, 'beginperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range
                    hf.addRefIfExists(self.graph, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        key = 'periode'  # needed for inconsistent labeling by SIKB
                        cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                        if self.ontology is not None:
                            hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(snode.text)], 'nl')
                            hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, cnode, 'eindperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP2'))  # wrong range
                        hf.addRefIfExists(self.graph, cnode, snode)
            if child.tag == self.sikbns + 'vindplaatstype':
                key = 'complextype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'geolocatieId':
                (cnode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.addType(self.graph, cnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))

    def dossierHandler(self, pnode, tnode):
        bnode = hf.genID(self.graph, pnode, self.basens)
        hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E12_Production'))
        hf.addProperty(self.graph, pnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P9_consists_of'))
        hf.addLabel(self.graph, bnode, 'Documenteren (Analoog)', 'nl')

        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))

        hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P108_has_produced'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'dossiertype':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
            if child.tag == self.sikbns + 'documentId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E31_Document'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P128_carries'))

    def bestandHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

        hf.addProperty(self.graph, pnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P128_carries'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['dcterms'] + 'isPartOf'))
            if child.tag == self.sikbns + 'bestandsnaam':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'title'))
            if child.tag == self.sikbns + 'bestandtype':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'format'))
            if child.tag == self.sikbns + 'bestandsinhoud':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'description'))
            if child.tag == self.sikbns + 'software':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'description'))
            if child.tag == self.sikbns + 'codeboek':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P67_refers_to'))
            if child.tag == self.sikbns + 'digitaalmediumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['dcterms'] + 'medium'))

    def digitaalmediumHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'digitaalmediumtype':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))

    def documentHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E31_Document'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'documenttype':
                key = 'documenttype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'titel':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'title'))
            if child.tag == self.sikbns + 'auteur':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'creator'))
            if child.tag == self.sikbns + 'jaar':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'gYear'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['prism'] + 'publicationDate'))
            if child.tag == self.sikbns + 'serie':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['prism'] + 'seriesTitle'))
            if child.tag == self.sikbns + 'paginas':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['prism'] + 'pageCount'))
            if child.tag == self.sikbns + 'uitgever':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'publisher'))
            if child.tag == self.sikbns + 'uitgavePlaats':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['dcterms'] + 'Location'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'spatial'))
            if child.tag == self.sikbns + 'redacteur':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['bibo'] + 'editor'))
            if child.tag == self.sikbns + 'titelContainer':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['prism'] + 'publicationName'))
            if child.tag == self.sikbns + 'issn':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['prism'] + 'issn'))
            if child.tag == self.sikbns + 'isbn':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['prism'] + 'isbn'))
            if child.tag == self.sikbns + 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P67_refers_to'))

    def organisatieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'naam':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E82_Actor_Appellation'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P131_is_identified_by'))
            if child.tag == self.sikbns + 'telefoon':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E51_Contact_Point'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P76_has_contact_point'))
            if child.tag == self.sikbns + 'email':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E51_Contact_Point'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P76_has_contact_point'))
            if child.tag == self.sikbns + 'contactpersoonId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))
            if child.tag == self.sikbns + 'adres':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['locn'] + 'Address'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['locn'] + 'address'))
                hf.addLabel(self.graph, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for element in child:
                    if element.tag == self.sikbns + 'straat':  # until index is available
                        enode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['gn'] + 'Feature'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['locn'] + 'thoroughfare'))
                        #gnnode = rdflib.URIRef(self.nss['gn'] + 'R.ST')
                        #hf.addProperty(self.graph, enode, gnnode, rdflib.URIRef(self.nss['gn'] + 'featureCode'))
                    if element.tag == self.sikbns + 'huisnummer':
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['locn'] + 'locatorDesignator'))
                    if element.tag == self.sikbns + 'postcode':
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['locn'] + 'postCode'))
                    if element.tag == self.sikbns + 'plaatsnaam':  # until index is available
                        enode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['gn'] + 'Feature'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['locn'] + 'postName'))
                        #gnnode = rdflib.URIRef(self.nss['gn'] + 'P.PPL')
                        #hf.addProperty(self.graph, enode, gnnode, rdflib.URIRef(self.nss['gn'] + 'featureCode'))
                    if element.tag == self.sikbns + 'gemeente':  # until index is available
                        enode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['gn'] + 'Feature'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['gn'] + 'parentADM2'))
                        #gnnode = rdflib.URIRef(self.nss['gn'] + 'A.ADM2')
                        #hf.addProperty(self.graph, enode, gnnode, rdflib.URIRef(self.nss['gn'] + 'featureCode'))
                    if element.tag == self.sikbns + 'provincie':  # until index is available
                        enode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['gn'] + 'Feature'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['gn'] + 'parentADM1'))
                        #gnnode = rdflib.URIRef(self.nss['gn'] + 'A.ADM1')
                        #hf.addProperty(self.graph, enode, gnnode, rdflib.URIRef(self.nss['gn'] + 'featureCode'))
                    if element.tag == self.sikbns + 'land':  # until index is available
                        enode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['gn'] + 'Feature'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['gn'] + 'parentCountry'))
                        #gnnode = rdflib.URIRef(self.nss['gn'] + 'A.PCLI')
                        #hf.addProperty(self.graph, enode, gnnode, rdflib.URIRef(self.nss['gn'] + 'featureCode'))

    def tekeningHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0016_RecordDrawing'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'tekeningtype':
                key = 'tekeningfototype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0081_RecordDrawingReferenceType'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'tekeningmateriaal':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'medium'))
            if child.tag == self.sikbns + 'tekeningformaat':
                key = 'papierformaat'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0079_RecordDrawingNote'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P3_has_note'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'tekenaar':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'creator'))
            if child.tag == self.sikbns + 'schaal':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0079_RecordDrawingNote'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P3_has_note'))
            if child.tag == self.sikbns + 'tekeningdatum':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'date'))
            if child.tag == self.sikbns + 'tekeningonderwerp':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'description'))
            if child.tag == self.sikbns + 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))  # for easy navigation
            if child.tag == self.sikbns + 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P70_documents'))
            if child.tag == self.sikbns + 'vondstId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))

    def fotoHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0017_RecordPhotograph'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'opnametype':
                key = 'tekeningfototype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0085_RecordPhotographReferenceType'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'opnamedatum':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'date'))
            if child.tag == self.sikbns + 'fotograaf':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'creator'))
            if child.tag == self.sikbns + 'opnamemedium':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'medium'))
            if child.tag == self.sikbns + 'fotoonderwerp':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'description'))
            if child.tag == self.sikbns + 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))  # for easy navigation
            if child.tag == self.sikbns + 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P70_documents'))
            if child.tag == self.sikbns + 'vondstId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))

    def doosHandler(self, pnode, tnode):
        bnode = hf.genID(self.graph, pnode, self.basens)
        hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E12_Production'))
        hf.addProperty(self.graph, pnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P9_consists_of'))
        hf.addLabel(self.graph, bnode, 'Verzamelen (Objecten)', 'nl')

        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))

        hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P108_has_produced'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'bewaarTemperatuur':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0041_ContextFindTreatmentProcedure'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))
            if child.tag == self.sikbns + 'bewaarVochtigheid':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0041_ContextFindTreatmentProcedure'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))
            if child.tag == self.sikbns + 'lichtgevoelig':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0041_ContextFindTreatmentProcedure'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))
            if child.tag == self.sikbns + 'breekbaar':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0041_ContextFindTreatmentProcedure'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))
            if child.tag == self.sikbns + 'gevaarlijkeStoffen':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0041_ContextFindTreatmentProcedure'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))

    def verpakkingseenheidHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0010_BulkFind'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'aantal':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'NonNegativeInteger'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P57_has_number_of_parts'))
            if child.tag == self.sikbns + 'gewicht':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, bnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P43_has_dimension'))
                hf.addLabel(self.graph, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['crm'] + 'E58_Measurement_Unit'))
                        hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE2021_BulkFindAssessment'))
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                    hf.addLabel(self.graph, bnode, 'Dateren', 'nl')

                    bnode2 = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))
                    hf.addLabel(self.graph, bnode2, 'Time Span', 'nl')

                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                    if self.ontology is not None:
                        hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                        hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                    hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode2, cnode, 'beginperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range
                    hf.addRefIfExists(self.graph, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        key = 'periode'  # needed for inconsistent labeling by SIKB
                        cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                        if self.ontology is not None:
                            hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(snode.text)], 'nl')
                            hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode2, cnode, 'eindperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP2'))  # wrong range
                        hf.addRefIfExists(self.graph, cnode, snode)
            if child.tag == self.sikbns + 'doosId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))

    def monsterHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0018_ContextSample'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'monstertype':
                key = 'monstertype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0053_ContextSampleType'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'monsterverwerking':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P3_has_note'))
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                    hf.addLabel(self.graph, bnode, 'Dateren', 'nl')

                    bnode2 = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))
                    hf.addLabel(self.graph, bnode2, 'Time Span', 'nl')

                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                    if self.ontology is not None:
                        hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                        hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                    hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode2, cnode, 'beginperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range
                    hf.addRefIfExists(self.graph, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        key = 'periode'  # needed for inconsistent labeling by SIKB
                        cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                        if self.ontology is not None:
                            hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(snode.text)], 'nl')
                            hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode2, cnode, 'eindperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range
                        hf.addRefIfExists(self.graph, cnode, snode)
            if child.tag == self.sikbns + 'verpakkingseenheidId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0010_BulkFind'))

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))
            if child.tag == self.sikbns + 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P53i_is_former_or_current_location_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P53_has_former_or_current_location'))

    def vondstHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'aantal':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0031_ContextFindMeasurement'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, bnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P43_has_dimension'))
                hf.addLabel(self.graph, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if child.tag == self.sikbns + 'gewicht':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0031_ContextFindMeasurement'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, bnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P43_has_dimension'))
                hf.addLabel(self.graph, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['crm'] + 'E58_Measurement_Unit'))
                        hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if child.tag == self.sikbns + 'materiaalcategorie':
                key = 'materiaalcategorie'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0030_ContextFindMaterial'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P45_consists_of'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'artefacttype':
                key = 'artefacttype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                    hf.addLabel(self.graph, bnode, 'Dateren', 'nl')

                    bnode2 = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crmeh'] + 'EHE0099_ContextFindUseEventTimespan'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))
                    hf.addLabel(self.graph, bnode2, 'Time Span', 'nl')

                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                    if self.ontology is not None:
                        hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                        hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                    hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode2, cnode, 'beginperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range
                    hf.addRefIfExists(self.graph, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        key = 'periode'  # needed for inconsistent labeling by SIKB
                        cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                        if self.ontology is not None:
                            hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(snode.text)], 'nl')
                            hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode2, cnode, 'eindperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range
                        hf.addRefIfExists(self.graph, cnode, snode)
            if child.tag == self.sikbns + 'geconserveerd':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E87_Curation_Activity'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P147i_was_curated_by'))
            if child.tag == self.sikbns + 'exposabel':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E87_Curation_Activity'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P147i_was_curated_by'))
            if child.tag == self.sikbns + 'gedeselecteerd':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E87_Curation_Activity'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P147i_was_curated_by'))
            if child.tag == self.sikbns + 'verpakkingseenheidId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0010_BulkFind'))

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))
            if child.tag == self.sikbns + 'veldvondstId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E78_Collectiono'))

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))

    def veldvondstHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'verzamelwijze':
                key = 'verzamelwijze'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0046_ContextNote'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P3_has_note'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P53_has_former_or_current_location'))

    def vondstcontextHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisLocatieTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'contexttype':
                key = 'contexttype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))
            if child.tag == self.sikbns + 'stortId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))
            if child.tag == self.sikbns + 'planumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))
            if child.tag == self.sikbns + 'vullingId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))
            if child.tag == self.sikbns + 'segmentId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))
            if child.tag == self.sikbns + 'vakId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))
            if child.tag == self.sikbns + 'boringId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))

        return gnode

    def boringHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))


    def vullingHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'vorm':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0059_ContextStuffNote'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P3_has_note'))
            if child.tag == self.sikbns + 'kleur':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0059_ContextStuffNote'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P3_has_note'))
            if child.tag == self.sikbns + 'textuur':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crmeh'] + 'EHE0059_ContextStuffNote'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P3_has_note'))
            if child.tag == self.sikbns + 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))

    def structuurHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'structuurtype':
                key = 'structuurtype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                    hf.addLabel(self.graph, bnode, 'Dateren', 'nl')

                    bnode2 = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))
                    hf.addLabel(self.graph, bnode2, 'Time Span', 'nl')

                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                    if self.ontology is not None:
                        hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                        hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                    hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode2, cnode, 'beginperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range
                    hf.addRefIfExists(self.graph, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        key = 'periode'  # needed for inconsistent labeling by SIKB
                        cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                        if self.ontology is not None:
                            hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(snode.text)], 'nl')
                            hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode2, cnode, 'eindperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range
                        hf.addRefIfExists(self.graph, cnode, snode)
            if child.tag == self.sikbns + 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P53_has_former_or_current_location'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P53i_is_former_or_current_location_of'))

    def segmentHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))

    def stortHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'putId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))
            if child.tag == self.sikbns + 'planumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))

    def planumHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'planumtype':
                key = 'planumtype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'putId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))

    def spoorHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'grondspoortype':
                key = 'grondspoortype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'diepte':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E16_Measurement'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P39i_was_measured_by'))
                hf.addLabel(self.graph, bnode, 'Meting', 'nl')

                bnode2 = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))
                hf.addLabel(self.graph, bnode2, 'Diepte', 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['crm'] + 'E58_Measurement_Unit'))
                        hf.addProperty(self.graph, bnode2, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                    hf.addLabel(self.graph, bnode, 'Dateren', 'nl')

                    bnode2 = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))
                    hf.addLabel(self.graph, bnode2, 'Time Span', 'nl')

                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                    if self.ontology is not None:
                        hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                        hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                    hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode2, cnode, 'beginperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range
                    hf.addRefIfExists(self.graph, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        key = 'periode'  # needed for inconsistent labeling by SIKB
                        cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                        if self.ontology is not None:
                            hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(snode.text)], 'nl')
                            hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode2, cnode, 'eindperiode', rdflib.URIRef(self.nss['crmeh'] + 'EXP1'))  # wrong range
                        hf.addRefIfExists(self.graph, cnode, snode)

    def putHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))


    def vakHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'vaknummer':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E41_Appellation'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by'))
            if child.tag == self.sikbns + 'dikte':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E16_Measurement'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P39i_was_measured_by'))
                hf.addLabel(self.graph, bnode, 'Meting', 'nl')

                bnode2 = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))
                hf.addLabel(self.graph, bnode2, 'Dikte', 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['crm'] + 'E58_Measurement_Unit'))
                        hf.addProperty(self.graph, bnode2, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if child.tag == self.sikbns + 'nap':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E16_Measurement'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P39i_was_measured_by'))
                hf.addLabel(self.graph, bnode, 'Meting', 'nl')

                bnode2 = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))
                hf.addLabel(self.graph, bnode2, 'Normaal Amsterdams Peil (NAP)', 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['crm'] + 'E58_Measurement_Unit'))
                        hf.addProperty(self.graph, bnode2, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if child.tag == self.sikbns + 'planumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))

    def persoonHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'telefoon':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E51_Contact_Point'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P76_has_contact_point'))
            if child.tag == self.sikbns + 'email':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E51_Contact_Point'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P76_has_contact_point'))
            if child.tag == self.sikbns + 'naam':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['foaf'] + 'Person'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, bnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P131_is_identified_by'))
                hf.addLabel(self.graph, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for element in child:
                    if element.tag == self.sikbns + 'achternaam':
                        snode = child.find(self.sikbns + 'tussenvoegsel')
                        value = element.text + ', ' + snode.text if snode is not None else element.text  # extract 'tussenvoegsel' if available

                        enode = rdflib.Literal(value, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['foaf'] + 'familyName'))
                    if element.tag == self.sikbns + 'voornaam':
                        snode = child.find(self.sikbns + 'initialen')
                        value = element.text + ', ' + snode.text if snode is not None else element.text  # extract 'initialen' if available

                        enode = rdflib.Literal(value, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['foaf'] + 'givenName'))
                    if element.tag == self.sikbns + 'initialen':
                        snode = child.find(self.sikbns + 'voornaam')
                        if snode is None:
                            enode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))

                            hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['foaf'] + 'givenName'))
                    if element.tag == self.sikbns + 'titel':
                        enode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, bnode, enode, re.sub(self.sikbns, '', element.tag).title(), rdflib.URIRef(self.nss['foaf'] + 'title'))

    def geolocatieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractGeoObjectFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'geometrie':
                cnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, cnode, rdflib.URIRef(self.nss['geosparql'] + 'Geometry'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))

                gmlnode = rdflib.Literal(hf.gmlLiteralOf(self.et, child), datatype=rdflib.URIRef(self.nss['geosparql'] + 'GMLLiteral'))
                hf.addProperty(self.graph, cnode, gmlnode, rdflib.URIRef(self.nss['geosparql'] + 'asGML'))

    def hoogtemetingHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'methode':
                key = 'hoogtemetingmethode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                if self.ontology is not None:
                    hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                    hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))
                hf.addRefIfExists(self.graph, cnode, child)
            if child.tag == self.sikbns + 'nap':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, bnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))
                hf.addLabel(self.graph, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['crm'] + 'E58_Measurement_Unit'))
                        hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

    def attribuutHandler(self, tnode):
        child = tnode.find(self.sikbns + 'objectId')
        (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
        if not exists:
            hf.extractGenericObjectFields(self.graph, enode, child)
            hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E1_CRM_Entity'))

        value = None
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'geheelgetal':
                value = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'integer'))
            if child.tag == self.sikbns + 'decimaalgetal':
                value = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
            if child.tag == self.sikbns + 'referentieId':
                value = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
            if child.tag == self.sikbns + 'text':
                value = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
            if child.tag == self.sikbns + 'jaNee':
                value = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))

        atypeID = tnode.find(self.sikbns + 'attribuuttypeId').text
        atype = None
        for atnode in self.troot.findall(self.sikbns + 'attribuuttype'):
            if atnode.attrib[self.sikbns + 'id'] == atypeID:
                atype = atnode
                break

        if atype is not None:
            pname = 'SIKBID_'+ rdflib.BNode()
            for child in atype.getchildren():
                if child.tag == self.sikbns + 'attribuutnaam':
                    pname = rdflib.Literal(hf.rawString(child.text))

            hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, enode, value, pname, rdflib.URIRef(self.nss['rdf'] + 'value'))

            for child in atype.getchildren():
                if child.tag == self.sikbns + 'informatie':
                    info = rdflib.Literal(hf.rawString(child.text), lang='nl')
                    hf.addProperty(self.graph, rdflib.URIRef(self.basens + pname), info, rdflib.URIRef(self.nss['rdfs'] + 'comment'))
                if child.tag == self.sikbns + 'waardetype':
                    key = 'waardetype'  # needed for inconsistent labeling by SIKB
                    cnode = rdflib.URIRef(self.basens + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                    if self.ontology is not None:
                        hf.addLabel(self.ontology, cnode, self.vocab[key][hf.rawString(child.text)], 'nl')
                        hf.addType(self.ontology, cnode, rdflib.URIRef(self.nss['crm'] + 'E55_Type'))
                    hf.addProperty(self.graph, rdflib.URIRef(self.basens + pname), cnode, rdflib.URIRef(self.nss['crm'] + 'P2_has_type'))

    def objectrelatieHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['owl'] + 'ObjectProperty'))

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'objectrelatietype':
                relation = child.text.title()
                object1Class = 'Thing'
                object2Class = 'Thing'

                snode = tnode.find(self.sikbns + 'object1Class')
                if snode is not None:
                    object1Class = snode.text.title()

                snode2 = tnode.find(self.sikbns + 'object2Class')
                if snode2 is not None:
                    object2Class = snode.text.title()

                cnode = rdflib.Literal(relation + '(' + object1Class + ', ' + object2Class + ')', lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.nss['rdfs'] + 'comment'))

            if child.tag == self.sikbns + 'object1Id':
                    (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                    if not exists:
                        hf.extractGenericObjectFields(self.graph, enode, child)
                        hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E1_CRM_Entity'))

                    snode = tnode.find(self.sikbns + 'object2Id')
                    if snode is not None:
                        (enode2, exists) = hf.getNodeFromElem(self.graph, self.basens, snode)
                        if not exists:
                            hf.extractGenericObjectFields(self.graph, enode2, snode)
                            hf.addType(self.graph, enode2, rdflib.URIRef(self.nss['crm'] + 'E1_CRM_Entity'))

                        object1Class = hf.getNodeClass(self.graph, enode)
                        if object1Class is not None:
                            hf.addProperty(self.graph, gnode, object1Class, rdflib.URIRef(self.nss['rdfs'] + 'domain'))
                        object2Class = hf.getNodeClass(self.graph, enode2)
                        if object2Class is not None:
                            hf.addProperty(self.graph, gnode, object2Class, rdflib.URIRef(self.nss['rdfs'] + 'range'))

                        # add new relation to specified resources
                        hf.addProperty(self.graph, enode, enode2, gnode)

    def codereferentieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, tnode)
        if not exists:
            hf.extractGenericObjectFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document'))

        hf.addProperty(self.graph, self.groot, gnode, rdflib.URIRef(self.nss['crm'] + 'P67_refers_to'))
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'bronCode':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E33_Linguistic_Object'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))
            if child.tag == self.sikbns + 'standaardCode':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E75_Conceptual_Object_Appellation'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by'))
            if child.tag == self.sikbns + 'bronOmschrijving':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, cnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['dcterms'] + 'description'))
            if child.tag == self.sikbns + 'bronCodeLijst':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, bnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P71i_is_listed_in'))
                hf.addLabel(self.graph, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E41_Appellation'))
                hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by'))
            if child.tag == self.sikbns + 'naamCodeLijst':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document'))
                hf.addSubPropertyIfExists(self.graph, self.ontology, self.schema, self.basens, gnode, bnode, re.sub(self.sikbns, '', child.tag).title(), rdflib.URIRef(self.nss['crm'] + 'P71i_is_listed_in'))
                hf.addLabel(self.graph, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['crm'] + 'E41_Appellation'))
                hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by'))
            if child.tag == self.sikbns + 'historyId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractGenericObjectFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['rdfs'] + 'subClassOf'))

    def conceptHandler(self):
        # existing concepts
        for element in self.troot:
            child = rdflib.URIRef(self.basens + 'SIKBID_' + hf.getID(element, self.nss))

            # if element.tag == self.sikbns + 'archis':
            #    hf.extractBasisTypeFields(self.graph, child, element)
            #    hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))
            if element.tag == self.sikbns + 'bestand':
                hf.extractBasisTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))
            if element.tag == self.sikbns + 'boring':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))
            if element.tag == self.sikbns + 'digitaalmedium':
                hf.extractBasisTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))
            if element.tag == self.sikbns + 'document':
                hf.extractBasisTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E31_Document'))
            if element.tag == self.sikbns + 'doos':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))
            if element.tag == self.sikbns + 'dossier':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))
            if element.tag == self.sikbns + 'foto':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0017_RecordPhotograph'))
            if element.tag == self.sikbns + 'geolocatie':
                hf.extractGeoObjectFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))
            if element.tag == self.sikbns + 'hoogtemeting':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
            if element.tag == self.sikbns + 'monster':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0018_ContextSample'))
            if element.tag == self.sikbns + 'organisatie':
                hf.extractBasisTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))
            if element.tag == self.sikbns + 'persoon':
                hf.extractBasisTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E21_Person'))
            if element.tag == self.sikbns + 'planum':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))
            if element.tag == self.sikbns + 'project':
                hf.extractBasisTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0001_EHProject'))
            if element.tag == self.sikbns + 'projectlocatie':
                hf.extractBasisTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0003_AreaOfInvestigation'))
            if element.tag == self.sikbns + 'put':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))
            if element.tag == self.sikbns + 'segment':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))
            if element.tag == self.sikbns + 'spoor':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))
            if element.tag == self.sikbns + 'stort':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))
            if element.tag == self.sikbns + 'structuur':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0006_GroupStuff'))
            if element.tag == self.sikbns + 'tekening':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0016_RecordDrawing'))
            if element.tag == self.sikbns + 'vak':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))
            if element.tag == self.sikbns + 'veldvondst':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))
            if element.tag == self.sikbns + 'verpakkingseenheid':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0010_BulkFind'))
            if element.tag == self.sikbns + 'vindplaats':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0004_SiteSubDivision'))
            if element.tag == self.sikbns + 'vondst':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))
            if element.tag == self.sikbns + 'vondstcontext':
                hf.extractBasisLocatieTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))
            if element.tag == self.sikbns + 'vulling':
                hf.extractBasisNaamTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))
            # if element.tag == self.sikbns + 'waarneming':
            #    hf.extractBasisLocatieTypeFields(self.graph, child, element)
            #    hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E5_Event'))
            # if element.tag == self.sikbns + 'attribuuttype':
            #    hf.extractGenericObjectFields(self.graph, child, element)
            #    hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E89_Propositional_Object'))
            # if element.tag == self.sikbns + 'attribuut':
            #    hf.extractGenericObjectFields(self.graph, child, element)
            #    hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E1_CRM_Entity'))
            if element.tag == self.sikbns + 'objectrelatie':
                hf.extractBasisTypeFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['owl'] + 'ObjectProperty'))
            if element.tag == self.sikbns + 'codereferentie':
                hf.extractGenericObjectFields(self.graph, child, element)
                hf.addType(self.graph, child, rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document'))
