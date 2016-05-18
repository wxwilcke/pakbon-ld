#!/usr/bin/python3

import rdflib
import helpFunctions as hf
import re


class Protocol0102:

    def __init__(self, et, tree, namespace, sikbns, vocab):
        self.et = et
        self.sikbns = '{' + sikbns + '}'
        self.basens = namespace['base'] + 'res/'
        self.ontns = namespace['base'] + 'ont/'
        self.vocns = namespace['base'] + 'voc/'

        # root of protocol
        self.troot = tree.getroot()
        self.graph = rdflib.Graph(identifier='SIKBID_' + self.troot.attrib[self.sikbns + 'id'])

        hf.setGraphNamespaceIDs(self.graph, namespace)
        self.nss = dict(ns for ns in self.graph.namespace_manager.namespaces())

        self.groot = rdflib.URIRef(self.basens + 'SIKBID_' + hf.getID(self.troot, self.sikbns))

        # set type of protocol
        hf.addType(self.graph, self.groot, rdflib.URIRef(self.nss['crm'] + 'E31_Document'))

        # root attributes
        child = rdflib.Literal('Exemplaar van SIKB Archeologisch Protocol 0102 (ofwel Pakbon) conform de RDF standaard', lang='nl')
        hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['rdfs'] + 'label'))
        child = rdflib.Literal('Instance of RDF-compliant SIKB Archaeological Protocol 0102 (aka Pakbon)', lang='en')
        hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['rdfs'] + 'label'))
        if self.sikbns + 'id' in self.troot.attrib.keys():  # id
            child = rdflib.Literal(self.troot.attrib[self.sikbns + 'id'], datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
            hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
        if 'versie' in self.troot.attrib.keys():  # versie
            child = rdflib.Literal(self.troot.attrib['versie'], datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
            hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['prism'] + 'versionIdentifier'))
        if 'timestamp' in self.troot.attrib.keys():  # timestamp
            child = rdflib.Literal(self.troot.attrib['timestamp'], datatype=rdflib.URIRef(self.nss['xsd'] + 'dateTime'))
            hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['dcterms'] + 'issued'))

        # root elements
        self.conceptHandler()

        (gproject, onode) = self.projectHandler(self.troot.find(self.sikbns + 'project'))
        for child in self.troot.iter(self.sikbns + 'projectlocatie'):
            self.projectlocatieHandler(gproject, child)
        for child in self.troot.iter(self.sikbns + 'vindplaats'):
            self.vindplaatsHandler(gproject, child, vocab)
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
            self.verpakkingseenheidHandler(gproject, child, vocab)
        for child in self.troot.iter(self.sikbns + 'monster'):
            self.monsterHandler(gproject, child, vocab)
        for child in self.troot.iter(self.sikbns + 'vondst'):
            self.vondstHandler(gproject, child, vocab)
        for child in self.troot.iter(self.sikbns + 'veldvondst'):
            self.veldvondstHandler(child)
        for child in self.troot.iter(self.sikbns + 'vondstcontext'):
            self.vondstcontextHandler(child)
        for child in self.troot.iter(self.sikbns + 'boring'):
            self.boringHandler(child)
        for child in self.troot.iter(self.sikbns + 'vulling'):
            self.vullingHandler(child)
        for child in self.troot.iter(self.sikbns + 'structuur'):
            self.structuurHandler(gproject, child, vocab)
        for child in self.troot.iter(self.sikbns + 'segment'):
            self.segmentHandler(child)
        for child in self.troot.iter(self.sikbns + 'spoor'):
            self.spoorHandler(gproject, child, vocab)
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
            self.attribuutHandler(gproject, child)
        #  for child in self.troot.iter(self.sikbns + 'archis'):
            #  self.archisHandler(child)
        # for child in self.troot.iter(self.sikbns + 'attribuuttype'):
            #  self.attribuuttypeHandler(child)
        for child in self.troot.iter(self.sikbns + 'objectrelatie'):
            self.objectrelatieHandler(child)
        for child in self.troot.iter(self.sikbns + 'codereferentie'):
            self.codereferentieHandler(self.groot, child)

    def projectHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0001_EHProject'))


        hf.addProperty(self.graph, self.groot, gnode, rdflib.URIRef(self.nss['crm'] + 'P70_documents'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'projectnaam':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))

                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) + " ({})".format(hf.rawString(child.text)), 'nl')
            if childname == 'startdatum':
                bnode = hf.genID(self.graph, gnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0021_EHProjectTimespan'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P4_has_time-span'))

                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))

                snode = tnode.find(self.sikbns + 'einddatum')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    dnode = rdflib.Literal(hf.rawString(snode.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                    hf.addProperty(self.graph, bnode, dnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                           parentname + '_' + childname))

                enddate = dnode.value if dnode is not None else '?'
                hf.addLabel(self.graph, bnode,\
                            'Tijdspanne (van {} tot {}) behorende bij {}'.format(cnode.value, enddate, hf.getLabel(self.graph, gnode)), 'nl')

            if childname == 'onderzoeksmeldingsnummber':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))

            if childname == 'onderzoektype':
                key = 'verwerving'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)

            if childname == 'omschrijving':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))

            if childname == 'bevoegdGezag':
                bnode = hf.genID(self.graph, gnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P11_had_participant'))
                hf.addLabel(self.graph, bnode,\
                            re.sub(self.sikbns, '', child.tag).title() + ' behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

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

            if childname == 'uitvoerder':
                bnode = hf.genID(self.graph, gnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P14_carried_out_by'))
                hf.addLabel(self.graph, bnode,\
                            re.sub(self.sikbns, '', child.tag).title() + ' behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

                parentname = childname
                for element in child:
                    childname = re.sub(self.sikbns, '', element.tag)
                    if childname == 'uitvoerdercode':  #
                        key = 'uitvoerder'  # needed for inconsistent labeling by SIKB
                        enode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(element.text))
                        hf.addSchemaType(self.graph, self.ontns, enode, bnode, childname, parentname)
                        hf.addRefIfExists(self.graph, enode, element)
                    if childname == 'opgravingsleiderPersoonId':
                        (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, element)
                        if not exists:
                            hf.extractBasisTypeFields(self.graph, enode, element)
                            hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))
                    if childname == 'depotContactPersoonId':
                        (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, element)
                        if not exists:
                            hf.extractBasisTypeFields(self.graph, enode, element)
                            hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))

        # add unexisting concept: 'production' and 'bestanden'
        bnode = hf.genID(self.graph, gnode, self.basens)
        hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E12_Production'))
        hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P9_consists_of'))
        hf.addLabel(self.graph, bnode, 'Documentatie (Digitaal) behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

        onode = hf.genID(self.graph, gnode, self.basens)
        hf.addType(self.graph, onode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))
        hf.addProperty(self.graph, bnode, onode, rdflib.URIRef(self.nss['crm'] + 'P108_has_produced'))
        hf.addLabel(self.graph, onode, 'Bestanden behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

        return (gnode, onode)

    def projectlocatieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0003_AreaOfInvestigation'))

        hf.addProperty(self.graph, pnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P7_took_place_at'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'provinciecode':
                key = 'provincie'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'gemeentecode':
                key = 'gemeente'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'plaatscode':
                key = 'plaats'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'toponiem':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) + " ({})".format(hf.rawString(child.text)), 'nl')
            if childname == 'kaartblad':
                key = 'kaartblad'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'geolocatieId':
                (cnode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.addType(self.graph, cnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

                #hf.addLabel(self.graph, cnode, 'Geografische locatie van {}'.format(hf.getLabel(self.graph, gnode)), 'nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
                hf.addProperty(self.graph, cnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P87i_identifies'))

    def vindplaatsHandler(self, pnode, tnode, vocab):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0004_SiteSubDivision'))

        hf.addProperty(self.graph, pnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P7_took_place_at'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'vondstmeldingsnummer':  # until direct linking in Archis is possible
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                        'positiveInteger'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'waarnemingsnummer':  # until direct linking in Archis is possible
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                        'positiveInteger'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'beginperiode':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E52_Time-Span'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P4_has_time-span'))

                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)

                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode, childname, parentname)
                    hf.addRefIfExists(self.graph, dnode, snode)

                startdate = hf.getLabel(vocab, cnode) if (cnode is not None and vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                enddate = hf.getLabel(vocab, dnode) if (dnode is not None and vocab is not None)\
                                else key + ' ' + hf.rawString(snode.text)
                hf.addLabel(self.graph, bnode, 'Tijdspanne (van {} tot {}) behorende bij {}'.format(startdate, enddate, hf.getLabel(self.graph, gnode)), 'nl')

            if childname == 'vindplaatstype':
                key = 'complextype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'geolocatieId':
                (cnode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.addType(self.graph, cnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

                #hf.addLabel(self.graph, cnode, 'Geografische locatie van {}'.format(hf.getLabel(self.graph, gnode)), 'nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
                hf.addProperty(self.graph, cnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P87i_identifies'))

    def dossierHandler(self, pnode, tnode):
        bnode = hf.genID(self.graph, pnode, self.basens)
        hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E12_Production'))
        hf.addProperty(self.graph, pnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P9_consists_of'))
        hf.addLabel(self.graph, bnode, 'Documentatie (Analoog) behorende bij {}'.format(hf.getLabel(self.graph, pnode)), 'nl')

        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))

        hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P108_has_produced'))

        hf.updateLabel(self.graph, gnode,\
                       hf.getLabel(self.graph, gnode) + " behorende bij {}".format(hf.getLabel(self.graph, pnode)), 'nl')


        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'dossiertype':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'documentId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E31_Document'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P128_carries'))

    def bestandHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

        hf.addProperty(self.graph, pnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P128_carries'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['dcterms'] + 'isPartOf'))
            if childname == 'bestandsnaam':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'bestandtype':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'bestandsinhoud':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) + " ({})".format(hf.rawString(child.text)), 'nl')
            if childname == 'software':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'codeboek':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'digitaalmediumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['dcterms'] + 'medium'))

    def digitaalmediumHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'digitaalmediumtype':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) + " ({})".format(hf.rawString(child.text)), 'nl')

    def documentHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E31_Document'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'documenttype':
                key = 'documenttype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'titel':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) + " met titel '{}'".format(hf.rawString(child.text)), 'nl')
            if childname == 'auteur':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'jaar':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'gYear'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'serie':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'paginas':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'uitgever':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'uitgavePlaats':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'redacteur':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'titelContainer':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'issn':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'isbn':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P67_refers_to'))

    def organisatieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'naam':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) + " ({})".format(hf.rawString(child.text)), 'nl')
            if childname == 'telefoon':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'email':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'contactpersoonId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))
            if childname == 'adres':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)
                hf.addLabel(self.graph, bnode,\
                            'Adres behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

                parentname = childname
                for element in child:
                    childname = re.sub(self.sikbns, '', element.tag)
                    if element.tag == self.sikbns + 'straat':  # until index is available
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                               parentname + '_' + childname))
                    if element.tag == self.sikbns + 'huisnummer':
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'positiveInteger'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                               parentname + '_' + childname))
                    if element.tag == self.sikbns + 'postcode':
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                               parentname + '_' + childname))
                    if element.tag == self.sikbns + 'plaatsnaam':  # until index is available
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                               parentname + '_' + childname))
                    if element.tag == self.sikbns + 'gemeente':  # until index is available
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                               parentname + '_' + childname))
                    if element.tag == self.sikbns + 'provincie':  # until index is available
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                               parentname + '_' + childname))
                    if element.tag == self.sikbns + 'land':  # until index is available
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                               parentname + '_' + childname))

    def tekeningHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0016_RecordDrawing'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'tekeningtype':
                key = 'tekeningfototype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'tekeningmateriaal':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'tekeningformaat':
                key = 'papierformaat'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'tekenaar':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'schaal':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'tekeningdatum':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'tekeningonderwerp':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) + " met betrekking tot '{}'".format(hf.rawString(child.text)), 'nl')
            if childname == 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))  # for easy navigation
            if childname == 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P70_documents'))
            if childname == 'vondstId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))

    def fotoHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0017_RecordPhotograph'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'opnametype':
                key = 'tekeningfototype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'opnamedatum':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'fotograaf':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'opnamemedium':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'fotoonderwerp':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) + " met betrekking tot '{}'".format(hf.rawString(child.text)), 'nl')
            if childname == 'bestandId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))  # for easy navigation
            if childname == 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P70_documents'))
            if childname == 'vondstId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))

    def doosHandler(self, pnode, tnode):
        bnode = hf.genID(self.graph, pnode, self.basens)
        hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E12_Production'))
        hf.addProperty(self.graph, pnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P9_consists_of'))
        hf.addLabel(self.graph, bnode, 'Verzamelde objecten behorende bij {}'.format(hf.getLabel(self.graph, pnode)), 'nl')

        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))

        hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P108_has_produced'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'bewaarTemperatuur':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'bewaarVochtigheid':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'lichtgevoelig':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'breekbaar':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'gevaarlijkeStoffen':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))

    def verpakkingseenheidHandler(self, pnode, tnode, vocab):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0010_BulkFind'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'aantal':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'NonNegativeInteger'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'gewicht':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

                uom = uomnode.value if uomnode is not None else 'eenheden'
                hf.addLabel(self.graph, bnode, 'Gewicht van {} {}'.format(inode.value, uom), 'nl')
            if childname == 'beginperiode':
                    bnode = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE2021_BulkFindAssessment'))
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                    hf.addLabel(self.graph, bnode,\
                                'Datering van {} behorende bij {}'.format(hf.getLabel(self.graph, gnode),\
                                                                          hf.getLabel(self.graph, pnode)), 'nl')

                    bnode2 = hf.genID(self.graph, pnode, self.basens)
                    hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E52_Time-Span'))
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))

                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                    hf.addSchemaType(self.graph, self.ontns, cnode, bnode, childname, parentname)
                    hf.addRefIfExists(self.graph, cnode, child)

                    snode = tnode.find(self.sikbns + 'eindperiode')
                    if snode is not None:
                        childname = re.sub(self.sikbns, '', snode.tag)
                        key = 'periode'  # needed for inconsistent labeling by SIKB
                        dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                        hf.addSchemaType(self.graph, self.ontns, dnode, bnode, childname, parentname)
                        hf.addRefIfExists(self.graph, dnode, snode)

                    startdate = hf.getLabel(vocab, cnode) if (cnode is not None and vocab is not None)\
                                    else key + ' ' + hf.rawString(child.text)
                    enddate = hf.getLabel(vocab, dnode) if (dnode is not None and vocab is not None)\
                                    else key + ' ' + hf.rawString(snode.text)
                    hf.addLabel(self.graph, bnode2, 'Tijdspanne (van {} tot {}) behorende bij {}'.format(startdate, enddate, hf.getLabel(self.graph, gnode)), 'nl')
            if childname == 'doosId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))

    def monsterHandler(self, pnode, tnode, vocab):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0018_ContextSample'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'monstertype':
                key = 'monstertype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'monsterverwerking':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'beginperiode':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                hf.addLabel(self.graph, bnode,\
                            'Datering van {} behorende bij {}'.format(hf.getLabel(self.graph, gnode),\
                                                                      hf.getLabel(self.graph, pnode)), 'nl')

                bnode2 = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E52_Time-Span'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))

                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)

                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode, childname, parentname)
                    hf.addRefIfExists(self.graph, dnode, snode)

                startdate = hf.getLabel(vocab, cnode) if (cnode is not None and vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                enddate = hf.getLabel(vocab, dnode) if (dnode is not None and vocab is not None)\
                                else key + ' ' + hf.rawString(snode.text)
                hf.addLabel(self.graph, bnode2, 'Tijdspanne (van {} tot {}) behorende bij {}'.format(startdate, enddate, hf.getLabel(self.graph, gnode)), 'nl')
            if childname == 'verpakkingseenheidId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0010_BulkFind'))

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))
            if childname == 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P53i_is_former_or_current_location_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P53_has_former_or_current_location'))

    def vondstHandler(self, pnode, tnode, vocab):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'aantal':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)
                hf.addLabel(self.graph, bnode,\
                            'Meting van hoeveelheid behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

                uomnode = rdflib.Literal('number of units', datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))
                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if childname == 'gewicht':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)
                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

                uom = uomnode.value if uomnode is not None else 'eenheden'
                hf.addLabel(self.graph, bnode, 'Gewicht van {} {}'.format(inode.value, uom), 'nl')
            if childname == 'materiaalcategorie':
                key = 'materiaalcategorie'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'artefacttype':
                key = 'artefacttype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'beginperiode':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                hf.addLabel(self.graph, bnode,\
                            'Datering van {} behorende bij {}'.format(hf.getLabel(self.graph, gnode),\
                                                                      hf.getLabel(self.graph, pnode)), 'nl')

                bnode2 = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crmeh'] + 'EHE0099_ContextFindUseEventTimespan'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))

                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)

                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode, childname, parentname)
                    hf.addRefIfExists(self.graph, dnode, snode)

                startdate = hf.getLabel(vocab, cnode) if (cnode is not None and vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                enddate = hf.getLabel(vocab, dnode) if (dnode is not None and vocab is not None)\
                                else key + ' ' + hf.rawString(snode.text)
                hf.addLabel(self.graph, bnode2, 'Tijdspanne (van {} tot {}) behorende bij {}'.format(startdate, enddate, hf.getLabel(self.graph, gnode)), 'nl')
            if childname == 'geconserveerd':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'exposabel':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'gedeselecteerd':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'verpakkingseenheidId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0010_BulkFind'))

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))
            if childname == 'veldvondstId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E78_Collectiono'))

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))

    def veldvondstHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'verzamelwijze':
                key = 'verzamelwijze'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'vondstcontextId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P53_has_former_or_current_location'))

    def vondstcontextHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisLocatieTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'contexttype':
                key = 'contexttype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))
            if childname == 'stortId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))
            if childname == 'planumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))
            if childname == 'vullingId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))
            if childname == 'segmentId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))
            if childname == 'vakId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))
            if childname == 'boringId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))

        return gnode

    def boringHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))


    def vullingHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'vorm':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'kleur':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'textuur':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))

    def structuurHandler(self, pnode, tnode, vocab):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'structuurtype':
                key = 'structuurtype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'beginperiode':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                hf.addLabel(self.graph, bnode,\
                            'Datering van {} behorende bij {}'.format(hf.getLabel(self.graph, gnode),\
                                                                      hf.getLabel(self.graph, pnode)), 'nl')

                bnode2 = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E52_Time-Span'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))

                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)

                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode, childname, parentname)
                    hf.addRefIfExists(self.graph, dnode, snode)

                startdate = hf.getLabel(vocab, cnode) if (cnode is not None and vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                enddate = hf.getLabel(vocab, dnode) if (dnode is not None and vocab is not None)\
                                else key + ' ' + hf.rawString(snode.text)
                hf.addLabel(self.graph, bnode2, 'Tijdspanne (van {} tot {}) behorende bij {}'.format(startdate, enddate, hf.getLabel(self.graph, gnode)), 'nl')
            if childname == 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P53_has_former_or_current_location'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P53i_is_former_or_current_location_of'))

    def segmentHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'spoorId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))

    def stortHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'putId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))
            if childname == 'planumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))

    def planumHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'planumtype':
                key = 'planumtype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'putId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))

    def spoorHandler(self, pnode, tnode, vocab):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'grondspoortype':
                key = 'grondspoortype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'diepte':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)
                hf.addLabel(self.graph, bnode,\
                            'Meting van diepte behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

                bnode2 = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode2, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

                uom = uomnode.value if uomnode is not None else 'eenheden'
                hf.addLabel(self.graph, bnode2, 'Diepte van {} {}'.format(inode.value, uom), 'nl')
            if childname == 'beginperiode':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                hf.addLabel(self.graph, bnode,\
                            'Datering van {} behorende bij {}'.format(hf.getLabel(self.graph, gnode),\
                                                                      hf.getLabel(self.graph, pnode)), 'nl')

                bnode2 = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E52_Time-Span'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))

                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)

                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode, childname, parentname)
                    hf.addRefIfExists(self.graph, dnode, snode)

                startdate = hf.getLabel(vocab, cnode) if (cnode is not None and vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                enddate = hf.getLabel(vocab, dnode) if (dnode is not None and vocab is not None)\
                                else key + ' ' + hf.rawString(snode.text)
                hf.addLabel(self.graph, bnode2, 'Tijdspanne (van {} tot {}) behorende bij {}'.format(startdate, enddate, hf.getLabel(self.graph, gnode)), 'nl')

    def putHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))


    def vakHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'vaknummer':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                        'positiveInteger'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'dikte':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)
                hf.addLabel(self.graph, bnode,\
                            'Meting van dikte behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

                bnode2 = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode2, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

                uom = uomnode.value if uomnode is not None else 'eenheden'
                hf.addLabel(self.graph, bnode2, 'Dikte van {} {}'.format(inode.value, uom), 'nl')
            if childname == 'nap':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)
                hf.addLabel(self.graph, bnode,\
                            'Meting van Normaal Amsterdams Peil (NAP) behorende bij {}'.format(\
                                                                                        hf.getLabel(self.graph, gnode)),\
                                                                                        'nl')

                bnode2 = hf.genID(self.graph, pnode, self.basens)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode2, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

                uom = uomnode.value if uomnode is not None else 'eenheden'
                hf.addLabel(self.graph, bnode2, '{} {} Normaal Amsterdams Peil (NAP)'.format(inode.value, uom), 'nl')
            if childname == 'planumId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractBasisLocatieNaamTypeFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))

    def persoonHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

        achternaam = ''
        initialen = ''
        titel = ''
        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'telefoon':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'email':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'naam':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)

                parentname = childname
                for element in child:
                    childname = re.sub(self.sikbns, '', element.tag)
                    if childname == 'achternaam':
                        snode = child.find(self.sikbns + 'tussenvoegsel')
                        achternaam = element.text + ', ' + snode.text if snode is not None else element.text  # extract 'tussenvoegsel' if available

                        enode = rdflib.Literal(achternaam, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                               parentname + '_' + childname))
                    if childname == 'voornaam':
                        snode = child.find(self.sikbns + 'initialen')
                        voornaam = element.text + ', ' + snode.text if snode is not None else element.text  # extract 'initialen' if available

                        enode = rdflib.Literal(voornaam, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                               parentname + '_' + childname))
                    if childname == 'initialen':
                        snode = child.find(self.sikbns + 'voornaam')
                        if snode is None:
                            initialen = hf.rawString(element.text)
                            enode = rdflib.Literal(initialen, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                            hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                                   parentname + '_' + childname))
                    if childname == 'titel':
                        titel = hf.rawString(element.text)
                        enode = rdflib.Literal(titel, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                               parentname + '_' + childname))
                name = voornaam if initialen == '' else initialen
                titel = titel if titel == '' else titel + ' '
                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) + " ({}{}, {})".format(titel, achternaam, name), 'nl')
            hf.addLabel(self.graph, bnode,\
                        'Persoon met naam {}{}, {}'.format(titel, achternaam, name), 'nl')

    def geolocatieHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractGeoObjectFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'geometrie':
                cnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)

                (gmlString, gmlID, gmlType) = hf.gmlLiteralOf(self.et, child)
                gmlnode = rdflib.Literal(gmlString, datatype=rdflib.URIRef(self.nss['geosparql'] + 'GMLLiteral'))
                hf.addProperty(self.graph, cnode, gmlnode, rdflib.URIRef(self.nss['geosparql'] + 'asGML'))

                idNode = rdflib.Literal(gmlID, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, cnode, idNode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
                hf.addLabel(self.graph, cnode, 'Geometrie {} ({})'.format(gmlID, gmlType), 'nl')

    def hoogtemetingHandler(self, pnode, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))

        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'methode':
                key = 'hoogtemetingmethode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname, parentname)
                hf.addRefIfExists(self.graph, cnode, child)
            if childname == 'nap':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

                uom = uomnode.value if uomnode is not None else 'eenheden'
                hf.addLabel(self.graph, bnode, '{} {} Normaal Amsterdams Peil (NAP)'.format(inode.value, uom), 'nl')
            if childname == 'geolocatieId':
                (cnode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.addType(self.graph, cnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

                #hf.addLabel(self.graph, cnode, 'Geografische locatie van {}'.format(hf.getLabel(self.graph, gnode)), 'nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.nss['crm'] + 'P7_took_place_at'))
                hf.addProperty(self.graph, cnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P7i_witnessed'))

    def attribuutHandler(self, pnode, tnode):
        child = tnode.find(self.sikbns + 'objectId')
        (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
        if not exists:
            hf.extractGenericObjectFields(self.graph, enode, child)
            hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E1_CRM_Entity'))

        value = None
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'geheelgetal':
                value = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'integer'))
            if childname == 'decimaalgetal':
                value = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
            if childname == 'referentieId':
                value = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
            if childname == 'text':
                value = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
            if childname == 'jaNee':
                value = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))

        atypeID = tnode.find(self.sikbns + 'attribuuttypeId').text
        atype = None
        for atnode in self.troot.findall(self.sikbns + 'attribuuttype'):
            if atnode.attrib[self.sikbns + 'id'] == atypeID:
                atype = atnode
                break

        if atype is not None:
            # add new relation type
            label = ''
            for child in atype.getchildren():
                childname = re.sub(self.sikbns, '', child.tag)
                if childname == 'attribuutnaam':
                    label = rdflib.Literal(hf.rawString(child.text))

            bnode = hf.genID(self.graph, pnode, self.basens)
            hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['rdf'] + 'Property'))
            hf.addProperty(self.graph, bnode, rdflib.URIRef(self.nss['rdf'] + 'value'), rdflib.URIRef(self.nss['rdfs'] + 'subPropertyOf'))
            if label != '':
                hf.addLabel(self.graph, bnode, label, 'nl')

            # use new relation type to link attribute with value
            hf.addProperty(self.graph, enode, value, bnode)

            for child in atype.getchildren():
                childname = re.sub(self.sikbns, '', child.tag)
                if childname == 'informatie':
                    info = rdflib.Literal(hf.rawString(child.text), lang='nl')
                    hf.addProperty(self.graph, bnode, info, \
                                   rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + 'attribuuttype' + '_' + childname))
                if childname == 'waardetype':
                    key = 'waardetype'  # needed for inconsistent labeling by SIKB
                    cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                    hf.addType(self.graph, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + childname.title() \
                                                             + '.' + hf.rawString(child.text.title())))
                    hf.addProperty(self.graph, bnode, cnode, \
                                   rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + 'attribuuttype' + '_' + childname))

    def objectrelatieHandler(self, tnode):
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractBasisTypeFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['owl'] + 'ObjectProperty'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'objectrelatietype':
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
                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) +\
                               " specificeert relatie '{}' tussen object '{}' (lhs) en object '{}' (rhs)".format(relation,\
                                                                                                           object1Class,\
                                                                                                           object2Class), 'nl')

            if childname == 'object1Id':
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
        (gnode, exists) = hf.getNodeFromBaseType(self.graph, self.basens, self.sikbns, tnode)
        if not exists:
            hf.extractGenericObjectFields(self.graph, gnode, tnode)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document'))

        hf.addProperty(self.graph, self.groot, gnode, rdflib.URIRef(self.nss['crm'] + 'P67_refers_to'))
        parentname = re.sub(self.sikbns, '', tnode.tag)
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'bronCode':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
                hf.updateLabel(self.graph, gnode,\
                               hf.getLabel(self.graph, gnode) + " van concept '{}'".format(hf.rawString(child.text)), 'nl')
            if childname == 'standaardCode':
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'bronOmschrijving':
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + \
                                                                       parentname + '_' + childname))
            if childname == 'bronCodeLijst':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)

                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
            if childname == 'naamCodeLijst':
                bnode = hf.genID(self.graph, pnode, self.basens)
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname, parentname)

                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
            if childname == 'historyId':
                (enode, exists) = hf.getNodeFromElem(self.graph, self.basens, child)
                if not exists:
                    hf.extractGenericObjectFields(self.graph, enode, child)
                    hf.addType(self.graph, enode, rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document'))

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['rdfs'] + 'subClassOf'))

    def conceptHandler(self):
        # existing concepts
        for element in self.troot:
            child = rdflib.URIRef(self.basens + 'SIKBID_' + hf.getID(element, self.sikbns))
            name = re.sub(self.sikbns, '', element.tag)

            if name in ('archis', 'waarneming', 'attribuut', 'attribuuttype'):
                continue

            # if name == 'archis':
            #    hf.extractBasisTypeFields(self.graph, child, element, self.sikbns)
            if name == 'bestand':
                hf.extractBasisTypeFields(self.graph, child, element, self.sikbns)
            if name == 'boring':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'digitaalmedium':
                hf.extractBasisTypeFields(self.graph, child, element, self.sikbns)
            if name == 'document':
                hf.extractBasisTypeFields(self.graph, child, element, self.sikbns)
            if name == 'doos':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'dossier':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'foto':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'geolocatie':
                hf.extractGeoObjectFields(self.graph, child, element, self.sikbns)
            if name == 'hoogtemeting':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'monster':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'organisatie':
                hf.extractBasisTypeFields(self.graph, child, element, self.sikbns)
            if name == 'persoon':
                hf.extractBasisTypeFields(self.graph, child, element, self.sikbns)
            if name == 'planum':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'project':
                hf.extractBasisTypeFields(self.graph, child, element, self.sikbns)
            if name == 'projectlocatie':
                hf.extractBasisTypeFields(self.graph, child, element, self.sikbns)
            if name == 'put':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'segment':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'spoor':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'stort':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'structuur':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'tekening':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'vak':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'veldvondst':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'verpakkingseenheid':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'vindplaats':
                hf.extractBasisLocatieNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'vondst':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            if name == 'vondstcontext':
                hf.extractBasisLocatieTypeFields(self.graph, child, element, self.sikbns)
            if name == 'vulling':
                hf.extractBasisNaamTypeFields(self.graph, child, element, self.sikbns)
            # if name == 'waarneming':
            #    hf.extractBasisLocatieTypeFields(self.graph, child, element, self.sikbns)
            # if name == 'attribuuttype':
            #    hf.extractGenericObjectFields(self.graph, child, element, self.sikbns)
            # if name == 'attribuut':
            #    hf.extractGenericObjectFields(self.graph, child, element, self.sikbns)
            if name == 'objectrelatie':
                hf.extractBasisTypeFields(self.graph, child, element, self.sikbns)
            if name == 'codereferentie':
                hf.extractGenericObjectFields(self.graph, child, element, self.sikbns)

            hf.addType(self.graph, child, rdflib.URIRef(self.ontns + 'SIKB0102_Schema_' + name.title()))
