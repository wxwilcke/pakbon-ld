#!/usr/bin/python3

import rdflib
import helpFunctions as hf
import re


class Protocol0102:

    def __init__(self, et, tree, namespace):
        self.et = et
        self.namespace = namespace
        self.sikbns = '{' + self.namespace['sikb'] + '}'

        # root of protocol
        self.troot = tree.getroot()
        self.graph = rdflib.Graph(identifier=self.troot.attrib[self.sikbns + 'id'])

        hf.setGraphNamespaceIDs(self.graph, self.namespace)


        self.groot = rdflib.URIRef(self.namespace['base'] + hf.getID(self.troot, self.namespace))

        # set type of protocol
        hf.addType(self.graph, self.namespace, self.groot, self.namespace['crm'].E31_Document)

        # root attributes
        if self.sikbns + 'id' in self.troot.attrib.keys():  # id
            child = rdflib.Literal(self.troot.attrib[self.sikbns + 'id'])
            hf.addProperty(self.graph, self.groot, child, self.namespace['crm'].P48_has_preferred_identifier)
            hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E42_Identifier)
        if 'versie' in self.troot.attrib.keys():  # versie
            child = rdflib.Literal(self.troot.attrib['versie'])
            hf.addProperty(self.graph, self.groot, child, self.namespace['prism'].versionIdentifier)
            hf.addType(self.graph, self.namespace, child, self.namespace['xsd'].string)
        if 'timestamp' in self.troot.attrib.keys():  # timestamp
            child = rdflib.Literal(self.troot.attrib['timestamp'])
            hf.addProperty(self.graph, self.groot, child, self.namespace['dcterms'].issued)
            hf.addType(self.graph, self.namespace, child, self.namespace['xsd'].dateTime)

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
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0001_EHProject)
            hf.addProperty(self.graph, self.groot, gnode, self.namespace['crm'].P70_documents)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'projectnaam':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E41_Appellation)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P1_is_identified_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

            if child.tag == self.sikbns + 'startdatum':
                    bnode = hf.genID(self.graph, self.namespace, gnode)
                    hf.addType(self.graph, self.namespace, bnode, rdflib.URIRef(self.namespace['crmeh'] + 'EHE0021_EHProjectTimespan'))
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.namespace['crm'] + 'P4_has_time-span'))
                    hf.addLabel(self.graph, self.namespace, bnode, 'Time Span', 'nl')

                    cnode = rdflib.Literal(child.text)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].date)
                    hf.addProperty(self.graph, bnode, cnode, self.namespace['crmeh'].EXP1)  # wrong range
                    hf.addLabel(self.graph, self.namespace, cnode, 'Startdatum', 'nl')

                    snode = tnode.find(self.sikbns + 'einddatum')
                    if snode is not None:
                        cnode = rdflib.Literal(snode.text)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].date)
                        hf.addProperty(self.graph, bnode, cnode, self.namespace['crmeh'].EXP2)  # wrong range
                        hf.addLabel(self.graph, self.namespace, cnode, 'Einddatum', 'nl')

            if child.tag == self.sikbns + 'onderzoeksmeldingsnummber':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E42_Identifier)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P48_has_preferred_identifier)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

            if child.tag == self.sikbns + 'onderzoektype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)

            if child.tag == self.sikbns + 'omschrijving':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['rdfs'].Literal)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P3_has_note)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

            if child.tag == self.sikbns + 'bevoegdGezag':
                bnode = hf.genID(self.graph, self.namespace, gnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E40_Legal_Body)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P11_had_participant)
                hf.addLabel(self.graph, self.namespace, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for element in child:
                    if element.tag == self.sikbns + 'organisatieId':
                        (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, element)
                        if not exists:
                            hf.extractBasisTypeFields(self.graph, self.namespace, enode, element)
                            hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E40_Legal_Body)

                        hf.addProperty(self.graph, bnode, enode, self.namespace['crm'].P107_has_current_or_former_member)
                    if element.tag == self.sikbns + 'persoonId':
                        (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, element)
                        if not exists:
                            hf.extractBasisTypeFields(self.graph, self.namespace, enode, element)
                            hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E21_Person)

                        hf.addProperty(self.graph, bnode, enode, self.namespace['crm'].P107_has_current_or_former_member)

            if child.tag == self.sikbns + 'uitvoerder':
                bnode = hf.genID(self.graph, self.namespace, gnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E40_Legal_Body)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P14_carried_out_by)
                hf.addLabel(self.graph, self.namespace, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for element in child:
                    if element.tag == self.sikbns + 'uitvoerdercode':  # until index is available
                        enode = rdflib.Literal(element.text)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E42_Identifier)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['crm'].P1_is_identified_by)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                        hf.addRefIfExists(self.graph, self.namespace, enode, element)
                    if element.tag == self.sikbns + 'opgravingsleiderPersoonId':
                        (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, element)
                        if not exists:
                            hf.extractBasisTypeFields(self.graph, self.namespace, enode, element)
                            hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E21_Person)

                        hf.addProperty(self.graph, bnode, enode, self.namespace['crm'].P107_has_current_or_former_member)
                    if element.tag == self.sikbns + 'depotContactPersoonId':
                        (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, element)
                        if not exists:
                            hf.extractBasisTypeFields(self.graph, self.namespace, enode, element)
                            hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E21_Person)

                        hf.addProperty(self.graph, bnode, enode, self.namespace['crm'].P107_has_current_or_former_member)

        # add unexisting concept: 'production' and 'bestanden'
        bnode = hf.genID(self.graph, self.namespace, gnode)
        hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E12_Production)
        hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P9_consists_of)
        hf.addLabel(self.graph, self.namespace, bnode, 'Documenteren (Digitaal)', 'nl')

        onode = hf.genID(self.graph, self.namespace, gnode)
        hf.addType(self.graph, self.namespace, onode, self.namespace['crm'].E84_Information_Carrier)
        hf.addProperty(self.graph, bnode, onode, self.namespace['crm'].P108_has_produced)
        hf.addLabel(self.graph, self.namespace, onode, 'Bestanden', 'nl')

        return (gnode, onode)

    def projectlocatieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0003_AreaOfInvestigation)

        hf.addProperty(self.graph, pnode, gnode, self.namespace['crm'].P7_took_place_at)
        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'provinciecode':  # until index is available
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E44_Place_Appellation)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P89_falls_within)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'gemeentecode':  # until index is available
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E44_Place_Appellation)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P89_falls_within)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'plaatscode':  # until index is available
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E44_Place_Appellation)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P89_falls_within)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'toponiem':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0002_ArchaeologicalSite)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P59i_is_located_on_or_within)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'kaartblad':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E46_Section_Definition)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P87_is_identified_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'geolocatieId':
                (cnode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E44_Place_Appellation)

                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P87_is_identified_by)

    def vindplaatsHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0004_SiteSubDivision)

        hf.addProperty(self.graph, pnode, gnode, self.namespace['crm'].P7_took_place_at)
        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'vondstmeldingsnummer':  # until direct linking in Archis is possible
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E42_Identifier)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P1_is_identified_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'waarnemingsnummer':  # until direct linking in Archis is possible
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E42_Identifier)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P1_is_identified_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode, rdflib.URIRef(self.namespace['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.namespace['crm'] + 'P4_has_time-span'))
                    hf.addLabel(self.graph, self.namespace, bnode, 'Time Span', 'nl')

                    cnode = rdflib.Literal(child.text)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                    hf.addProperty(self.graph, bnode, cnode, self.namespace['crmeh'].EXP1)  # wrong range
                    hf.addLabel(self.graph, self.namespace, cnode, 'Beginperiode', 'nl')
                    hf.addRefIfExists(self.graph, self.namespace, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        cnode = rdflib.Literal(snode.text)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                        hf.addProperty(self.graph, bnode, cnode, self.namespace['crmeh'].EXP2)  # wrong range
                        hf.addLabel(self.graph, self.namespace, cnode, 'Eindperiode', 'nl')
                        hf.addRefIfExists(self.graph, self.namespace, cnode, snode)
            if child.tag == self.sikbns + 'vindplaatstype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'geolocatieId':
                (cnode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E44_Place_Appellation)

                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P87_is_identified_by)

    def dossierHandler(self, pnode, tnode):
        bnode = hf.genID(self.graph, self.namespace, pnode)
        hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E12_Production)
        hf.addProperty(self.graph, pnode, bnode, self.namespace['crm'].P9_consists_of)
        hf.addLabel(self.graph, self.namespace, bnode, 'Documenteren (Analoog)', 'nl')

        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E84_Information_Carrier)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        hf.addProperty(self.graph, bnode, gnode, self.namespace['crm'].P108_has_produced)

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'dossiertype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'documentId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E31_Document)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P128_carries)

    def bestandHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E73_Information_Object)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        hf.addProperty(self.graph, pnode, gnode, self.namespace['crm'].P128_carries)

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E73_Information_Object)

                hf.addProperty(self.graph, gnode, enode, self.namespace['dcterms'].isPartOf)
            if child.tag == self.sikbns + 'bestandsnaam':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].title)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'bestandtype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.namespace['dcterms'] + 'format'))
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'bestandsinhoud':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].description)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'software':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].description)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'codeboek':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E73_Information_Object)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P67_refers_to)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'digitaalmediumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E84_Information_Carrier)

                hf.addProperty(self.graph, gnode, enode, self.namespace['dcterms'].medium)

    def digitaalmediumHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E84_Information_Carrier)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'digitaalmediumtype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

    def documentHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E31_Document)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'documenttype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'titel':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].title)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'auteur':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].creator)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'jaar':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].gYear)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['prism'].publicationDate)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'serie':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['prism'].seriesTitle)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'paginas':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].positiveInteger)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['prism'].pageCount)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'uitgever':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].publisher)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                snode = tnode.find(self.sikbns + 'uitgavePlaats')
                if snode is not None:
                    lnode = rdflib.Literal(snode.text)
                    hf.addType(self.graph, self.namespace, lnode, self.namespace['dcterms'].Location)
                    hf.addProperty(self.graph, cnode, lnode, self.namespace['dcterms'].spatial)
                    hf.addLabel(self.graph, self.namespace, lnode, 'Plaats van Uitgave', 'nl')
            if child.tag == self.sikbns + 'redacteur':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['bibo'].editor)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'titelContainer':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['prism'].publicationName)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'issn':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['prism'].issn)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).upper(), 'nl')
            if child.tag == self.sikbns + 'isbn':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['prism'].isbn)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).upper(), 'nl')
            if child.tag == self.sikbns + 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E73_Information_Object)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P67_refers_to)

    def organisatieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E40_Legal_Body)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'naam':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E82_Actor_Appellation)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P131_is_identified_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'telefoon':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E51_Contact_Point)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P76_has_contact_point)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'email':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E51_Contact_Point)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P76_has_contact_point)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'contactpersoonId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E21_Person)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P107_has_current_or_former_member)
            if child.tag == self.sikbns + 'adres':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['locn'].Address)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['locn'].address)
                hf.addLabel(self.graph, self.namespace, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for element in child:
                    if element.tag == self.sikbns + 'straat':  # until index is available
                        enode = rdflib.Literal(element.text)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['gn'].Feature)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['locn'].thoroughfare)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                        gnnode = rdflib.URIRef(self.namespace['gn'] + 'R.ST')
                        hf.addProperty(self.graph, enode, gnnode, self.namespace['gn'].featureCode)
                    if element.tag == self.sikbns + 'huisnummer':
                        enode = rdflib.Literal(element.text)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['xsd'].positiveInteger)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['locn'].locatorDesignator)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                    if element.tag == self.sikbns + 'postcode':
                        enode = rdflib.Literal(element.text)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['xsd'].string)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['locn'].postCode)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                    if element.tag == self.sikbns + 'plaatsnaam':  # until index is available
                        enode = rdflib.Literal(element.text)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['gn'].Feature)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['locn'].postName)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                        gnnode = rdflib.URIRef(self.namespace['gn'] + 'P.PPL')
                        hf.addProperty(self.graph, enode, gnnode, self.namespace['gn'].featureCode)
                    if element.tag == self.sikbns + 'gemeente':  # until index is available
                        enode = rdflib.Literal(element.text)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['gn'].Feature)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['gn'].parentADM2)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                        gnnode = rdflib.URIRef(self.namespace['gn'] + 'A.ADM2')
                        hf.addProperty(self.graph, enode, gnnode, self.namespace['gn'].featureCode)
                    if element.tag == self.sikbns + 'provincie':  # until index is available
                        enode = rdflib.Literal(element.text)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['gn'].Feature)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['gn'].parentADM1)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                        gnnode = rdflib.URIRef(self.namespace['gn'] + 'A.ADM1')
                        hf.addProperty(self.graph, enode, gnnode, self.namespace['gn'].featureCode)
                    if element.tag == self.sikbns + 'land':  # until index is available
                        enode = rdflib.Literal(element.text)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['gn'].Feature)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['gn'].parentCountry)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                        gnnode = rdflib.URIRef(self.namespace['gn'] + 'A.PCLI')
                        hf.addProperty(self.graph, enode, gnnode, self.namespace['gn'].featureCode)

    def tekeningHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0016_RecordDrawing)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'tekeningtype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0081_RecordDrawingReferenceType)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'tekeningmateriaal':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].medium)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'tekeningformaat':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0079_RecordDrawingNote)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P3_has_note)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'tekenaar':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].creator)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'schaal':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0079_RecordDrawingNote)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P3_has_note)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'tekeningdatum':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].date)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].date)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'tekeningonderwerp':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].description)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E73_Information_Object)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P129i_is_subject_of)
                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P129_is_about)  # for easy navigation
            if child.tag == self.sikbns + 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P70_documents)
            if child.tag == self.sikbns + 'vondstId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0009_ContextFind)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P129_is_about)

    def fotoHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0017_RecordPhotograph)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'opnametype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0085_RecordPhotographReferenceType)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'opnamedatum':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].date)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].date)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'fotograaf':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].creator)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'opnamemedium':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].medium)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'fotoonderwerp':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].description)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E73_Information_Object)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P129i_is_subject_of)
                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P129_is_about)  # for easy navigation
            if child.tag == self.sikbns + 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P70_documents)
            if child.tag == self.sikbns + 'vondstId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0009_ContextFind)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P129_is_about)

    def doosHandler(self, pnode, tnode):
        bnode = hf.genID(self.graph, self.namespace, pnode)
        hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E12_Production)
        hf.addProperty(self.graph, pnode, bnode, self.namespace['crm'].P9_consists_of)
        hf.addLabel(self.graph, self.namespace, bnode, 'Verzamelen (Objecten)', 'nl')

        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E78_Collection)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        hf.addProperty(self.graph, bnode, gnode, self.namespace['crm'].P108_has_produced)

        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'bewaarTemperatuur':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0041_ContextFindTreatmentProcedure)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P129i_is_subject_of)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'bewaarVochtigheid':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0041_ContextFindTreatmentProcedure)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P129i_is_subject_of)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'lichtgevoelig':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0041_ContextFindTreatmentProcedure)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P129i_is_subject_of)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'breekbaar':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0041_ContextFindTreatmentProcedure)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P129i_is_subject_of)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'gevaarlijkeStoffen':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0041_ContextFindTreatmentProcedure)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P129i_is_subject_of)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

    def verpakkingseenheidHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0010_BulkFind)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'aantal':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].NonNegativeInteger)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P57_has_number_of_parts)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'gewicht':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E54_Dimension)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P43_has_dimension)
                hf.addLabel(self.graph, self.namespace, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v)
                        hf.addType(self.graph, self.namespace, uomnode, self.namespace['crm'].E58_Measurement_Unit)
                        hf.addProperty(self.graph, bnode, uomnode, self.namespace['crm'].P91_has_unit)
                        hf.addLabel(self.graph, self.namespace, uomnode, 'Meeteenheid', 'nl')

                inode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, inode, self.namespace['xsd'].positiveInteger)
                hf.addProperty(self.graph, bnode, inode, self.namespace['crm'].P90_has_value)
                hf.addLabel(self.graph, self.namespace, inode, 'Waarde', 'nl')
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode, self.namespace['crmeh'].EHE2021_BulkFindAssessment)
                    hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P140i_was_attributed_by)
                    hf.addLabel(self.graph, self.namespace, bnode, 'Dateren', 'nl')

                    bnode2 = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode2, rdflib.URIRef(self.namespace['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.namespace['crm'] + 'P141_assigned'))
                    hf.addLabel(self.graph, self.namespace, bnode2, 'Time Span', 'nl')

                    cnode = rdflib.Literal(child.text)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                    hf.addProperty(self.graph, bnode2, cnode, self.namespace['crmeh'].EXP1)  # wrong range
                    hf.addLabel(self.graph, self.namespace, cnode, 'Beginperiode', 'nl')
                    hf.addRefIfExists(self.graph, self.namespace, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        cnode = rdflib.Literal(snode.text)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                        hf.addProperty(self.graph, bnode2, cnode, self.namespace['crmeh'].EXP2)  # wrong range
                        hf.addLabel(self.graph, self.namespace, cnode, 'Eindperiode', 'nl')
                        hf.addRefIfExists(self.graph, self.namespace, cnode, snode)
            if child.tag == self.sikbns + 'doosId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E78_Collection)

                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P46_is_composed_of)
                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P46i_forms_part_of)

    def monsterHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0018_ContextSample)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'monstertype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0053_ContextSampleType)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'monsterverwerking':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P3_has_note)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E13_Attribute_Assignment)
                    hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P140i_was_attributed_by)
                    hf.addLabel(self.graph, self.namespace, bnode, 'Dateren', 'nl')

                    bnode2 = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode2, rdflib.URIRef(self.namespace['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.namespace['crm'] + 'P141_assigned'))
                    hf.addLabel(self.graph, self.namespace, bnode2, 'Time Span', 'nl')

                    cnode = rdflib.Literal(child.text)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                    hf.addProperty(self.graph, bnode2, cnode, self.namespace['crmeh'].EXP1)  # wrong range
                    hf.addLabel(self.graph, self.namespace, cnode, 'Beginperiode', 'nl')
                    hf.addRefIfExists(self.graph, self.namespace, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        cnode = rdflib.Literal(snode.text)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                        hf.addProperty(self.graph, bnode2, cnode, self.namespace['crmeh'].EXP2)  # wrong range
                        hf.addLabel(self.graph, self.namespace, cnode, 'Eindperiode', 'nl')
                        hf.addRefIfExists(self.graph, self.namespace, cnode, snode)
            if child.tag == self.sikbns + 'verpakkingseenheidId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0010_BulkFind)

                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P46_is_composed_of)
                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P46i_forms_part_of)
            if child.tag == self.sikbns + 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P53i_is_former_or_current_location_of)
                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P53_has_former_or_current_location)

    def vondstHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0009_ContextFind)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'aantal':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crmeh'].EHE0031_ContextFindMeasurement)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P43_has_dimension)
                hf.addLabel(self.graph, self.namespace, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                inode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, inode, self.namespace['xsd'].positiveInteger)
                hf.addProperty(self.graph, bnode, inode, self.namespace['crm'].P90_has_value)
                hf.addLabel(self.graph, self.namespace, inode, 'Waarde', 'nl')
            if child.tag == self.sikbns + 'gewicht':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crmeh'].EHE0031_ContextFindMeasurement)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P43_has_dimension)
                hf.addLabel(self.graph, self.namespace, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v)
                        hf.addType(self.graph, self.namespace, uomnode, self.namespace['crm'].E58_Measurement_Unit)
                        hf.addProperty(self.graph, bnode, uomnode, self.namespace['crm'].P91_has_unit)
                        hf.addLabel(self.graph, self.namespace, uomnode, 'Meeteenheid', 'nl')

                inode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, inode, self.namespace['xsd'].positiveInteger)
                hf.addProperty(self.graph, bnode, inode, self.namespace['crm'].P90_has_value)
                hf.addLabel(self.graph, self.namespace, inode, 'Waarde', 'nl')
            if child.tag == self.sikbns + 'materiaalcategorie':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0030_ContextFindMaterial)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P45_consists_of)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'artefacttype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E13_Attribute_Assignment)
                    hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P140i_was_attributed_by)
                    hf.addLabel(self.graph, self.namespace, bnode, 'Dateren', 'nl')

                    bnode2 = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode2, rdflib.URIRef(self.namespace['crmeh'] + 'EHE0099_ContextFindUseEventTimespan'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.namespace['crm'] + 'P141_assigned'))
                    hf.addLabel(self.graph, self.namespace, bnode2, 'Time Span', 'nl')

                    cnode = rdflib.Literal(child.text)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                    hf.addProperty(self.graph, bnode2, cnode, self.namespace['crmeh'].EXP1)  # wrong range
                    hf.addLabel(self.graph, self.namespace, cnode, 'Beginperiode', 'nl')
                    hf.addRefIfExists(self.graph, self.namespace, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        cnode = rdflib.Literal(snode.text)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                        hf.addProperty(self.graph, bnode2, cnode, self.namespace['crmeh'].EXP2)  # wrong range
                        hf.addLabel(self.graph, self.namespace, cnode, 'Eindperiode', 'nl')
                        hf.addRefIfExists(self.graph, self.namespace, cnode, snode)
            if child.tag == self.sikbns + 'geconserveerd':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E87_Curation_Activity)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P147i_was_curated_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'exposabel':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E87_Curation_Activity)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P147i_was_curated_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'gedeselecteerd':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E87_Curation_Activity)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P147i_was_curated_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'verpakkingseenheidId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0010_BulkFind)

                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P46_is_composed_of)
                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P46i_forms_part_of)
            if child.tag == self.sikbns + 'veldvondstId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E78_Collectiono)

                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P46_is_composed_of)
                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P46i_forms_part_of)

    def veldvondstHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E78_Collection)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'verzamelwijze':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0046_ContextNote)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P3_has_note)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P53_has_former_or_current_location)

    def vondstcontextHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisLocatieTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0009_ContextFind)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'contexttype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P89i_contains)
            if child.tag == self.sikbns + 'stortId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0008_ContextStuff)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crmeh'].EHP3i)
            if child.tag == self.sikbns + 'planumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P89i_contains)
            if child.tag == self.sikbns + 'vullingId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0008_ContextStuff)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crmeh'].EHP3i)
            if child.tag == self.sikbns + 'segmentId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P89i_contains)
            if child.tag == self.sikbns + 'vakId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P89i_contains)
            if child.tag == self.sikbns + 'boringId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P89i_contains)

        return gnode

    def boringHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0007_Context)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')

    def vullingHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0008_ContextStuff)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'vorm':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0059_ContextStuffNote)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P3_has_note)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'kleur':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0059_ContextStuffNote)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P3_has_note)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'textuur':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0059_ContextStuffNote)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P3_has_note)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crmeh'].EHP3)
                hf.addProperty(self.graph, enode, gnode, self.namespace['crmeh'].EHP3i)

    def structuurHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0008_ContextStuff)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'structuurtype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E13_Attribute_Assignment)
                    hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P140i_was_attributed_by)
                    hf.addLabel(self.graph, self.namespace, bnode, 'Dateren', 'nl')

                    bnode2 = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode2, rdflib.URIRef(self.namespace['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.namespace['crm'] + 'P141_assigned'))
                    hf.addLabel(self.graph, self.namespace, bnode2, 'Time Span', 'nl')

                    cnode = rdflib.Literal(child.text)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                    hf.addProperty(self.graph, bnode2, cnode, self.namespace['crmeh'].EXP1)  # wrong range
                    hf.addLabel(self.graph, self.namespace, cnode, 'Beginperiode', 'nl')
                    hf.addRefIfExists(self.graph, self.namespace, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        cnode = rdflib.Literal(snode.text)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                        hf.addProperty(self.graph, bnode2, cnode, self.namespace['crmeh'].EXP2)  # wrong range
                        hf.addLabel(self.graph, self.namespace, cnode, 'Eindperiode', 'nl')
                        hf.addRefIfExists(self.graph, self.namespace, cnode, snode)
            if child.tag == self.sikbns + 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P53_has_former_or_current_location)
                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P53i_is_former_or_current_location_of)

    def segmentHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0007_Context)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P89_falls_within)
                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P89i_contains)

    def stortHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0008_ContextStuff)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'putId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crmeh'].EHP3)
                hf.addProperty(self.graph, enode, gnode, self.namespace['crmeh'].EHP3i)
            if child.tag == self.sikbns + 'planumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crmeh'].EHP3)
                hf.addProperty(self.graph, enode, gnode, self.namespace['crmeh'].EHP3i)

    def planumHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0007_Context)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'planumtype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'putId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P89_falls_within)
                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P89i_contains)

    def spoorHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0007_Context)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'grondspoortype':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'diepte':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E16_Measurement)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P39i_was_measured_by)
                hf.addLabel(self.graph, self.namespace, bnode, 'Meting', 'nl')

                bnode2 = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode2, self.namespace['crm'].E54_Dimension)
                hf.addProperty(self.graph, bnode, bnode2, self.namespace['crm'].P40_observed_dimension)
                hf.addLabel(self.graph, self.namespace, bnode2, 'Diepte', 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v)
                        hf.addType(self.graph, self.namespace, uomnode, self.namespace['crm'].E58_Measurement_Unit)
                        hf.addProperty(self.graph, bnode2, uomnode, self.namespace['crm'].P91_has_unit)
                        hf.addLabel(self.graph, self.namespace, uomnode, 'Meeteenheid', 'nl')

                inode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, inode, self.namespace['xsd'].positiveInteger)
                hf.addProperty(self.graph, bnode2, inode, self.namespace['crm'].P90_has_value)
                hf.addLabel(self.graph, self.namespace, inode, 'Waarde', 'nl')
            if child.tag == self.sikbns + 'beginperiode':
                    bnode = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E13_Attribute_Assignment)
                    hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P140i_was_attributed_by)
                    hf.addLabel(self.graph, self.namespace, bnode, 'Dateren', 'nl')

                    bnode2 = hf.genID(self.graph, self.namespace, pnode)
                    hf.addType(self.graph, self.namespace, bnode2, rdflib.URIRef(self.namespace['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.namespace['crm'] + 'P141_assigned'))
                    hf.addLabel(self.graph, self.namespace, bnode2, 'Time Span', 'nl')

                    cnode = rdflib.Literal(child.text)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                    hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                    hf.addProperty(self.graph, bnode2, cnode, self.namespace['crmeh'].EXP1)  # wrong range
                    hf.addLabel(self.graph, self.namespace, cnode, 'Beginperiode', 'nl')
                    hf.addRefIfExists(self.graph, self.namespace, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        cnode = rdflib.Literal(snode.text)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['crmeh'].EHE0091_Timestamp)
                        hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                        hf.addProperty(self.graph, bnode2, cnode, self.namespace['crmeh'].EXP2)  # wrong range
                        hf.addLabel(self.graph, self.namespace, cnode, 'Eindperiode', 'nl')
                        hf.addRefIfExists(self.graph, self.namespace, cnode, snode)

    def putHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0007_Context)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')

    def vakHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crmeh'].EHE0007_Context)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'vaknummer':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E41_Appellation)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P1_is_identified_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'dikte':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E16_Measurement)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P39i_was_measured_by)
                hf.addLabel(self.graph, self.namespace, bnode, 'Meting', 'nl')

                bnode2 = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode2, self.namespace['crm'].E54_Dimension)
                hf.addProperty(self.graph, bnode, bnode2, self.namespace['crm'].P40_observed_dimension)
                hf.addLabel(self.graph, self.namespace, bnode2, 'Dikte', 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v)
                        hf.addType(self.graph, self.namespace, uomnode, self.namespace['crm'].E58_Measurement_Unit)
                        hf.addProperty(self.graph, bnode2, uomnode, self.namespace['crm'].P91_has_unit)
                        hf.addLabel(self.graph, self.namespace, uomnode, 'Meeteenheid', 'nl')

                inode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, inode, self.namespace['xsd'].positiveInteger)
                hf.addProperty(self.graph, bnode2, inode, self.namespace['crm'].P90_has_value)
                hf.addLabel(self.graph, self.namespace, inode, 'Waarde', 'nl')
            if child.tag == self.sikbns + 'nap':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E16_Measurement)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P39i_was_measured_by)
                hf.addLabel(self.graph, self.namespace, bnode, 'Meting', 'nl')

                bnode2 = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode2, self.namespace['crm'].E54_Dimension)
                hf.addProperty(self.graph, bnode, bnode2, self.namespace['crm'].P40_observed_dimension)
                hf.addLabel(self.graph, self.namespace, bnode2, 'Normaal Amsterdams Peil (NAP)', 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v)
                        hf.addType(self.graph, self.namespace, uomnode, self.namespace['crm'].E58_Measurement_Unit)
                        hf.addProperty(self.graph, bnode2, uomnode, self.namespace['crm'].P91_has_unit)
                        hf.addLabel(self.graph, self.namespace, uomnode, 'Meeteenheid', 'nl')

                inode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, inode, self.namespace['xsd'].positiveInteger)
                hf.addProperty(self.graph, bnode2, inode, self.namespace['crm'].P90_has_value)
                hf.addLabel(self.graph, self.namespace, inode, 'Waarde', 'nl')
            if child.tag == self.sikbns + 'planumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crmeh'].EHE0007_Context)

                hf.addProperty(self.graph, gnode, enode, self.namespace['crm'].P89_falls_within)
                hf.addProperty(self.graph, enode, gnode, self.namespace['crm'].P89i_contains)

    def persoonHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E21_Person)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'telefoon':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E51_Contact_Point)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P76_has_contact_point)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'email':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E51_Contact_Point)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P76_has_contact_point)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'naam':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['foaf'].Person)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P131_is_identified_by)
                hf.addLabel(self.graph, self.namespace, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for element in child:
                    if element.tag == self.sikbns + 'achternaam':
                        snode = child.find(self.sikbns + 'tussenvoegsel')
                        value = element.text + ', ' + snode.text if snode is not None else element.text  # extract 'tussenvoegsel' if available

                        enode = rdflib.Literal(value)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['xsd'].string)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['foaf'].familyName)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                    if element.tag == self.sikbns + 'voornaam':
                        snode = child.find(self.sikbns + 'initialen')
                        value = element.text + ', ' + snode.text if snode is not None else element.text  # extract 'initialen' if available

                        enode = rdflib.Literal(value)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['xsd'].string)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['foaf'].givenName)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                    if element.tag == self.sikbns + 'initialen':
                        snode = child.find(self.sikbns + 'voornaam')
                        if snode is None:
                            enode = rdflib.Literal(element.text)

                            hf.addType(self.graph, self.namespace, enode, self.namespace['xsd'].string)
                            hf.addProperty(self.graph, bnode, enode, self.namespace['foaf'].givenName)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')
                    if element.tag == self.sikbns + 'titel':
                        enode = rdflib.Literal(element.text)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['xsd'].string)
                        hf.addProperty(self.graph, bnode, enode, self.namespace['foaf'].title)
                        hf.addLabel(self.graph, self.namespace, enode, re.sub(self.sikbns, '', element.tag).title(), 'nl')

    def geolocatieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractGeoObjectFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E44_Place_Appellation)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'geometrie':
                cnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['geosparql'].Geometry)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P87_is_identified_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                gmlnode = rdflib.Literal(hf.gmlLiteralOf(self.et, child))
                hf.addType(self.graph, self.namespace, gmlnode, self.namespace['geosparql'].GMLLiteral)
                hf.addProperty(self.graph, cnode, gmlnode, self.namespace['geosparql'].asGML)

    def hoogtemetingHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E13_Attribute_Assignment)

        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'methode':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E55_Type)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P2_has_type)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
                hf.addRefIfExists(self.graph, self.namespace, cnode, child)
            if child.tag == self.sikbns + 'nap':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E54_Dimension)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P40_observed_dimension)
                hf.addLabel(self.graph, self.namespace, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v)
                        hf.addType(self.graph, self.namespace, uomnode, self.namespace['crm'].E58_Measurement_Unit)
                        hf.addProperty(self.graph, bnode, uomnode, self.namespace['crm'].P91_has_unit)
                        hf.addLabel(self.graph, self.namespace, uomnode, 'Meeteenheid', 'nl')

                inode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, inode, self.namespace['xsd'].positiveInteger)
                hf.addProperty(self.graph, bnode, inode, self.namespace['crm'].P90_has_value)
                hf.addLabel(self.graph, self.namespace, inode, 'Waarde', 'nl')

    def attribuutHandler(self, tnode):
        child = tnode.find(self.sikbns + 'objectId')
        (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
        if not exists:
            hf.extractGenericObjectFields(self.graph, self.namespace, enode, child)
            hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E1_CRM_Entity)

        value = None
        vtype = None
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'geheelgetal':
                value = rdflib.Literal(child.text)
                vtype = self.namespace['xsd'].integer
            if child.tag == self.sikbns + 'decimaalgetal':
                value = rdflib.Literal(child.text)
                vtype = self.namespace['xsd'].decimal
            if child.tag == self.sikbns + 'referentieId':
                value = rdflib.Literal(child.text)
                vtype = self.namespace['xsd'].ID
            if child.tag == self.sikbns + 'text':
                value = rdflib.Literal(child.text)
                vtype = self.namespace['xsd'].string
            if child.tag == self.sikbns + 'jaNee':
                value = rdflib.Literal(child.text)
                vtype = self.namespace['xsd'].boolean

        atypeID = tnode.find(self.sikbns + 'attribuuttypeId').text
        atype = None
        for atnode in self.troot.findall(self.sikbns + 'attribuuttype'):
            if atnode.attrib[self.sikbns + 'id'] == atypeID:
                atype = atnode
                break

        if atype is not None:
            for child in atype.getchildren():
                if child.tag == self.sikbns + 'attribuutnaam':
                    hf.addLabel(self.graph, self.namespace, value, rdflib.Literal(child.text), 'nl')
                if child.tag == self.sikbns + 'informatie':
                    info = rdflib.Literal(child.text, 'nl')
                    hf.addProperty(self.graph, value, info, self.namespace['rdfs'].comment)
                    hf.addType(self.graph, self.namespace, info, self.namespace['xsd'].string)

            hf.addType(self.graph, self.namespace, value, vtype)
            hf.addProperty(self.graph, enode, value, self.namespace['rdf'].value)

    def objectrelatieHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['owl'].ObjectProperty)

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

                cnode = rdflib.Literal(relation + '(' + object1Class + ', ' + object2Class + ')', 'nl')
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['rdfs'].comment)

            if child.tag == self.sikbns + 'object1Id':
                    (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                    if not exists:
                        hf.extractGenericObjectFields(self.graph, self.namespace, enode, child)
                        hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E1_CRM_Entity)

                    snode = tnode.find(self.sikbns + 'object2Id')
                    if snode is not None:
                        (enode2, exists) = hf.getNodeFromElem(self.graph, self.namespace, snode)
                        if not exists:
                            hf.extractGenericObjectFields(self.graph, self.namespace, enode2, snode)
                            hf.addType(self.graph, self.namespace, enode2, self.namespace['crm'].E1_CRM_Entity)

                        object1Class = hf.getNodeClass(self.graph, self.namespace, enode)
                        if object1Class is not None:
                            hf.addProperty(self.graph, gnode, object1Class, self.namespace['rdfs'].domain)
                        object2Class = hf.getNodeClass(self.graph, self.namespace, enode2)
                        if object2Class is not None:
                            hf.addProperty(self.graph, gnode, object2Class, self.namespace['rdfs'].range)

                        # add new relation to specified resources
                        hf.addProperty(self.graph, enode, enode2, gnode)

    def codereferentieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.namespace, tnode)
        if not exists:
            hf.extractGenericObjectFields(self.graph, self.namespace, gnode, tnode)
            hf.addType(self.graph, self.namespace, gnode, self.namespace['crm'].E32_Authority_Document)

        hf.addProperty(self.graph, self.groot, gnode, self.namespace['crm'].P67_refers_to)
        hf.addLabel(self.graph, self.namespace, gnode, re.sub(self.sikbns, '', tnode.tag).title(), 'nl')
        for child in tnode.getchildren():
            if child.tag == self.sikbns + 'bronCode':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E33_Linguistic_Object)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['crm'].P129_is_about)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                snode = tnode.find(self.sikbns + 'standaardCode')
                if snode is not None:
                    dnode = rdflib.Literal(snode.text)
                    hf.addType(self.graph, self.namespace, dnode, self.namespace['crm'].E75_Conceptual_Object_Appellation)
                    hf.addProperty(self.graph, cnode, dnode, self.namespace['crm'].P1_is_identified_by)
                    hf.addLabel(self.graph, self.namespace, dnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'bronOmschrijving':
                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['xsd'].string)
                hf.addProperty(self.graph, gnode, cnode, self.namespace['dcterms'].description)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'bronCodeLijst':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E32_Authority_Document)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P71i_is_listed_in)
                hf.addLabel(self.graph, self.namespace, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E41_Appellation)
                hf.addProperty(self.graph, bnode, cnode, self.namespace['crm'].P1_is_identified_by)
            if child.tag == self.sikbns + 'naamCodeLijst':
                bnode = hf.genID(self.graph, self.namespace, pnode)
                hf.addType(self.graph, self.namespace, bnode, self.namespace['crm'].E32_Authority_Document)
                hf.addProperty(self.graph, gnode, bnode, self.namespace['crm'].P71i_is_listed_in)
                hf.addLabel(self.graph, self.namespace, bnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')

                cnode = rdflib.Literal(child.text)
                hf.addType(self.graph, self.namespace, cnode, self.namespace['crm'].E41_Appellation)
                hf.addProperty(self.graph, bnode, cnode, self.namespace['crm'].P1_is_identified_by)
                hf.addLabel(self.graph, self.namespace, cnode, re.sub(self.sikbns, '', child.tag).title(), 'nl')
            if child.tag == self.sikbns + 'historyId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.namespace, child)
                if not exists:
                    hf.extractGenericObjectFields(self.graph, self.namespace, enode, child)
                    hf.addType(self.graph, self.namespace, enode, self.namespace['crm'].E32_Authority_Document)

                hf.addProperty(self.graph, gnode, enode, self.namespace['rdfs'].subClassOf)

    def conceptHandler(self):
        # existing concepts
        for element in self.troot:
            child = rdflib.URIRef(self.namespace['base'] + hf.getID(element, self.namespace))

            # if element.tag == self.sikbns + 'archis':
            #    hf.extractBasisTypeFields(self.graph, self.namespace, child, element)
            #    hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E73_Information_Object)
            if element.tag == self.sikbns + 'bestand':
                hf.extractBasisTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E73_Information_Object)
            if element.tag == self.sikbns + 'boring':
                hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0007_Context)
            if element.tag == self.sikbns + 'digitaalmedium':
                hf.extractBasisTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E84_Information_Carrier)
            if element.tag == self.sikbns + 'document':
                hf.extractBasisTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E31_Document)
            if element.tag == self.sikbns + 'doos':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E78_Collection)
            if element.tag == self.sikbns + 'dossier':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E84_Information_Carrier)
            if element.tag == self.sikbns + 'foto':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0017_RecordPhotograph)
            if element.tag == self.sikbns + 'geolocatie':
                hf.extractGeoObjectFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E44_Place_Appellation)
            if element.tag == self.sikbns + 'hoogtemeting':
                hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E13_Attribute_Assignment)
            if element.tag == self.sikbns + 'monster':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0018_ContextSample)
            if element.tag == self.sikbns + 'organisatie':
                hf.extractBasisTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E40_Legal_Body)
            if element.tag == self.sikbns + 'persoon':
                hf.extractBasisTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E21_Person)
            if element.tag == self.sikbns + 'planum':
                hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0007_Context)
            if element.tag == self.sikbns + 'project':
                hf.extractBasisTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0001_EHProject)
            if element.tag == self.sikbns + 'projectlocatie':
                hf.extractBasisTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0003_AreaOfInvestigation)
            if element.tag == self.sikbns + 'put':
                hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0007_Context)
            if element.tag == self.sikbns + 'segment':
                hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0007_Context)
            if element.tag == self.sikbns + 'spoor':
                hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0007_Context)
            if element.tag == self.sikbns + 'stort':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0008_ContextStuff)
            if element.tag == self.sikbns + 'structuur':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0006_GroupStuff)
            if element.tag == self.sikbns + 'tekening':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0016_RecordDrawing)
            if element.tag == self.sikbns + 'vak':
                hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0007_Context)
            if element.tag == self.sikbns + 'veldvondst':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E78_Collection)
            if element.tag == self.sikbns + 'verpakkingseenheid':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0010_BulkFind)
            if element.tag == self.sikbns + 'vindplaats':
                hf.extractBasisLocatieNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0004_SiteSubDivision)
            if element.tag == self.sikbns + 'vondst':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0009_ContextFind)
            if element.tag == self.sikbns + 'vondstcontext':
                hf.extractBasisLocatieTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0007_Context)
            if element.tag == self.sikbns + 'vulling':
                hf.extractBasisNaamTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crmeh'].EHE0008_ContextStuff)
            # if element.tag == self.sikbns + 'waarneming':
            #    hf.extractBasisLocatieTypeFields(self.graph, self.namespace, child, element)
            #    hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E5_Event)
            # if element.tag == self.sikbns + 'attribuuttype':
            #    hf.extractGenericObjectFields(self.graph, self.namespace, child, element)
            #    hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E89_Propositional_Object)
            # if element.tag == self.sikbns + 'attribuut':
            #    hf.extractGenericObjectFields(self.graph, self.namespace, child, element)
            #    hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E1_CRM_Entity)
            if element.tag == self.sikbns + 'objectrelatie':
                hf.extractBasisTypeFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['owl'].ObjectProperty)
            if element.tag == self.sikbns + 'codereferentie':
                hf.extractGenericObjectFields(self.graph, self.namespace, child, element)
                hf.addType(self.graph, self.namespace, child, self.namespace['crm'].E32_Authority_Document)