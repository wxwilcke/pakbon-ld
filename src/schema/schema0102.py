#!/usr/bin/python3

import rdflib
import helpFunctions as hf
import re


class Schema0102:

    def __init__(self, troot, namespace):
        self.troot = troot
        self.basens = namespace['base']
        self.ns = re.sub(r'(\{.*\})schema', r'\1', troot.tag)

        self.baseid = 'SIKB0102_Schema'

        # new graph
        self.graph = rdflib.Graph(identifier=self.baseid)

        hf.setGraphNamespaceIDs(self.graph, namespace)
        self.nss = dict(ns for ns in self.graph.namespace_manager.namespaces())

        self.groot = rdflib.URIRef(self.basens + self.baseid)
        hf.addType(self.graph, self.groot, rdflib.URIRef(self.nss['owl'] + 'Ontology'))

        # title
        title = rdflib.Literal('Pakbon-ld Ontology', lang='en')
        hf.addProperty(self.graph, self.groot, title, rdflib.URIRef(self.nss['dcterms'] + 'title'))

        # description
        description = rdflib.Literal('An automatically generated ontology based on the elements ' + \
                                     'defined by the SIKB Archaeological Protocol 0102 (aka Pakbon).', lang='en')
        hf.addProperty(self.graph, self.groot, description, rdflib.URIRef(self.nss['dcterms'] + 'description'))


        for ctype in self.troot.iter(self.ns + 'complexType'):
            if 'name' in ctype.attrib.keys():
                name = ctype.attrib['name']
                basename = name[:1].lower() + name[1:-4]
                func = basename + 'Handler'
                getattr(self, func)(ctype, basename)

    def classHandler(self, ctype, name, superclass):
        node = rdflib.URIRef(self.basens + self.baseid + '_' + name)
        hf.addSubClassOf(self.graph, node, superclass)
        hf.addLabel(self.graph, node, name, 'nl')
        self.addDoc(ctype, node)

    def propertyHandler(self, element, basename, superprop, proprange=None):
        node = rdflib.URIRef(self.basens + self.baseid + '_' + basename + '_' + element.attrib['name'])
        hf.addType(self.graph, node, rdflib.URIRef(self.nss['rdf'] + 'Property'))
        hf.addProperty(self.graph, node, superprop, rdflib.URIRef(self.nss['rdfs'] + 'suppropertyOf'))
        hf.addLabel(self.graph, node, element.attrib['name'] + ' van ' + basename, 'nl')
        #self.addDoc(element, node)

        hf.addProperty(self.graph, node, rdflib.URIRef(self.basens + self.baseid + '_' + basename.title()), rdflib.URIRef(self.nss['rdfs'] + 'domain'))
        if proprange is not None:
            hf.addProperty(self.graph, node, proprange, rdflib.URIRef(self.nss['rdfs'] + 'range'))

    def addDoc(self, base, node):
        doc = base.find('./' + self.ns + 'annotation/' + self.ns + 'documentation')
        if doc is not None:
           hf.addProperty(self.graph, node, rdflib.Literal(doc.text, lang='nl'), \
                          rdflib.URIRef(self.nss['dcterms'] + 'description'))


    def adresHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['locn'] + 'Address'))

        for element in ctype.findall('./' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'straat':
                supprop = rdflib.URIRef(self.nss['locn'] + 'thoroughfare')
                supclass = rdflib.URIRef(self.nss['gn'] + 'Feature')
            if name == 'huisnummer':
                supprop = rdflib.URIRef(self.nss['locn'] + 'locatorDesignator')
            if name == 'postcode':
                supprop = rdflib.URIRef(self.nss['locn'] + 'postCode')
            if name == 'plaatsnaam':
                supprop = rdflib.URIRef(self.nss['locn'] + 'postName')
                supclass = rdflib.URIRef(self.nss['gn'] + 'Feature')
            if name == 'gemeente':
                supprop = rdflib.URIRef(self.nss['gn'] + 'parentADM2')
                supclass = rdflib.URIRef(self.nss['gn'] + 'Feature')
            if name == 'provincie':
                supprop = rdflib.URIRef(self.nss['gn'] + 'parentADM1')
                supclass = rdflib.URIRef(self.nss['gn'] + 'Feature')
            if name == 'land':
                supprop = rdflib.URIRef(self.nss['gn'] + 'parentCountry')
                supclass = rdflib.URIRef(self.nss['gn'] + 'Feature')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def persoonHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'naam':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P131_is_identified_by')
                supclass = rdflib.URIRef(self.nss['foaf'] + 'Person')
            if name == 'telefoon':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P76_has_contact_point')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E51_Contact_Point')
            if name == 'email':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P76_has_contact_point')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E51_Contact_Point')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def naamHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E21_Person'))

        for element in ctype.findall('./' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'achternaam':
                supprop = rdflib.URIRef(self.nss['foaf'] + 'familyName')
            if name == 'voornaam':
                supprop = rdflib.URIRef(self.nss['foaf'] + 'givenName')
            if name == 'initialen':
                supprop = rdflib.URIRef(self.nss['foaf'] + 'givenName')
            if name == 'tussenvoegsel':
                supprop = rdflib.URIRef(self.nss['foaf'] + 'givenName')
            if name == 'titel':
                supprop = rdflib.URIRef(self.nss['foaf'] + 'title')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def projectHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0001_EHProject'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'projectnaam':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E41_Appellation')
            if name == 'startdatum':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP1')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp')
            if name == 'einddatum':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP2')
                supclass = rdflib.URIRef(self.nss['crm'] + 'EHE0091_Timestamp')
            if name == 'onderzoeksmeldingsnummber':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P48_has_preferred_identifier')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E42_Identifier')
            if name == 'onderzoektype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')
            if name == 'omschrijving':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P3_has_note')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def organisatieHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'naam':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P131_is_identified_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E82_Actor_Appellation')
            if name == 'telefoon':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P76_has_contact_point')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E51_Contact_Point')
            if name == 'email':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P76_has_contact_point')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E51_Contact_Point')
            if name == 'adres':
                supprop = rdflib.URIRef(self.nss['locn'] + 'address')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def uitvoerderHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))

        for element in ctype.findall('./' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'uitvoerdercode':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E42_Identifier')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def bevoegdGezagHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E40_Legal_Body'))

    def projectlocatieHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0003_AreaOfInvestigation'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'provinciecode':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P89_falls_within')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation')
            if name == 'gemeentecode':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P89_falls_within')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation')
            if name == 'plaatscode':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P89_falls_within')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation')
            if name == 'toponiem':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P59i_is_located_on_or_within')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0002_ArchaeologicalSite')
            if name == 'kaartblad':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E46_Section_Definition')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def archisHandler(self, ctype, basename):
        pass

    def digitaalmediumHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E84_Information_Carrier'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'digitaalmediumtype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def documentHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E31_Document'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'documenttype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')
            if name == 'titel':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'title')
            if name == 'auteur':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'creator')
            if name == 'jaar':
                supprop = rdflib.URIRef(self.nss['prism'] + 'publicationDate')
            if name == 'serie':
                supprop = rdflib.URIRef(self.nss['prism'] + 'seriesTitle')
            if name == 'paginas':
                supprop = rdflib.URIRef(self.nss['prism'] + 'pageCount')
            if name == 'uitgever':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'publisher')
            if name == 'uitgavePlaats':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'spatial')
            if name == 'redacteur':
                supprop = rdflib.URIRef(self.nss['bibo'] + 'editor')
            if name == 'titelContainer':
                supprop = rdflib.URIRef(self.nss['prism'] + 'publicationName')
            if name == 'issn':
                supprop = rdflib.URIRef(self.nss['prism'] + 'issn')
            if name == 'isbn':
                supprop = rdflib.URIRef(self.nss['prism'] + 'isbn')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def verpakkingseenheidHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0010_BulkFind'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'beginperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP1')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp')
            if name == 'eindperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP2')
                supclass = rdflib.URIRef(self.nss['crm'] + 'EHE0091_Timestamp')
            if name == 'aantal':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P57_has_number_of_parts')
            if name == 'gewicht':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P43_has_dimension')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E54_Dimension')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def dossierHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E12_Production'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'dossiertype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def bestandHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E73_Information_Object'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'bestandnaam':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'title')
            if name == 'bestandtype':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'format')
            if name == 'bestandsinhoud':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'description')
            if name == 'software':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'description')
            if name == 'codeboek':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P67_refers_to')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def doosHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'bewaarTemperatuur':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0041_ContextFindTreatmentProcedure')
            if name == 'bewaarVochtigheid':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0041_ContextFindTreatmentProcedure')
            if name == 'lichtgevoelig':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0041_ContextFindTreatmentProcedure')
            if name == 'breekbaar':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0041_ContextFindTreatmentProcedure')
            if name == 'gevaarlijkeStoffen':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P129i_is_subject_of')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0041_ContextFindTreatmentProcedure')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def monsterHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0018_ContextSample'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'beginperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP1')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp')
            if name == 'eindperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP2')
                supclass = rdflib.URIRef(self.nss['crm'] + 'EHE0091_Timestamp')
            if name == 'monstertype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0053_ContextSampleType')
            if name == 'monsterverwerking':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P3_has_note')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def vindplaatsHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0004_SiteSubDivision'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'beginperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP1')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp')
            if name == 'eindperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP2')
                supclass = rdflib.URIRef(self.nss['crm'] + 'EHE0091_Timestamp')
            if name == 'vindplaatstype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')
            if name == 'vondstmeldingsnummer':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E42_Identifier')
            if name == 'waarnemingsnummer':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E42_Identifier')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def hoogtemetingHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E13_Attribute_Assignment'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'hoogtemetingmethode':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')
            if name == 'nap':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P40_observed_dimension')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E54_Dimension')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def tekeningHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0016_RecordDrawing'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'tekeningtype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0081_RecordDrawingReferenceType')
            if name == 'tekeningmateriaal':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'medium')
            if name == 'tekeningformaat':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P3_has_note')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0079_RecordDrawingNote')
            if name == 'tekenaar':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'creator')
            if name == 'tekeningdatum':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'date')
            if name == 'tekeningonderwerp':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'description')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def fotoHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0017_RecordPhotograph'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'opnametype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0085_RecordPhotographReferenceType')
            if name == 'opnamedatum':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'medium')
            if name == 'fotograaf':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'creator')
            if name == 'opnamedatum':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'date')
            if name == 'fotoonderwerp':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'description')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def putHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

    def segmentHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

    def waarnemingHandler(self, ctype, basename):
        pass

    def spoorHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'beginperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP1')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp')
            if name == 'eindperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP2')
                supclass = rdflib.URIRef(self.nss['crm'] + 'EHE0091_Timestamp')
            if name == 'grondspoortype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')
            if name == 'diepte':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P43_has_dimension')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E54_Dimension')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def stortHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

    def vondstcontextHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'contexttype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def vakHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'vaknummer':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E41_Appellation')
            if name == 'dikte':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P43_has_dimension')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E54_Dimension')
            if name == 'nap':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P43_has_dimension')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E54_Dimension')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def vullingHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'vorm':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P3_has_note')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0059_ContextStuffNote')
            if name == 'kleur':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P3_has_note')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0059_ContextStuffNote')
            if name == 'textuur':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P3_has_note')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0059_ContextStuffNote')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def structuurHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0008_ContextStuff'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'beginperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP1')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp')
            if name == 'eindperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP2')
                supclass = rdflib.URIRef(self.nss['crm'] + 'EHE0091_Timestamp')
            if name == 'structuurtype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def veldvondstHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E78_Collection'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'verzamelwijze':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P3_has_note')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0046_ContextNote')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def geolocatieHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E44_Place_Appellation'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'geometrie':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P87_is_identified_by')
                supclass = rdflib.URIRef(self.nss['geosparql'] + 'Geometry')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def boringHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

    def planumHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0007_Context'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'planumtype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def vondstHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crmeh'] + 'EHE0009_ContextFind'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'beginperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP1')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0091_Timestamp')
            if name == 'eindperiode':
                supprop = rdflib.URIRef(self.nss['crmeh'] + 'EXP2')
                supclass = rdflib.URIRef(self.nss['crm'] + 'EHE0091_Timestamp')
            if name == 'artefacttype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')
            if name == 'materiaalcategorie':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P45_consists_of')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0030_ContextFindMaterial')
            if name == 'aantal':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P43_has_dimension')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0031_ContextFindMeasurement')
            if name == 'gewicht':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P43_has_dimension')
                supclass = rdflib.URIRef(self.nss['crmeh'] + 'EHE0031_ContextFindMeasurement')
            if name == 'geconserveerd':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P147i_was_curated_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E87_Curation_Activity')
            if name == 'exposabel':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P147i_was_curated_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E87_Curation_Activity')
            if name == 'gedeselecteerd':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P147i_was_curated_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E87_Curation_Activity')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

    def attribuutHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E1_CRM_Entity'))

    def attribuuttypeHandler(self, ctype, basename):
        for element in ctype.findall('./' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'informatie':
                supprop = rdflib.URIRef(self.nss['rdfs'] + 'comment')
            if name == 'waardetype':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P2_has_type')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E55_Type')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)


    def objectrelatieHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['owl'] + 'ObjectProperty'))

        for element in ctype.findall('./' + self.ns + 'complexContent/' + self.ns + 'extension/' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'objectrelatietype':
                supprop = rdflib.URIRef(self.nss['rdfs'] + 'comment')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)


    def codereferentieHandler(self, ctype, basename):
        self.classHandler(ctype, basename.title(), rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document'))

        for element in ctype.findall('./' + self.ns + 'sequence/' + self.ns + 'element'):
            if 'name' not in element.attrib.keys():
                continue

            name = element.attrib['name']
            supprop = None
            supclass = None
            if name == 'bronCode':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P129_is_about')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E33_Linguistic_Object')
            if name == 'standaardCode':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P1_is_identified_by')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E75_Conceptual_Object_Appellation')
            if name == 'bronOmschrijving':
                supprop = rdflib.URIRef(self.nss['dcterms'] + 'description')
            if name == 'bronCodeLijst':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P71i_is_listed_in')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document')
            if name == 'naamCodeLijst':
                supprop = rdflib.URIRef(self.nss['crm'] + 'P71i_is_listed_in')
                supclass = rdflib.URIRef(self.nss['crm'] + 'E32_Authority_Document')

            if name != '' and supprop is not None and supclass is not None:
                self.propertyHandler(element, basename, supprop, supclass)
                self.classHandler(element, basename.title() + '.' + name.title(), supclass)
            elif name != '' and supprop is not None:
                self.propertyHandler(element, basename, supprop)

