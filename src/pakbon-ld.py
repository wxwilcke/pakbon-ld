#!/usr/bin/python3

import sys
import os
import getopt
import re
import data.writer as writer
import translator

supported_version = '3.1.0'
version = '0.1.1'


def main(argv):
    sikb_zip = re.sub('src/pakbon-ld.py', 'if/SIKB0102 versie 3.1.0 XSD en Lookup domeintabellen.zip', os.path.realpath(__file__))
    ifile = ''
    ofile = ''
    default_ns = 'http://www.example.org/'
    sformat = 'turtle'
    ignore_version = False
    gen_ontology = False
    gen_vocabulary = False

    try:
        opts, args = getopt.getopt(argv, "d:f:hi:o:", ["if=", "of=", "format=", "default_namespace=", "ignore_version",\
                                                       "generate_ontology", "generate_vocabulary", "version"])
    except getopt.GetoptError:
        print('pakbon-ld.py -i <inputfile> [-d <default namespace> -o <outputfile> -f <serialization format> \
              --ignore_version --generate_ontology --generate_vocabulary --version]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(str('A tools to translate the SIKB archaeological protocol, aka the Pakbon, to its Semantic Web ' +
                      'equivalent.\nNote that only version {0} of this protocol is supported, and that the used data '.format(supported_version) +
                      'model may change in subsequent updates.\nUsage:\n\t' +
                      'pakbon-ld.py -i <inputfile> [-d <default namespace> -o <outputfile> -f <serialization format>' +
                      ' --ignore_version --generate_ontology --version]'))
            sys.exit(0)
        elif opt in ("-i", "--ifile"):
            ifile = arg
        elif opt in ("-o", "--ofile"):
            ofile = arg
        elif opt in ("-d", "--default_namespace"):
            default_ns = arg
        elif opt in ("-f", "--format"):
            sformat = arg
        elif opt in ("--ignore_version"):
            ignore_version = True
        elif opt in ("--generate_ontology"):
            gen_ontology = True
        elif opt in ("--generate_vocabulary"):
            gen_vocabulary = True
        elif opt in ("--version"):
            print('Pakbon-ld v{0}'.format(version))
            sys.exit(0)

    if ifile == '' and gen_ontology is False and gen_vocabulary is False:
        print('Missing required input (flags).\nUse \'pakbon-ld.py -h\' for help.')
        sys.exit(1)

    if ofile == '' and ifile != '' :
        ofile = os.getcwd() + '/' + re.sub(r'^(?:.*/)?(.*)\..*$', r'\1', ifile)
    else:
        ofile = os.getcwd() + '/' + 'SIKB0102'

    (graph, ontology, vocabulary) = translator.translate(ifile, default_ns, sikb_zip, gen_ontology, gen_vocabulary, \
                                                         ignore_version)

    if graph is not None:
        writer.write(graph, ofile + extOf(sformat), sformat)
    if ontology is not None:
        writer.write(ontology, ofile + '_Ontology' + extOf(sformat), sformat)
    if vocabulary is not None:
        writer.write(vocabulary, ofile + '_Vocabulary' + extOf(sformat), sformat)


def extOf(sformat=None):
    if sformat == 'n3':
        return '.n3'
    elif sformat == 'nquads':
        return '.nq'
    elif sformat == 'nt':
        return '.nt'
    elif sformat == 'pretty-xml':
        return '.xml'
    elif sformat == 'trig':
        return '.trig'
    elif sformat == 'trix':
        return '.trix'
    elif sformat == 'turtle':
        return '.ttl'
    elif sformat == 'xml':
        return '.xml'
    else:
        return '.rdf'


def translate(tree=None):
    if tree is None:
        raise ValueError()

    return translate.translate(tree)

if __name__ == "__main__":
    main(sys.argv[1:])
