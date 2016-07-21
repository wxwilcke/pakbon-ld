#!/usr/bin/python3

import rdflib
import helpFunctions as hf
import aligner as al
import re
import itertools
from collections import namedtuple


class Protocol0102:

    def __init__(self, et, tree, default_graphs, namespace, sikbns, vocab, align='off', endpoint='', geoRef=False,\
                 interactive=True):
        self.et = et
        self.vocab = vocab
        self.sikbns = '{' + sikbns + '}'
        self.basens = namespace['base'] + '/res/'
        self.ontns = namespace['base'] + '/ont/'
        self.vocns = namespace['base'] + '/voc/'
        self.align = align
        self.endpoint = endpoint
        self.geoRef = geoRef
        self.interactive = interactive
        self.default_graphs = default_graphs

        self.ReturnValues = namedtuple('ReturnValues', 'node, altnode')

        # root of protocol
        self.troot = tree.getroot()

        # init new graph
        version = ''
        timestamp = ''
        if 'versie' in self.troot.attrib.keys():  # versie
            version = self.troot.attrib['versie']
        if 'timestamp' in self.troot.attrib.keys():  # timestamp
            timestamp = self.troot.attrib['timestamp']

        gid = hf.genHash(None, None, [], salt='SIKB Pakbon' + version + timestamp)
        self.graph = rdflib.Graph(identifier=gid)

        hf.setGraphNamespaceIDs(self.graph, namespace)
        self.nss = dict(ns for ns in self.graph.namespace_manager.namespaces())

        self.groot = rdflib.URIRef(self.basens + gid)

        # set type of protocol
        hf.addType(self.graph, self.groot, rdflib.URIRef(self.nss['crm'] + 'E31_Document'))

        # root attributes
        child = rdflib.Literal(gid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
        hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
        child = rdflib.Literal('SIKB Archeologisch Protocol 0102 (ofwel Pakbon) conform de RDF standaard', lang='nl')
        hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['rdfs'] + 'label'))
        child = rdflib.Literal('RDF-compliant SIKB Archaeological Protocol 0102 (aka Pakbon)', lang='en')
        hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['rdfs'] + 'label'))
        if version != '':  # versie
            child = rdflib.Literal(version, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
            hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['prism'] + 'versionIdentifier'))
        if timestamp != '':  # timestamp
            child = rdflib.Literal(timestamp, datatype=rdflib.URIRef(self.nss['xsd'] + 'dateTime'))
            hf.addProperty(self.graph, self.groot, child, rdflib.URIRef(self.nss['dcterms'] + 'issued'))

        # process elements
        self.gproject = self.projectHandler(self.troot.find(self.sikbns + 'project'))
        for child in self.troot.iter(self.sikbns + 'projectlocatie'):
            self.projectlocatieHandler(child)
        for child in self.troot.iter(self.sikbns + 'vindplaats'):
            self.vindplaatsHandler(child)
        for child in self.troot.iter(self.sikbns + 'organisatie'):
            self.organisatieHandler(child)
        for child in self.troot.iter(self.sikbns + 'persoon'):
            self.persoonHandler(child)
        for child in self.troot.iter(self.sikbns + 'geolocatie'):
            self.geolocatieHandler(child)
        for child in self.troot.iter(self.sikbns + 'dossier'):
            self.dossierHandler(child)
        for child in self.troot.iter(self.sikbns + 'document'):
            self.documentHandler(child)
        for child in self.troot.iter(self.sikbns + 'bestand'):
            self.bestandHandler(child)
        for child in self.troot.iter(self.sikbns + 'digitaalmedium'):
            self.digitaalmediumHandler(child)
        for child in self.troot.iter(self.sikbns + 'tekening'):
            self.tekeningHandler(child)
        for child in self.troot.iter(self.sikbns + 'foto'):
            self.fotoHandler(child)
        for child in self.troot.iter(self.sikbns + 'doos'):
            self.doosHandler(child)
        for child in self.troot.iter(self.sikbns + 'verpakkingseenheid'):
            self.verpakkingseenheidHandler(child)
        for child in self.troot.iter(self.sikbns + 'monster'):
            self.monsterHandler(child)
        for child in self.troot.iter(self.sikbns + 'vondst'):
            self.vondstHandler(child)
        for child in self.troot.iter(self.sikbns + 'veldvondst'):
            self.veldvondstHandler(child)
        for child in self.troot.iter(self.sikbns + 'vondstcontext'):
            self.vondstcontextHandler(child)
        for child in self.troot.iter(self.sikbns + 'boring'):
            self.boringHandler(child)
        for child in self.troot.iter(self.sikbns + 'vulling'):
            self.vullingHandler(child)
        for child in self.troot.iter(self.sikbns + 'structuur'):
            self.structuurHandler(child)
        for child in self.troot.iter(self.sikbns + 'segment'):
            self.segmentHandler(child)
        for child in self.troot.iter(self.sikbns + 'spoor'):
            self.spoorHandler(child)
        for child in self.troot.iter(self.sikbns + 'vak'):
            self.vakHandler(child)
        for child in self.troot.iter(self.sikbns + 'stort'):
            self.stortHandler(child)
        for child in self.troot.iter(self.sikbns + 'planum'):
            self.planumHandler(child)
        for child in self.troot.iter(self.sikbns + 'put'):
            self.putHandler(child)
        for child in self.troot.iter(self.sikbns + 'hoogtemeting'):
            self.hoogtemetingHandler(child)
        #  for child in self.troot.iter(self.sikbns + 'waarneming'):
            #  self.waarnemingHandler(child)
        for child in self.troot.iter(self.sikbns + 'attribuuttype'):
            self.attribuuttypeHandler(child)
        for child in self.troot.iter(self.sikbns + 'attribuut'):
            self.attribuutHandler(child)
        """
        #  for child in self.troot.iter(self.sikbns + 'archis'):
            #  self.archisHandler(child)
        # for child in self.troot.iter(self.sikbns + 'attribuuttype'):
            #  self.attribuuttypeHandler(child)
        """
        for child in self.troot.iter(self.sikbns + 'objectrelatie'):
            self.objectrelatieHandler(child)
        for child in self.troot.iter(self.sikbns + 'codereferentie'):
            self.codereferentieHandler(child)

    def projectHandler(self, tnode):
        hid = hf.genHash(tnode, self.sikbns, ['onderzoeksmeldingsnummer', 'onderzoektype'])

        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)

        hf.extractBasisTypeFields(self.graph, gnode, tnode, self.sikbns)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0001_EHProject'))

        hf.addProperty(self.graph, self.groot, gnode, rdflib.URIRef(self.nss['crm'] + 'P70_documents'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'projectnaam':
                if child.text is None:
                    continue
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))

                hf.updateLabel(self.graph, gnode, "({})".format(hf.rawString(child.text)), 'nl')
            if childname == 'startdatum':
                if child.text is None:
                    continue
                bhid = hf.genHash(tnode, self.sikbns, ['startdatum', 'einddatum'], 'EHE0021_EHProjectTimespan')
                bnode = hf.getNode(self.graph, bhid)
                if bnode is not None:
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P4_has_time-span'))
                    continue

                bnode = rdflib.URIRef(self.basens + bhid)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0021_EHProjectTimespan'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P4_has_time-span'))
                inode = rdflib.Literal(bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))

                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))

                dnode = None
                snode = tnode.find(self.sikbns + 'einddatum')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    dnode = rdflib.Literal(hf.rawString(snode.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                    hf.addProperty(self.graph, bnode, dnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                           childname))

                enddate = dnode.value if dnode is not None else '?'
                hf.addLabel(self.graph, bnode,\
                            'Tijdspanne (van {} tot {})'.format(cnode.value, enddate), 'nl')

            if childname == 'onderzoeksmeldingsnummer':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))

            if childname == 'onderzoektype':
                if child.text is None:
                    continue
                key = 'verwerving'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)

                hf.addRefIfExists(self, cnode, child)
            if childname == 'omschrijving':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))

            if childname == 'bevoegdGezag':
                if child.text is None:
                    continue
                bhid = hf.genHash(child, self.sikbns, ['organisatieId', 'persoonId'])
                bnode = hf.getNode(self.graph, bhid)
                if bnode is not None:
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P11_had_participant'))
                    continue

                bnode = rdflib.URIRef(self.basens + hid + bhid)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P11_had_participant'))
                hf.addLabel(self.graph, bnode,\
                            re.sub(self.sikbns, '', child.tag).title() + ' behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')
                inode = rdflib.Literal(hid + bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))

                for element in child:
                    if element.tag == self.sikbns + 'organisatieId':
                        enode = self.organisatieHandler(hf.getTreeNodeByID(self.troot, self.sikbns, element.text), gnode).node
                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))
                    if element.tag == self.sikbns + 'persoonId':
                        enode = self.persoonHandler(hf.getTreeNodeByID(self.troot, self.sikbns, element.text), gnode).node
                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))

            if childname == 'uitvoerder':
                if child.text is None:
                    continue
                bhid = hf.genHash(child, self.sikbns, ['uitvoerdercode', 'opgravingsleiderPersoonId',\
                                                       'depotContactPersoonId'])
                bnode = hf.getNode(self.graph, bhid)
                if bnode is not None:
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P14_carried_out_by'))
                    continue

                bnode = rdflib.URIRef(self.basens + hid + bhid)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P14_carried_out_by'))
                inode = rdflib.Literal(hid + bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))

                
                uitvoerdercode = ''
                for element in child:
                    childname = re.sub(self.sikbns, '', element.tag)
                    if childname == 'uitvoerdercode':  #
                        if child.text is None:
                            continue
                        key = 'uitvoerder'  # needed for inconsistent labeling by SIKB
                        enode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(element.text))
                        hf.addSchemaType(self.graph, self.ontns, enode, bnode, childname)
                        hf.addRefIfExists(self, enode, element)

                        uitvoerdercode = hf.rawString(element.text) + ' '
                    if childname == 'opgravingsleiderPersoonId':
                        if child.text is None:
                            continue
                        enode = self.persoonHandler(hf.getTreeNodeByID(self.troot, self.sikbns, element.text), gnode).node
                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))
                    if childname == 'depotContactPersoonId':
                        if child.text is None:
                            continue
                        enode = self.persoonHandler(hf.getTreeNodeByID(self.troot, self.sikbns, element.text), gnode).node
                        hf.addProperty(self.graph, bnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))

                hf.addLabel(self.graph, bnode,\
                            re.sub(self.sikbns, '', child.tag).title() + ' {}behorende bij {}'.format(\
                            uitvoerdercode, hf.getLabel(self.graph, gnode)), 'nl')

        # add unexisting concept: 'production' and 'bestanden'
        bhid = hf.genHash(None, None, [], salt='E12_Production')
        bnode = rdflib.URIRef(self.basens + hid + bhid)
        hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E12_Production'))
        hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P9_consists_of'))
        hf.addLabel(self.graph, bnode, 'Documentatie (Digitaal) behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

        ohid = hf.genHash(None, None, [], salt='E84_Information_Carrier')
        onode = rdflib.URIRef(self.basens + hid + ohid)
        hf.addType(self.graph, onode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))
        hf.addProperty(self.graph, bnode, onode, rdflib.URIRef(self.nss['crm'] + 'P108_has_produced'))
        hf.addLabel(self.graph, onode, 'Bestanden behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

        return self.ReturnValues(node=gnode, altnode=onode)

    def projectlocatieHandler(self, tnode):
        geonode = None
        geomnode = None
        geonodeID = ''
        geoIDtnode = tnode.find(self.sikbns + 'geolocatieId')
        if geoIDtnode is not None:
            geotnode = hf.getTreeNodeByID(self.troot, self.sikbns, geoIDtnode.text)
            if geotnode is not None:
                geonode, geomnode = self.geolocatieHandler(geotnode)
                geonodeID = hf.getNodeID(self.graph, geonode)

        hid = hf.genHash(tnode, self.sikbns, ['toponiem'], salt=geonodeID)
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisTypeFields(self.graph, gnode, tnode, self.sikbns, nolabel=True, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0003_AreaOfInvestigation'))
        hf.addProperty(self.graph, self.gproject.node, gnode, rdflib.URIRef(self.nss['crm'] + 'P7_took_place_at'))

        if geonode is not None:
            hf.addProperty(self.graph, gnode, geonode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
            hf.addProperty(self.graph, geonode, gnode, rdflib.URIRef(self.nss['crm'] + 'P87i_identifies'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'provinciecode':
                if child.text is None:
                    continue
                key = 'provincie'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'gemeentecode':
                if child.text is None:
                    continue
                key = 'gemeente'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'plaatscode':
                if child.text is None:
                    continue
                key = 'plaats'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'toponiem':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
                hf.addLabel(self.graph, gnode, "Projectlocatie ({})".format(hf.rawString(child.text)), 'nl')
                hf.updateLabel(self.graph, geonode, "({})".format(hf.rawString(child.text)), 'nl')
                hf.updateLabel(self.graph, geomnode, "({})".format(hf.rawString(child.text)), 'nl')
            if childname == 'kaartblad':
                if child.text is None:
                    continue
                key = 'kaartblad'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'geolocatieId':
                continue

        return self.ReturnValues(node=gnode, altnode=None)

    def vindplaatsHandler(self, tnode):
        geonode = None
        geomnode = None
        geonodeID = ''
        geoIDtnode = tnode.find(self.sikbns + 'geolocatieId')
        if geoIDtnode is not None:
            geotnode = hf.getTreeNodeByID(self.troot, self.sikbns, geoIDtnode.text)
            if geotnode is not None:
                geonode, geomnode = self.geolocatieHandler(geotnode)
                geonodeID = hf.getNodeID(self.graph, geonode)

        hid = hf.genHash(tnode, self.sikbns, ['vondstmeldingsnummer', 'waarnemingsnummer'], salt=geonodeID)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0004_SiteSubDivision'))
        hf.addProperty(self.graph, self.gproject.node, gnode, rdflib.URIRef(self.nss['crm'] + 'P7_took_place_at'))

        if geonode is not None:
            hf.addProperty(self.graph, gnode, geonode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
            hf.addProperty(self.graph, geonode, gnode, rdflib.URIRef(self.nss['crm'] + 'P87i_identifies'))


        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'vondstmeldingsnummer':
                if child.text is None:
                    continue  # until direct linking in Archis is possible
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                        'positiveInteger'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'waarnemingsnummer':
                if child.text is None:
                    continue  # until direct linking in Archis is possible
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                        'positiveInteger'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'beginperiode':
                if child.text is None:
                    continue
                bhid = hf.genHash(tnode, self.sikbns, ['beginperiode', 'eindperiode'], 'E52_Time-Span')
                bnode = hf.getNode(self.graph, bhid)
                if bnode is not None:
                    hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P4_has_time-span'))
                    continue

                bnode = rdflib.URIRef(self.basens + bhid)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crmeh'] + 'E52_Time-Span'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P4_has_time-span'))
                inode = rdflib.Literal(bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))



                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode, childname)
                hf.addRefIfExists(self, cnode, child)

                enddate = "?"
                dnode = None
                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode, childname)
                    hf.addRefIfExists(self, dnode, snode)
                    
                    enddate = hf.getLabel(self.vocab, dnode) if (dnode is not None and self.vocab is not None)\
                                    else key + ' ' + hf.rawString(snode.text)

                startdate = hf.getLabel(self.vocab, cnode) if (cnode is not None and self.vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                hf.addLabel(self.graph, bnode, 'Tijdspanne (van {} tot {})'.format(startdate, enddate), 'nl')

            if childname == 'vindplaatstype':
                if child.text is None:
                    continue
                key = 'complextype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'geolocatieId':
                continue

        return self.ReturnValues(node=gnode, altnode=None)

    def dossierHandler(self, tnode):
        bhid = hf.genHash(None, None, [], salt='dossier')
        bhid = hf.getNodeID(self.graph, self.gproject.node) + bhid
        bnode = hf.getNode(self.graph, bhid)
        if bnode is None:
            bnode = rdflib.URIRef(self.basens + bhid)
            hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E12_Production'))
            hf.addProperty(self.graph, self.gproject.node, bnode, rdflib.URIRef(self.nss['crm'] + 'P9_consists_of'))
            hf.addLabel(self.graph, bnode, "Documentatie (Analoog) behorende bij {}".format(hf.getLabel(self.graph, self.gproject.node)), 'nl')

        nodeIDs = ''
        nodes = []
        for doctnodeID in tnode.findall(self.sikbns + 'documentId'):
            doctnode = hf.getTreeNodeByID(self.troot, self.sikbns, doctnodeID.text)
            if doctnode is not None:
                node = self.documentHandler(doctnode).node
                nodeIDs += hf.getNodeID(self.graph, node)
                nodes.append(node)

        hid = hf.genHash(tnode, self.sikbns, ['dossiertype'], salt=nodeIDs)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is None:
            gnode = rdflib.URIRef(self.basens + hid)
            hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
            hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))
            hf.updateLabel(self.graph, gnode, "behorende bij {}".format(hf.getLabel(self.graph, self.gproject.node)), 'nl')


            hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P108_has_produced'))
            hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P108i_was_produced_by'))

            for doc in nodes:
                hf.addProperty(self.graph, gnode, doc, rdflib.URIRef(self.nss['crm'] + 'P128_carries'))
                hf.addProperty(self.graph, doc, gnode, rdflib.URIRef(self.nss['crm'] + 'P128i_is_carried_by'))


            for child in tnode.getchildren():
                childname = re.sub(self.sikbns, '', child.tag)
                if childname == 'dossiertype':
                    cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                    hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                           childname))
                if childname == 'documentId':
                    continue

    def bestandHandler(self, tnode):
        hid = hf.genHash(tnode, self.sikbns, ['bestandsnaam', 'bestandtype'])
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

        hf.addProperty(self.graph, self.gproject.altnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P128_carries'))
        hf.addProperty(self.graph, gnode, self.gproject.altnode, rdflib.URIRef(self.nss['crm'] + 'P128i_is_carried_by'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'bestandId':
                if child.text is None:
                    continue
                enode = self.bestandHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['dcterms'] + 'isPartOf'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['dcterms'] + 'hasPart'))
            if childname == 'bestandsnaam':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'bestandtype':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'bestandsinhoud':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
                hf.updateLabel(self.graph, gnode, "({})".format(hf.rawString(child.text)), 'nl')
            if childname == 'software':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'codeboek':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'digitaalmediumId':
                if child.text is None:
                    continue
                enode = self.digitaalmediumHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['dcterms'] + 'medium'))

        return self.ReturnValues(node=gnode, altnode=None)

    def digitaalmediumHandler(self, tnode):
        hid = hf.genHash(tnode, self.sikbns, ['digitaalmediumtype'])
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'digitaalmediumtype':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
                hf.updateLabel(self.graph, gnode, "({})".format(hf.rawString(child.text)), 'nl')

        return self.ReturnValues(node=gnode, altnode=None)

    def documentHandler(self, tnode):
        hid = hf.genHash(tnode, self.sikbns, ['isbn', 'issn', 'titel', 'auteur', 'documenttype'])
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E31_Document'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'documenttype':
                if child.text is None:
                    continue
                key = 'documenttype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'titel':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
                hf.updateLabel(self.graph, gnode, "('{}'".format(hf.rawString(child.text)), 'nl')
            if childname == 'auteur':
                if child.text is None:
                    continue
                cnode = al.fuzzyTextMatchElseNew(self.graph, self.default_graphs, self.basens, rdflib.URIRef(self.ontns + 'SIKB0102S_Persoon'),\
                                                                            [rdflib.URIRef(self.nss['rdfs'] + 'label')],\
                                                                            hf.rawString(child.text), align=self.align,\
                                                                            endpoint=self.endpoint, interactive=self.interactive)

                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
                hf.updateLabel(self.graph, gnode, "; {})".format(hf.rawString(child.text)), 'nl')
            if childname == 'jaar':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'gYear'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'serie':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'paginas':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'uitgever':
                if child.text is None:
                    continue
                cnode = al.fuzzyTextMatchElseNew(self.graph, self.default_graphs, self.basens, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'),\
                                                                            [rdflib.URIRef(self.nss['rdfs'] + 'label')],\
                                                                            hf.rawString(child.text), align=self.align,\
                                                                            endpoint=self.endpoint, interactive=self.interactive)

                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'uitgavePlaats':
                if child.text is None:
                    continue
                cnode = al.fuzzyTextMatchElseNew(self.graph, self.default_graphs, self.basens, rdflib.URIRef(self.ontns + 'SIKB0102S_'\
                                                                                       + childname),\
                                                                            [rdflib.URIRef(self.nss['rdfs'] + 'label')],\
                                                                            hf.rawString(child.text), align=self.align,\
                                                                            endpoint=self.endpoint, interactive=self.interactive)

                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
                if self.geoRef:
                    point = hf.genGeoRef(self.graph, self.basens, placename=child.text, interactive=self.interactive)
                    if point is not None:
                        hf.addProperty(self.graph, cnode, point, rdflib.URIRef(self.nss['locn'] + 'geometry'))
            if childname == 'redacteur':
                if child.text is None:
                    continue
                cnode = al.fuzzyTextMatchElseNew(self.graph, self.default_graphs, self.basens, rdflib.URIRef(self.ontns + 'SIKB0102S_Persoon'),\
                                                                            [rdflib.URIRef(self.nss['rdfs'] + 'label')],\
                                                                            hf.rawString(child.text), align=self.align,\
                                                                            endpoint=self.endpoint, interactive=self.interactive)

                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'titelContainer':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'issn':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'isbn':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'bestandId':
                if child.text is None:
                    continue
                enode = self.bestandHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P67_refers_to'))
                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P67i_is_referred_to_by'))

        return self.ReturnValues(node=gnode, altnode=None)

    def organisatieHandler(self, tnode, gpnode=None):
        hid = hf.genHash(tnode, self.sikbns, ['naam', 'email', 'telefoon'])
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gproject = gpnode if gpnode is not None else self.gproject.node

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisTypeFields(self.graph, gnode, tnode, self.sikbns, nolabel=True, gpnode=gproject)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'naam':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
                hf.addLabel(self.graph, gnode, "Organisatie ({})".format(hf.rawString(child.text)), 'nl')
            if childname == 'telefoon':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'email':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'contactpersoonId':
                if child.text is None:
                    continue
                enode = self.persoonHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P107_has_current_or_former_member'))
            if childname == 'adres':
                if child.text is None:
                    continue
                bhid = hf.genHash(child, self.basens, ['straat', 'huisnummer', 'postcode', 'plaatsnaam', 'gemeente',\
                                                       'provincie', 'land'])
                bnode = rdflib.URIRef(self.basens + hid + bhid)
                inode = rdflib.Literal(hid + bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname)
                hf.addLabel(self.graph, bnode,\
                            'Adres behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

                streetname = ''
                housenumber = ''
                postalcode = ''
                placename = ''
                countryname = ''
                for element in child:
                    childname = re.sub(self.sikbns, '', element.tag)
                    if element.tag == self.sikbns + 'straat':  # until index is available
                        if element.text is None:
                            continue
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                               childname))
                        streetname = element.text
                    if element.tag == self.sikbns + 'huisnummer':
                        if element.text is None:
                            continue
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'positiveInteger'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                               childname))
                        housenumber = element.text
                    if element.tag == self.sikbns + 'postcode':
                        if element.text is None:
                            continue
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                               childname))
                        postalcode = element.text
                    if element.tag == self.sikbns + 'plaatsnaam':  # until index is available
                        if element.text is None:
                            continue
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                               childname))
                        placename = element.text
                    if element.tag == self.sikbns + 'gemeente':  # until index is available
                        if element.text is None:
                            continue
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                               childname))
                    if element.tag == self.sikbns + 'provincie':  # until index is available
                        if element.text is None:
                            continue
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                               childname))
                    if element.tag == self.sikbns + 'land':  # until index is available
                        if element.text is None:
                            continue
                        cnode = rdflib.Literal(hf.rawString(element.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                                  'string'))
                        hf.addProperty(self.graph, bnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                               childname))
                        countryname = element.text

                if self.geoRef:
                    point = hf.genGeoRef(self.graph, self.basens, housenumber=housenumber, streetname=streetname,\
                                         placename=placename, countryname=countryname, postalcode=postalcode,\
                                        interactive=self.interactive)
                    if point is not None:
                        hf.addProperty(self.graph, gnode, point, rdflib.URIRef(self.nss['locn'] + 'geometry')) 

        return self.ReturnValues(node=gnode, altnode=None)

    def tekeningHandler(self, tnode):
        nodes = []
        for ttnode in tnode.findall(self.sikbns + 'bestandId'):
            ttnode = hf.getTreeNodeByID(self.troot, self.sikbns, ttnode.text)
            nodes.append(self.bestandHandler(ttnode).node)

        nodeIDs = ''
        for node in nodes:
            nodeIDs += hf.getNodeID(self.graph, node)

        hid = hf.genHash(tnode, self.sikbns, ['tekeningfototype', 'tekeningmateriaal', 'tekeningformaat',\
                                             'tekenaar', 'schaal', 'tekeningdatum'], salt=nodeIDs)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0016_RecordDrawing'))

        for enode in nodes:
            hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))
            hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))  # for easy navigation

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'tekeningtype':
                if child.text is None:
                    continue
                key = 'tekeningfototype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)

                if 'codereferentieId' in child.attrib:
                    treeNode = hf.getTreeNodeByID(self.troot, self.sikbns, child.attrib['codereferentieId'])
                    crnode = self.codereferentieHandler(treeNode).node
                    if crnode is not None:
                        hf.addProperty(self.graph, cnode, crnode, rdflib.URIRef(self.nss['crm'] + 'P71i_is_listed_in'))
            if childname == 'tekeningmateriaal':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'tekeningformaat':
                if child.text is None:
                    continue
                key = 'papierformaat'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'tekenaar':
                if child.text is None:
                    continue
                cnode = al.fuzzyTextMatchElseNew(self.graph, self.default_graphs, self.basens, rdflib.URIRef(self.ontns + 'SIKB0102S_Persoon'),\
                                                                            [rdflib.URIRef(self.nss['rdfs'] + 'label')],\
                                                                            hf.rawString(child.text), align=self.align,\
                                                                            endpoint=self.endpoint, interactive=self.interactive)

                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'schaal':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'tekeningdatum':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'tekeningonderwerp':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
                hf.updateLabel(self.graph, gnode, "met betrekking tot '{}'".format(hf.rawString(child.text)), 'nl')
            if childname == 'bestandId':
                continue
            if childname == 'vondstcontextId':
                if child.text is None:
                    continue
                enode = self.vondstcontextHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P70_documents'))
            if childname == 'vondstId':
                if child.text is None:
                    continue
                enode = self.vondstHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))

        return self.ReturnValues(node=gnode, altnode=None)

    def fotoHandler(self, tnode):
        nodes = []
        for ttnode in tnode.findall(self.sikbns + 'bestandId'):
            ttnode = hf.getTreeNodeByID(self.troot, self.sikbns, ttnode.text)
            nodes.append(self.bestandHandler(ttnode).node)

        nodeIDs = ''
        for node in nodes:
            nodeIDs += hf.getNodeID(self.graph, node)

        hid = hf.genHash(tnode, self.sikbns, ['opnametype', 'opnamedatum', 'fotograaf'], salt=nodeIDs)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0017_RecordPhotograph'))

        for enode in nodes:
            hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of'))
            hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))  # for easy navigation

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'opnametype':
                if child.text is None:
                    continue
                key = 'tekeningfototype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'opnamedatum':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'date'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'fotograaf':
                if child.text is None:
                    continue
                cnode = al.fuzzyTextMatchElseNew(self.graph, self.default_graphs, self.basens, rdflib.URIRef(self.ontns + 'SIKB0102S_Persoon'),\
                                                                            [rdflib.URIRef(self.nss['rdfs'] + 'label')],\
                                                                            hf.rawString(child.text), align=self.align,\
                                                                            endpoint=self.endpoint, interactive=self.interactive)

                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'opnamemedium':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'fotoonderwerp':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
                hf.updateLabel(self.graph, gnode, "met betrekking tot '{}'".format(hf.rawString(child.text)), 'nl')
            if childname == 'bestandId':
                continue
            if childname == 'vondstcontextId':
                if child.text is None:
                    continue
                enode = self.vondstcontextHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P70_documents'))
            if childname == 'vondstId':
                if child.text is None:
                    continue
                enode = self.vondstHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P129_is_about'))

        return self.ReturnValues(node=gnode, altnode=None)

    def doosHandler(self, tnode):
        bhid = hf.genHash(None, None, [], salt='doos')
        bnode = hf.getNode(self.graph, hf.getNodeID(self.graph, self.gproject.node) + bhid)
        if bnode is None:
            bnode = rdflib.URIRef(self.basens + hf.getNodeID(self.graph, self.gproject.node) + bhid)
            hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E12_Production'))
            hf.addProperty(self.graph, self.gproject.node, bnode, rdflib.URIRef(self.nss['crm'] + 'P9_consists_of'))
            hf.addLabel(self.graph, bnode, 'Verzamelde objecten behorende bij {}'.format(hf.getLabel(self.graph, self.gproject.node)), 'nl')

        name = ''
        nnode = tnode.find(self.sikbns + 'naam')
        if nnode is not None:
            name = nnode.text
        hid = hf.genHash(tnode, self.sikbns, ['bewaarTemperatuur', 'bewaarVochtigheid', 'lichtgevoelig',\
                                             'breekbaar', 'gevaarlijkeStoffen'], salt=name)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))

        hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P108_has_produced'))
        hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P108i_was_produced_by'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'bewaarTemperatuur':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'bewaarVochtigheid':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'lichtgevoelig':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'breekbaar':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'gevaarlijkeStoffen':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
        return self.ReturnValues(node=gnode, altnode=None)

    def verpakkingseenheidHandler(self, tnode):
        hid = hf.genHash(tnode, self.sikbns, ['aantal', 'gewicht', 'beginperiode', 'eindperiode', {'doosId': ['naam']}])
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0010_BulkFind'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'aantal':
                if child.text is None:
                    continue
                bhid = hf.genHash(tnode, self.sikbns, [childname], salt=childname)
                bnode = rdflib.URIRef(self.basens + bhid)
                inode = rdflib.Literal(bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname)
                hf.addLabel(self.graph, bnode,\
                            'Hoeveelheid van {} stuks'.format(hf.rawString(child.text)), 'nl')

                uomnode = rdflib.Literal('number of units', datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))
                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if childname == 'gewicht':
                if child.text is None:
                    continue
                uomvalue = child.attrib['uom'] if 'uom' in child.attrib else 'eenheden'

                bhid = hf.genHash(tnode, self.sikbns, [childname], salt='E54_Dimension' + uomvalue)
                bnode = rdflib.URIRef(self.basens + bhid)
                inode = rdflib.Literal(bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname)
                hf.addLabel(self.graph, bnode,\
                            'Gewicht van {} {}'.format(hf.rawString(child.text), uomvalue), 'nl')

                uomnode = rdflib.Literal(uomvalue, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if childname == 'beginperiode':
                if child.text is None:
                    continue
                bhid = hf.genHash(None, None, [], salt=hid + 'EHE2021_BulkFindAssessment')
                bnode = rdflib.URIRef(self.basens + hid + bhid)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'EHE2021_BulkFindAssessment'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P140_assigned_attribute_to'))
                hf.addLabel(self.graph, bnode,\
                            'Datering van {} behorende bij {}'.format(hf.getLabel(self.graph, gnode),\
                                                                      hf.getLabel(self.graph, self.gproject.node)), 'nl')

                bhid2 = hf.genHash(tnode, self.sikbns, ['beginperiode', 'eindperiode'], 'E52_Time-Span')
                bnode2 = hf.getNode(self.graph, bhid2)
                if bnode2 is not None:
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))
                    continue

                bnode2 = rdflib.URIRef(self.basens + bhid2)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crmeh'] + 'E52_Time-Span'))
                inode = rdflib.Literal(bhid2, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))

                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode2, childname)
                hf.addRefIfExists(self, cnode, child)

                enddate = "?"
                dnode = None
                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode2, childname)
                    hf.addRefIfExists(self, dnode, snode)

                    enddate = hf.getLabel(self.vocab, dnode) if (dnode is not None and self.vocab is not None)\
                                    else key + ' ' + hf.rawString(snode.text)

                startdate = hf.getLabel(self.vocab, cnode) if (cnode is not None and self.vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                hf.addLabel(self.graph, bnode2, 'Tijdspanne (van {} tot {})'.format(startdate, enddate), 'nl')
            if childname == 'doosId':
                if child.text is None:
                    continue
                enode = self.doosHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))

        return self.ReturnValues(node=gnode, altnode=None)

    def monsterHandler(self, tnode):
        venodes = []
        for atnode in tnode.findall(self.sikbns + 'verpakkingseenheidId'):
            atnode = hf.getTreeNodeByID(self.troot, self.sikbns, atnode.text)
            venodes.append(self.verpakkingseenheidHandler(atnode).node)
        vcnodes = []
        for atnode in tnode.findall(self.sikbns + 'vondstcontextId'):
            atnode = hf.getTreeNodeByID(self.troot, self.sikbns, atnode.text)
            vcnodes.append(self.vondstcontextHandler(atnode).node)

        nodeIDs = ''
        for node in itertools.chain(venodes, vcnodes):
            nodeIDs += hf.getNodeID(self.graph, node)

        hid = hf.genHash(tnode, self.sikbns, ['monstertype', 'monsterverwerking', 'beginperiode', 'eindperiode'], salt=nodeIDs)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0018_ContextSample'))

        for enode in venodes:
            hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
            hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))
        for enode in vcnodes:
            hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P53i_is_former_or_current_location_of'))
            hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P53_has_former_or_current_location'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'monstertype':
                if child.text is None:
                    continue
                key = 'monstertype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'monsterverwerking':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'beginperiode':
                if child.text is None:
                    continue
                bhid = hf.genHash(None, None, [], salt=hid + 'E13_Attribute_Assignment')
                bnode = rdflib.URIRef(self.basens + hid + bhid)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P140_assigned_attribute_to'))
                hf.addLabel(self.graph, bnode,\
                            'Datering van {} behorende bij {}'.format(hf.getLabel(self.graph, gnode),\
                                                                      hf.getLabel(self.graph, self.gproject.node)), 'nl')

                bhid2 = hf.genHash(tnode, self.sikbns, ['beginperiode', 'eindperiode'], 'E52_Time-Span')
                bnode2 = hf.getNode(self.graph, bhid2)
                if bnode2 is not None:
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))
                    continue

                bnode2 = rdflib.URIRef(self.basens + bhid2)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crmeh'] + 'E52_Time-Span'))
                inode = rdflib.Literal(bhid2, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))

                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode, childname)
                hf.addRefIfExists(self, cnode, child)

                enddate = "?"
                dnode = None
                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode, childname)
                    hf.addRefIfExists(self, dnode, snode)
                
                    enddate = hf.getLabel(self.vocab, dnode) if (dnode is not None and self.vocab is not None)\
                                    else key + ' ' + hf.rawString(snode.text)

                startdate = hf.getLabel(self.vocab, cnode) if (cnode is not None and self.vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                hf.addLabel(self.graph, bnode2, 'Tijdspanne (van {} tot {})'.format(startdate, enddate), 'nl')
            if childname == 'verpakkingseenheidId':
                continue
            if childname == 'vondstcontextId':
                continue

        return self.ReturnValues(node=gnode, altnode=None)

    def vondstHandler(self, tnode):
        hid = hf.genHash(tnode, self.sikbns, ['aantal', 'gewicht', 'materiaalcategorie', 'artefacttype',\
                                              'beginperiode', 'eindperiode', {'verpakkingseenheidId': ['naam']}])
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'aantal':
                if child.text is None:
                    continue
                bhid = hf.genHash(tnode, self.sikbns, [childname], salt=childname)
                bnode = rdflib.URIRef(self.basens + bhid)
                inode = rdflib.Literal(bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname)
                hf.addLabel(self.graph, bnode,\
                            'Hoeveelheid van {} stuks'.format(hf.rawString(child.text)), 'nl')

                uomnode = rdflib.Literal('number of units', datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))
                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'positiveInteger'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if childname == 'gewicht':
                if child.text is None:
                    continue
                uomvalue = child.attrib['uom'] if 'uom' in child.attrib else 'eenheden'

                bhid = hf.genHash(tnode, self.sikbns, [childname], salt='E54_Dimension' + uomvalue)
                bnode = rdflib.URIRef(self.basens + bhid)
                inode = rdflib.Literal(bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname)
                hf.addLabel(self.graph, bnode,\
                            'Gewicht van {} {}'.format(hf.rawString(child.text), uomvalue), 'nl')

                uomnode = rdflib.Literal(uomvalue, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, bnode, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))
            if childname == 'materiaalcategorie':
                if child.text is None:
                    continue
                key = 'materiaalcategorie'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'artefacttype':
                if child.text is None:
                    continue
                key = 'artefacttype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'beginperiode':
                if child.text is None:
                    continue
                bhid = hf.genHash(None, None, [], salt=hid + 'E13_Attribute_Assignment')
                bnode = rdflib.URIRef(self.basens + hid + bhid)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P140_assigned_attribute_to'))
                hf.addLabel(self.graph, bnode,\
                            'Datering van {} behorende bij {}'.format(hf.getLabel(self.graph, gnode),\
                                                                      hf.getLabel(self.graph, self.gproject.node)), 'nl')

                bhid2 = hf.genHash(tnode, self.sikbns, ['beginperiode', 'eindperiode'], 'E52_Time-Span')
                bnode2 = hf.getNode(self.graph, bhid2)
                if bnode2 is not None:
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))
                    continue

                bnode2 = rdflib.URIRef(self.basens + bhid2)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crmeh'] + 'E52_Time-Span'))
                inode = rdflib.Literal(bhid2, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))

                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode2, childname)
                hf.addRefIfExists(self, cnode, child)

                enddate = "?"
                dnode = None
                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode2, childname)
                    hf.addRefIfExists(self, dnode, snode)
                    
                    enddate = hf.getLabel(self.vocab, dnode) if (dnode is not None and self.vocab is not None)\
                                    else key + ' ' + hf.rawString(snode.text)

                startdate = hf.getLabel(self.vocab, cnode) if (cnode is not None and self.vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                hf.addLabel(self.graph, bnode2, 'Tijdspanne (van {} tot {})'.format(startdate, enddate), 'nl')
            if childname == 'geconserveerd':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'exposabel':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'gedeselecteerd':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'boolean'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'verpakkingseenheidId':
                if child.text is None:
                    continue
                enode = self.verpakkingseenheidHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))
            if childname == 'veldvondstId':
                if child.text is None:
                    continue
                enode = self.veldvondstHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P46_is_composed_of'))
                hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P46i_forms_part_of'))

        return self.ReturnValues(node=gnode, altnode=None)

    def veldvondstHandler(self, tnode):
        vnode = None
        vtnode = tnode.find(self.sikbns + 'vondstcontextId')
        if vtnode is not None:
            vtnode = hf.getTreeNodeByID(self.troot, self.sikbns, vtnode.text)
            vnode = self.vondstcontextHandler(vtnode).node

        vnodeID = ''
        if vnode is not None:
            vnodeID = hf.getNodeID(self.graph, vnode)

        hid = hf.genHash(tnode, self.sikbns, ['verzamelwijze'], salt=vnodeID + 'E78_Collection')
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'verzamelwijze':
                if child.text is None:
                    continue
                key = 'verzamelwijze'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'vondstcontextId' and vnode is not None:
                hf.addProperty(self.graph, gnode, vnode, rdflib.URIRef(self.nss['crm'] + 'P53_has_former_or_current_location'))
                hf.addProperty(self.graph, vnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P53_is_former_or_current_location_of'))

        return self.ReturnValues(node=gnode, altnode=None)

    def vondstcontextHandler(self, tnode):
        contexts = []
        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'spoorId':
                if child.text is None:
                    continue
                enode = self.spoorHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                contexts.append((enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'),\
                                rdflib.URIRef(self.nss['crm'] + 'P89_falls_within')))
            if childname == 'stortId':
                if child.text is None:
                    continue
                enode = self.stortHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                contexts.append((enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'),\
                                rdflib.URIRef(self.nss['crmeh'] + 'EHP3')))
            if childname == 'planumId':
                if child.text is None:
                    continue
                enode = self.planumHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                contexts.append((enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'),\
                                rdflib.URIRef(self.nss['crm'] + 'P89_falls_within')))
            if childname == 'vullingId':
                if child.text is None:
                    continue
                enode = self.vullingHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                contexts.append((enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'),\
                                rdflib.URIRef(self.nss['crmeh'] + 'EHP3')))
            if childname == 'segmentId':
                if child.text is None:
                    continue
                enode = self.segmentHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                contexts.append((enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'),\
                                rdflib.URIRef(self.nss['crm'] + 'P89_falls_within')))
            if childname == 'vakId':
                if child.text is None:
                    continue
                enode = self.vakHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                contexts.append((enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'),\
                                rdflib.URIRef(self.nss['crm'] + 'P89_falls_within')))
            if childname == 'boringId':
                if child.text is None:
                    continue
                enode = self.boringHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                contexts.append((enode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'),\
                                rdflib.URIRef(self.nss['crm'] + 'P89_falls_within')))
            if childname == 'geolocatieId':
                if child.text is None:
                    continue
                enode = self.geolocatieHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node

                contexts.append((enode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'),\
                                rdflib.URIRef(self.nss['crm'] + 'P87i_identifies')))


        contextIDs = ''
        for context, _, _ in contexts:
            if context is not None:
                contextIDs += hf.getNodeID(self.graph, context)

        hid = hf.genHash(tnode, self.sikbns, ['contexttype'], salt=contextIDs)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisLocatieTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))
        hf.updateLabel(self.graph, gnode, "({})".format(hf.getTID(self.graph, gnode)),'nl')

        for context, fp, bp in contexts:
            if context is not None:
                hf.addProperty(self.graph, gnode, context, fp)
                hf.addProperty(self.graph, context, gnode, bp)


        child = tnode.find(self.sikbns + 'contexttype')
        if child is not None:
            key = 'contexttype'  # needed for inconsistent labeling by SIKB
            cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
            hf.addSchemaType(self.graph, self.ontns, cnode, gnode, 'contexttype')
            hf.addRefIfExists(self, cnode, child)

        return self.ReturnValues(node=gnode, altnode=None)

    def boringHandler(self, tnode):
        name = tnode.attrib['naam'] if 'naam' in tnode.attrib else ''

        geonode = None
        geotnode = tnode.find(self.sikbns + 'geolocatieId')
        if geotnode is not None:
            geonode = self.geolocatieHandler(hf.getTreeNodeByID(self.troot, self.sikbns, geotnode.text)).node

        hid = hf.genHash(tnode, self.sikbns, [], salt=name + 'EHE0007_Context' + hf.getNodeID(self.graph, geonode))
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode, self.sikbns, self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        if geonode is not None:
            hf.addProperty(self.graph, gnode, geonode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
            hf.addProperty(self.graph, geonode, gnode, rdflib.URIRef(self.nss['crm'] + 'P87i_identifies'))

        return self.ReturnValues(node=gnode, altnode=None)

    def vullingHandler(self, tnode):
        snode = None
        stnode = tnode.find(self.sikbns + 'spoorId')
        if stnode is not None:
            stnode = hf.getTreeNodeByID(self.troot, self.sikbns, stnode.text)
            snode = self.spoorHandler(stnode).node

        snodeID = ''
        if snode is not None:
            snodeID = hf.getNodeID(self.graph, snode)

        hid = hf.genHash(tnode, self.sikbns, ['vorm', 'kleur', 'textuur'], salt=snodeID)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'vorm':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'kleur':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'textuur':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'spoorId':
                if child.text is None:
                    continue
                hf.addProperty(self.graph, gnode, snode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3'))
                hf.addProperty(self.graph, snode, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))

        return self.ReturnValues(node=gnode, altnode=None)

    def structuurHandler(self, tnode):
        snodes = []
        for stnode in tnode.findall(self.sikbns + 'spoorId'):
            stnode = hf.getTreeNodeByID(self.troot, self.sikbns, stnode.text)
            snodes.append(self.spoorHandler(stnode).node)

        snodeIDs = ''
        for snode in snodes:
            snodeIDs += hf.getNodeID(self.graph, snode)

        hid = hf.genHash(tnode, self.sikbns, ['structuurtype', 'beginperiode', 'eindperiode'], salt=snodeIDs)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'structuurtype':
                if child.text is None:
                    continue
                key = 'structuurtype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'beginperiode':
                if child.text is None:
                    continue
                bhid = hf.genHash(None, None, [], salt=hid + 'E13_Attribute_Assignment')
                bnode = rdflib.URIRef(self.basens + hid + bhid)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P140_assigned_attribute_to'))
                hf.addLabel(self.graph, bnode,\
                            'Datering van {} behorende bij {}'.format(hf.getLabel(self.graph, gnode),\
                                                                      hf.getLabel(self.graph, self.gproject.node)), 'nl')

                bhid2 = hf.genHash(tnode, self.sikbns, ['beginperiode', 'eindperiode'], 'E52_Time-Span')
                bnode2 = hf.getNode(self.graph, bhid2)
                if bnode2 is not None:
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))
                    continue

                bnode2 = rdflib.URIRef(self.basens + bhid2)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crmeh'] + 'E52_Time-Span'))
                inode = rdflib.Literal(bhid2, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))


                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode2, childname)
                hf.addRefIfExists(self, cnode, child)

                enddate = "?"
                dnode = None
                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode2, childname)
                    hf.addRefIfExists(self, dnode, snode)
                
                    enddate = hf.getLabel(self.vocab, dnode) if (dnode is not None and self.vocab is not None)\
                                    else key + ' ' + hf.rawString(snode.text)

                startdate = hf.getLabel(self.vocab, cnode) if (cnode is not None and self.vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                hf.addLabel(self.graph, bnode2, 'Tijdspanne (van {} tot {})'.format(startdate, enddate), 'nl')
            if childname == 'spoorId':
                continue

        for enode in snodes:
            hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crm'] + 'P53_has_former_or_current_location'))
            hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crm'] + 'P53i_is_former_or_current_location_of'))

        return self.ReturnValues(node=gnode, altnode=None)

    def segmentHandler(self, tnode):
        snode = None
        stnode = tnode.find(self.sikbns + 'spoorId')
        if stnode is not None:
            stnode = hf.getTreeNodeByID(self.troot, self.sikbns, stnode.text)
            snode = self.spoorHandler(stnode).node

        snodeID = ''
        if snode is not None:
            snodeID = hf.getNodeID(self.graph, snode)

        hid = hf.genHash(tnode, self.sikbns, ['planumtype'], salt=snodeID)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode, self.sikbns, self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'spoorId':
                if child.text is None:
                    continue
                hf.addProperty(self.graph, gnode, snode, rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
                hf.addProperty(self.graph, snode, gnode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))
            if childname == 'geolocatieId':
                if child.text is None:
                    continue
                geonode = self.geolocatieHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node
                if geonode is not None:
                    hf.addProperty(self.graph, gnode, geonode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
                    hf.addProperty(self.graph, geonode, gnode, rdflib.URIRef(self.nss['crm'] + 'P87i_identifies'))

        return self.ReturnValues(node=gnode, altnode=None)

    def stortHandler(self, tnode):
        nodes = []
        for atnode in tnode.findall(self.sikbns + 'spoorId'):
            atnode = hf.getTreeNodeByID(self.troot, self.sikbns, atnode.text)
            nodes.append(self.spoorHandler(atnode).node)
        for atnode in tnode.findall(self.sikbns + 'putId'):
            atnode = hf.getTreeNodeByID(self.troot, self.sikbns, atnode.text)
            nodes.append(self.putHandler(atnode).node)

        nodeIDs = ''
        for node in nodes:
            nodeIDs += hf.getNodeID(self.graph, node)

        hid = hf.genHash(tnode, self.sikbns, [], salt=nodeIDs + 'EHE0008_ContextStuff')
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        for enode in nodes:
            hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3'))
            hf.addProperty(self.graph, enode, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHP3i'))

        return self.ReturnValues(node=gnode, altnode=None)

    def planumHandler(self, tnode):
        ptnode = None
        pttnode = tnode.find(self.sikbns + 'putId')
        if pttnode is not None:
            pttnode = hf.getTreeNodeByID(self.troot, self.sikbns, pttnode.text)
            ptnode = self.putHandler(pttnode).node

        ptnodeID = ''
        if ptnode is not None:
            ptnodeID = hf.getNodeID(self.graph, ptnode)

        hid = hf.genHash(tnode, self.sikbns, ['planumtype'], salt=ptnodeID)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode, self.sikbns, self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'planumtype':
                if child.text is None:
                    continue
                key = 'planumtype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'geolocatieId':
                if child.text is None:
                    continue
                geonode = self.geolocatieHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node
                if geonode is not None:
                    hf.addProperty(self.graph, gnode, geonode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
                    hf.addProperty(self.graph, geonode, gnode, rdflib.URIRef(self.nss['crm'] + 'P87i_identifies'))
            if childname == 'putId':
                continue
        hf.addProperty(self.graph, gnode, ptnode, rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
        hf.addProperty(self.graph, ptnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))

        return self.ReturnValues(node=gnode, altnode=None)

    def spoorHandler(self, tnode):
        geonode = None
        geotnode = tnode.find(self.sikbns + 'geolocatieId')
        if geotnode is not None:
            geonode = self.geolocatieHandler(hf.getTreeNodeByID(self.troot, self.sikbns, geotnode.text)).node

        name = tnode.find(self.sikbns + 'naam')
        name = name.text if name is not None else ''

        hid = hf.genHash(tnode, self.sikbns, ['grondspoortype', 'diepte', 'beginperiode', 'eindperiode'],\
                         salt=name + hf.getNodeID(self.graph, geonode))
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        if geonode is not None:
            hf.addProperty(self.graph, gnode, geonode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
            hf.addProperty(self.graph, geonode, gnode, rdflib.URIRef(self.nss['crm'] + 'P87i_identifies'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'grondspoortype':
                if child.text is None:
                    continue
                key = 'grondspoortype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'diepte':
                if child.text is None:
                    continue
                bhid = hf.genHash(None, None, [], salt=hid + childname)
                bnode = rdflib.URIRef(self.basens + hid + bhid)
                inode = rdflib.Literal(hid + bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname)
                hf.addLabel(self.graph, bnode,\
                            'Meting van diepte behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

                uom = child.attrib['uom'] if 'uom' in child.attrib else ''
                bhid2 = hf.genHash(tnode, self.sikbns, [childname], salt='E54_Dimension' + uom)
                bnode2 = hf.getNode(self.graph, bhid2)
                if bnode2 is not None:
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))
                    continue

                bnode2 = rdflib.URIRef(self.basens + bhid2)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.ontns + 'SIKB0102S_Diepte'))
                inode = rdflib.Literal(bhid2, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode2, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

                uom = uomnode.value if uomnode is not None else 'eenheden'
                hf.addLabel(self.graph, bnode2, 'Diepte van {} {}'.format(inode.value, uom), 'nl')
            if childname == 'beginperiode':
                if child.text is None:
                    continue
                bhid = hf.genHash(None, None, [], salt=hid + 'E13_Attribute_Assignment')
                bnode = rdflib.URIRef(self.basens + hid + bhid)
                hf.addType(self.graph, bnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))
                hf.addProperty(self.graph, gnode, bnode, rdflib.URIRef(self.nss['crm'] + 'P140i_was_attributed_by'))
                hf.addProperty(self.graph, bnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P140_assigned_attribute_to'))
                hf.addLabel(self.graph, bnode,\
                            'Datering van {} behorende bij {}'.format(hf.getLabel(self.graph, gnode),\
                                                                      hf.getLabel(self.graph, self.gproject.node)), 'nl')

                bhid2 = hf.genHash(tnode, self.sikbns, ['beginperiode', 'eindperiode'], 'E52_Time-Span')
                bnode2 = hf.getNode(self.graph, bhid2)
                if bnode2 is not None:
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))
                    continue

                bnode2 = rdflib.URIRef(self.basens + bhid2)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crmeh'] + 'E52_Time-Span'))
                inode = rdflib.Literal(bhid2, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P141_assigned'))

                key = 'periode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, bnode2, childname)
                hf.addRefIfExists(self, cnode, child)

                enddate = "?"
                dnode = None
                snode = tnode.find(self.sikbns + 'eindperiode')
                if snode is not None:
                    childname = re.sub(self.sikbns, '', snode.tag)
                    key = 'periode'  # needed for inconsistent labeling by SIKB
                    dnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(snode.text))
                    hf.addSchemaType(self.graph, self.ontns, dnode, bnode2, childname)
                    hf.addRefIfExists(self, dnode, snode)
                
                    enddate = hf.getLabel(self.vocab, dnode) if (dnode is not None and self.vocab is not None)\
                                    else key + ' ' + hf.rawString(snode.text)

                startdate = hf.getLabel(self.vocab, cnode) if (cnode is not None and self.vocab is not None)\
                                else key + ' ' + hf.rawString(child.text)
                hf.addLabel(self.graph, bnode2, 'Tijdspanne (van {} tot {})'.format(startdate, enddate), 'nl')

        return self.ReturnValues(node=gnode, altnode=None)

    def putHandler(self, tnode):
        geonode = None
        geotnode = tnode.find(self.sikbns + 'geolocatieId')
        if geotnode is not None:
            geonode = self.geolocatieHandler(hf.getTreeNodeByID(self.troot, self.sikbns, geotnode.text)).node

        name = tnode.attrib['naam'] if 'naam' in tnode.attrib else ''

        hid = hf.genHash(tnode, self.sikbns, [], salt=name + 'EHE0007_Context' + hf.getNodeID(self.graph, geonode))
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode, self.sikbns, self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        if geonode is not None:
            hf.addProperty(self.graph, gnode, geonode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
            hf.addProperty(self.graph, geonode, gnode, rdflib.URIRef(self.nss['crm'] + 'P87i_identifies'))

        return self.ReturnValues(node=gnode, altnode=None)


    def vakHandler(self, tnode):
        plnode = None
        pltnode = tnode.find(self.sikbns + 'planumId')
        if pltnode is not None:
            pltnode = hf.getTreeNodeByID(self.troot, self.sikbns, pltnode.text)
            plnode = self.planumHandler(pltnode).node

        plnodeID = ''
        if plnode is not None:
            plnodeID = hf.getNodeID(self.graph, plnode)

        hid = hf.genHash(tnode, self.sikbns, ['vaknummer', 'dikte'], salt=plnodeID)
        hid = hf.getNodeID(self.graph, self.gproject.node) + hid
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode, self.sikbns, self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'vaknummer':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + \
                                                                                        'positiveInteger'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'dikte':
                if child.text is None:
                    continue
                bhid = hf.genHash(None, None, [], salt=hid + childname)
                bnode = rdflib.URIRef(self.basens + hid + bhid)
                inode = rdflib.Literal(hid + bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname)
                hf.addLabel(self.graph, bnode,\
                            'Meting van dikte behorende bij {}'.format(hf.getLabel(self.graph, gnode)), 'nl')

                uom = child.attrib['uom'] if 'uom' in child.attrib else 'eenheden'
                bhid2 = hf.genHash(tnode, self.sikbns, [childname], 'E54_Dimension' + uom)
                bnode2 = hf.getNode(self.graph, bhid2)
                if bnode2 is not None:
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))
                    continue

                bnode2 = rdflib.URIRef(self.basens + bhid2)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                inode = rdflib.Literal(bhid2, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))

                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))

                uomnode = rdflib.Literal(uom, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, bnode2, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

                uom = uomnode.value if uomnode is not None else 'eenheden'
                hf.addLabel(self.graph, bnode2, 'Dikte van {} {}'.format(inode.value, uom), 'nl')
            if childname == 'nap':
                if child.text is None:
                    continue
                bhid = hf.genHash(None, None, [], salt=hid + childname)
                bnode = rdflib.URIRef(self.basens + hid + bhid)
                inode = rdflib.Literal(hid + bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname)
                hf.addLabel(self.graph, bnode,\
                            'Meting van Normaal Amsterdams Peil (NAP) behorende bij {}'.format(\
                                                                                        hf.getLabel(self.graph, gnode)),\
                                                                                        'nl')

                uom = child.attrib['uom'] if 'uom' in child.attrib else ''
                bhid2 = hf.genHash(tnode, self.sikbns, [childname], 'E54_Dimension' + uom)
                bnode2 = hf.getNode(self.graph, bhid2)
                if bnode2 is not None:
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))
                    continue

                bnode2 = rdflib.URIRef(self.basens + bhid2)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                inode = rdflib.Literal(bhid2, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))

                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))

                uomnode = rdflib.Literal(uom, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, bnode2, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

                uom = uomnode.value if uomnode is not None else 'eenheden'
                hf.addLabel(self.graph, bnode2, '{} {} Normaal Amsterdams Peil (NAP)'.format(inode.value, uom), 'nl')
            if childname == 'planumId':
                continue
            if childname == 'geolocatieId':
                if child.text is None:
                    continue
                geonode = self.geolocatieHandler(hf.getTreeNodeByID(self.troot, self.sikbns, child.text)).node
                if geonode is not None:
                    hf.addProperty(self.graph, gnode, geonode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
                    hf.addProperty(self.graph, geonode, gnode, rdflib.URIRef(self.nss['crm'] + 'P87i_identifies'))

        hf.addProperty(self.graph, gnode, plnode, rdflib.URIRef(self.nss['crm'] + 'P89_falls_within'))
        hf.addProperty(self.graph, plnode, gnode, rdflib.URIRef(self.nss['crm'] + 'P89i_contains'))

        return self.ReturnValues(node=gnode, altnode=None)

    def persoonHandler(self, tnode, gpnode=None):
        hid = hf.genHash(tnode, self.sikbns, ['email', 'telefoon',\
                                              {'naam':['achternaam', 'voornaam', 'initialen', 'titel']}])
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gproject = gpnode if gpnode is not None else self.gproject.node

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisTypeFields(self.graph, gnode, tnode, self.sikbns, nolabel=True, gpnode=gproject)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.ontns + 'SIKB0102S_Persoon'))

        voornaam = ''
        achternaam = ''
        initialen = ''
        titel = ''
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'telefoon':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'email':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'naam':
                if child.text is None:
                    continue
                for element in child:
                    childname = re.sub(self.sikbns, '', element.tag)
                    if childname == 'achternaam':
                        if element.text is None:
                            continue
                        snode = child.find(self.sikbns + 'tussenvoegsel')
                        if snode is not None and snode.text is not None:
                            achternaam = element.text + ', ' + snode.text
                        else:
                            achternaam = element.text  # extract 'tussenvoegsel' if available

                        enode = rdflib.Literal(achternaam, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                               childname))
                    if childname == 'voornaam':
                        if element.text is None:
                            continue
                        snode = child.find(self.sikbns + 'initialen')
                        if snode is not None and snode.text is not None:
                            voornaam = element.text + ', ' + snode.text  # extract 'initialen' if available
                        else:
                            voornaam = element.text

                        enode = rdflib.Literal(voornaam, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                               childname))
                    if childname == 'initialen':
                        if element.text is None:
                            continue
                        snode = child.find(self.sikbns + 'voornaam')
                        if snode is None or snode.text is None:
                            initialen = hf.rawString(element.text)
                            enode = rdflib.Literal(initialen, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                            hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                                   childname))
                    if childname == 'titel':
                        if element.text is None:
                            continue
                        titel = hf.rawString(element.text)
                        enode = rdflib.Literal(titel, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, gnode, enode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                               childname))
                name = voornaam if initialen == '' else initialen
                titel = titel if titel == '' else titel + ' '
            hf.addLabel(self.graph, gnode,\
                        '{}{}, {}'.format(titel, achternaam, name), 'nl')

        return self.ReturnValues(node=gnode, altnode=None)

    def geolocatieHandler(self, tnode):
        hid = hf.genHash(tnode, self.sikbns, ['geometrie'])
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            geonode = self.graph.value(gnode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'), None)
            return self.ReturnValues(node=gnode, altnode=geonode)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractGeoObjectFields(self.graph, gnode, tnode, self.sikbns)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

        
        cnode = None
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'geometrie':
                if child.text is None:
                    continue
                (gmlString, gmlID, gmlType) = hf.gmlLiteralOf(self.et, child)

                bhid = hf.genHash(tnode, self.sikbns, ['geometrie'], salt=gmlType)
                cnode = rdflib.URIRef(self.basens + hid + bhid)
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)

                gmlnode = rdflib.Literal(gmlString, datatype=rdflib.URIRef(self.nss['geosparql'] + 'GMLLiteral'))
                hf.addProperty(self.graph, cnode, gmlnode, rdflib.URIRef(self.nss['geosparql'] + 'asGML'))

                idNode = rdflib.Literal(gmlID, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, cnode, idNode, rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by'))
                hf.addLabel(self.graph, cnode, 'Geometrie [{}]'.format(gmlType), 'nl')

        return self.ReturnValues(node=gnode, altnode=cnode)

    def hoogtemetingHandler(self, tnode):
        node = None
        ttnode = tnode.find(self.sikbns + 'geolocatieId')
        if ttnode is not None:
            ttnode = hf.getTreeNodeByID(self.troot, self.sikbns, ttnode.text)
            node = self.geolocatieHandler(ttnode).node

        nodeID = ''
        if node is not None:
            nodeID = hf.getNodeID(self.graph, node)

        hid = hf.genHash(tnode, self.sikbns, ['hoogtemetingmethode', 'nap'], salt=nodeID)
        gnode = hf.getNode(self.graph, hf.getNodeID(self.graph, self.gproject.node) + hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hf.getNodeID(self.graph, self.gproject.node) + hid)
        hf.extractBasisLocatieNaamTypeFields(self.graph, gnode, tnode, self.sikbns, self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))

        
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'methode':
                if child.text is None:
                    continue
                key = 'hoogtemetingmethode'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addSchemaType(self.graph, self.ontns, cnode, gnode, childname)
                hf.addRefIfExists(self, cnode, child)
            if childname == 'nap':
                if child.text is None:
                    continue
                bhid = hf.genHash(None, None, [], salt=hid + childname)
                bnode = rdflib.URIRef(self.basens + hid + bhid)
                inode = rdflib.Literal(hid + bhid, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))
                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname)
                hf.addLabel(self.graph, bnode,\
                            'Meting van Normaal Amsterdams Peil (NAP) behorende bij {}'.format(\
                                                                                        hf.getLabel(self.graph, gnode)),\
                                                                                        'nl')

                uom = child.attrib['uom'] if 'uom' in child.attrib else ''
                bhid2 = hf.genHash(tnode, self.sikbns, [childname], 'E54_Dimension' + uom)
                bnode2 = hf.getNode(self.graph, bhid2)
                if bnode2 is not None:
                    hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))
                    continue

                bnode2 = rdflib.URIRef(self.basens + bhid)
                hf.addType(self.graph, bnode2, rdflib.URIRef(self.nss['crm'] + 'E54_Dimension'))
                inode = rdflib.Literal(bhid2, datatype=rdflib.URIRef(self.nss['xsd'] + 'ID'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier'))

                hf.addProperty(self.graph, bnode, bnode2, rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension'))

                for k, v in child.attrib.items():
                    if k == 'uom':
                        uomnode = rdflib.Literal(v, datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                        hf.addProperty(self.graph, bnode2, uomnode, rdflib.URIRef(self.nss['crm'] + 'P91_has_unit'))

                inode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'decimal'))
                hf.addProperty(self.graph, bnode2, inode, rdflib.URIRef(self.nss['crm'] + 'P90_has_value'))

                uom = uomnode.value if uomnode is not None else 'eenheden'
                hf.addLabel(self.graph, bnode2, '{} {} Normaal Amsterdams Peil (NAP)'.format(inode.value, uom), 'nl')
            if childname == 'geolocatieId':
                if child.text is None:
                    continue
                hf.addProperty(self.graph, gnode, node, rdflib.URIRef(self.nss['crm'] + 'P7_took_place_at'))
                hf.addProperty(self.graph, node, gnode, rdflib.URIRef(self.nss['crm'] + 'P7i_witnessed'))

        return self.ReturnValues(node=gnode, altnode=None)

    def attribuuttypeHandler(self, tnode):
        hid = hf.genHash(tnode, self.sikbns, ['attribuutnaam', 'klassenaam', 'waardetype'], pre='P')
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['owl'] + 'DataProperty'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'attribuutnaam':
                if child.text is None:
                    continue
                hf.updateLabel(self.graph, gnode, "(gebruiker-gedefinieerd) '{}'".format(hf.rawString(child.text)),'nl')
            if childname == 'informatie':
                continue  # base type extractor covers this as well
                #info = rdflib.Literal(hf.rawString(child.text), lang='nl')
                #hf.addProperty(self.graph, gnode, info, rdflib.URIRef(self.nss['rdfs'] + 'comment'))
            if childname == 'klassenaam':
                if child.text is None:
                    continue
                cnode = rdflib.URIRef(self.ontns + 'SIKB0102S_' + hf.rawString(child.text).rstrip('Type'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.nss['rdfs'] + 'domain'))
            if childname == 'waardetype':
                if child.text is None:
                    continue
                key = 'waardetype'  # needed for inconsistent labeling by SIKB
                cnode = rdflib.URIRef(self.vocns + 'SIKB_Code_' + key.title() + '_' + hf.rawString(child.text))
                hf.addType(self.graph, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + childname.title() \
                                                         + '.' + hf.rawString(child.text.title())))
                hf.addProperty(self.graph, gnode, cnode, \
                               rdflib.URIRef(self.ontns + 'SIKB0102S_' + 'attribuuttype' + '_' + childname))

                if hf.rawString(child.text) == 'Geheelgetal':
                    datatype = rdflib.URIRef(self.nss['xsd'] + 'integer')
                if hf.rawString(child.text) == 'Decimaalgetal':
                    datatype = rdflib.URIRef(self.nss['xsd'] + 'decimal')
                if hf.rawString(child.text) == 'Referentie':
                    datatype = rdflib.URIRef(self.nss['xsd'] + 'ID')
                if hf.rawString(child.text) == 'Text':
                    datatype = rdflib.URIRef(self.nss['xsd'] + 'string')
                if hf.rawString(child.text) == 'JaNee':
                    datatype = rdflib.URIRef(self.nss['xsd'] + 'boolean')

                hf.addProperty(self.graph, gnode, datatype, rdflib.URIRef(self.nss['rdfs'] + 'range'))

        return self.ReturnValues(node=gnode, altnode=None)

    def attribuutHandler(self, tnode):
        objectID = tnode.find(self.sikbns + 'objectId')
        oidTnode = hf.getTreeNodeByID(self.troot, self.sikbns, objectID.text)
        function = getattr(self, re.sub(self.sikbns, '', oidTnode.tag) + 'Handler')
        oidnode = function(oidTnode).node

        if oidnode is None:
            return

        attrID = tnode.find(self.sikbns + 'attribuuttypeId')
        attrTnode = hf.getTreeNodeByID(self.troot, self.sikbns, attrID.text)
        function = getattr(self, re.sub(self.sikbns, '', attrTnode.tag) + 'Handler')
        attrnode = function(attrTnode).node

        if attrnode is None:
            return
        attrType = self.graph.value(subject=attrnode,\
                                    predicate=rdflib.URIRef(self.nss['rdfs'] + 'range'),\
                                    object=None)

        value = None
        for child in list(tnode):
            childname = re.sub(self.sikbns, '', child.tag)
            if childname in ['geheelgetal', 'decimaalgetal', 'referentieId', 'text', 'jaNee']:
                value = hf.rawString(child.text)

        if value is None:
            return

        vnode = rdflib.Literal(value, datatype=attrType)
        hf.addProperty(self.graph, oidnode, vnode, attrnode)


    def objectrelatieHandler(self, tnode):
        hid = hf.genHash(tnode, self.sikbns, ['objectrelatietype', 'object1Class', 'object2Class'], pre='P')
        gnode = hf.getNode(self.graph, hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + hid)
        hf.extractBasisTypeFields(self.graph, gnode, tnode, self.sikbns, gpnode=self.gproject.node)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['owl'] + 'ObjectProperty'))

        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'objectrelatietype':
                if child.text is None:
                    continue
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
                               "specificeert relatie '{}' tussen object '{}' (lhs) en object '{}' (rhs)".format(relation,\
                                                                                                           object1Class,\
                                                                                                           object2Class), 'nl')

            if childname == 'object1Id':
                ctnode = hf.getTreeNodeByID(self.troot, self.sikbns, child.text)
                function = getattr(self, re.sub(self.sikbns, '', ctnode.tag) + 'Handler')
                cnode = function(ctnode).node

                if cnode is None:
                    continue

                sibling = tnode.find(self.sikbns + 'object2Id')
                stnode = hf.getTreeNodeByID(self.troot, self.sikbns, sibling.text)
                function = getattr(self, re.sub(self.sikbns, '', stnode.tag) + 'Handler')
                scnode = function(stnode).node

                if scnode is None:
                    continue

                # add new relation to specified resources
                hf.addProperty(self.graph, cnode, scnode, gnode)

                object1Class = hf.getNodeClass(self.graph, cnode)
                if object1Class is not None:
                    hf.addProperty(self.graph, gnode, object1Class, rdflib.URIRef(self.nss['rdfs'] + 'domain'))
                object2Class = hf.getNodeClass(self.graph, scnode)
                if object2Class is not None:
                    hf.addProperty(self.graph, gnode, object2Class, rdflib.URIRef(self.nss['rdfs'] + 'range'))


        return self.ReturnValues(node=gnode, altnode=None)

    def codereferentieHandler(self, tnode):
        # code is optionally defined through its superclass
        node = None
        ttnode = tnode.find(self.sikbns + 'historyId')
        if ttnode is not None:
            ttnode = hf.getTreeNodeByID(self.troot, self.sikbns, ttnode.text)
            node = self.codereferentieHandler(ttnode).node

        nodeID = ''
        if node is not None:
            nodeID = hf.getNodeID(self.graph, node)

        hid = hf.genHash(tnode, self.sikbns, ['standaardCode', 'bronCode', 'bronCodeLijst', 'naamCodeLijst'], salt=nodeID)

        # concat code ID after code list ID
        # 'naamCodelijst' gets priority
        
        tag = 'naamCodelijst'
        ttnode = tnode.find(self.sikbns + tag)
        usedBronCode = False
        if ttnode is None:
            tag = 'bronCodelijst'
            ttnode = tnode.find(self.sikbns + tag)
            usedBronCode = True

        bhid = hf.genHash(None, None, [], salt=tag + ttnode.text)
        cbnode = hf.getNode(self.graph, bhid)
        if cbnode is None:
            cbnode = rdflib.URIRef(self.basens + bhid)

        # generate code node
        gnode = hf.getNode(self.graph, self.basens + bhid + hid)
        if gnode is not None:
            return self.ReturnValues(node=gnode, altnode=None)

        gnode = rdflib.URIRef(self.basens + bhid + hid)
        hf.extractGenericObjectFields(self.graph, gnode, tnode, self.sikbns)
        hf.addType(self.graph, gnode, rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document'))

        if node is not None:
            hf.addProperty(self.graph, gnode, node, rdflib.URIRef(self.nss['rdfs'] + 'subClassOf'))

        hf.addProperty(self.graph, self.groot, gnode, rdflib.URIRef(self.nss['crm'] + 'P67_refers_to'))
        for child in tnode.getchildren():
            childname = re.sub(self.sikbns, '', child.tag)
            if childname == 'bronCode':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
                hf.updateLabel(self.graph, gnode, "van concept '{}'".format(hf.rawString(child.text)), 'nl')
            if childname == 'standaardCode':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), datatype=rdflib.URIRef(self.nss['xsd'] + 'string'))
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'bronOmschrijving':
                if child.text is None:
                    continue
                cnode = rdflib.Literal(hf.rawString(child.text), lang='nl')
                hf.addProperty(self.graph, gnode, cnode, rdflib.URIRef(self.ontns + 'SIKB0102S_' + \
                                                                       childname))
            if childname == 'bronCodelijst':
                if child.text is None:
                    continue
                bnode = cbnode
                if not usedBronCode:
                    bhid = hf.genHash(None, None, [], salt=childname + child.text)
                    bnode = hf.getNode(self.graph, bhid)
                    if bnode is None:
                        bnode = rdflib.URIRef(self.basens + bhid)

                hf.addSchemaType(self.graph, self.ontns, bnode, gnode, childname)
            if childname == 'naamCodelijst':
                if child.text is None:
                    continue
                hf.addSchemaType(self.graph, self.ontns, cbnode, gnode, childname)
            if childname == 'historyId':
                pass

        return self.ReturnValues(node=gnode, altnode=None)
