#!/usr/bin/python3

import sys
import os
import argparse
import re
import data.writer as writer
import translator

supported_version = '3.1.0'
version = '0.2'

def main(parser):
    sikb_zip = re.sub('src/pakbon-ld.py', 'if/SIKB0102 versie 3.1.0 XSD en Lookup domeintabellen.zip', os.path.realpath(__file__))

    args = parser.parse_args()

    if args.version:
        print('Pakbon-ld v{0}'.format(version))
        sys.exit(0)

    if args.endpoint == '':
        args.endpoint = args.default_namespace + 'sparql/'

    if args.input_path == '' and args.generate_ontology is False and args.generate_ontology is False:
        print('Missing required input (flags).\nUse \'pakbon-ld.py -h\' for help.')
        sys.exit(1)

    if args.output_path == '' and args.input_path != '' :
        args.output_path = os.getcwd() + '/' + re.sub(r'^(?:.*/)?(.*)\..*$', r'\1', args.input_path)
    else:
        args.output_path = os.getcwd() + '/' + 'SIKB0102'

    (graph, ontology, vocabulary) = translator.translate(args.input_path,\
                                                         args.align_with,\
                                                         args.default_namespace,\
                                                         sikb_zip,\
                                                         args.generate_ontology,\
                                                         args.generate_vocabulary,\
                                                         args.ignore_version,\
                                                         args.align,\
                                                         args.endpoint,\
                                                         args.enable_georesolver,\
                                                         args.interactive)

    if graph is not None:
        writer.write(graph, args.output_path + extOf(args.serialization_format), args.serialization_format)
    if ontology is not None:
        writer.write(ontology, args.output_path + '_Ontology' + extOf(args.serialization_format), args.serialization_format)
    if vocabulary is not None:
        writer.write(vocabulary, args.output_path + '_Vocabulary' + extOf(args.serialization_format), args.serialization_format)


def extOf(sformat=None):
    if sformat == 'n3':
        return '.n3'
    elif sformat == 'nquads':
        return '.nq'
    elif sformat == 'ntriples':
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", help="input path", default='')
    parser.add_argument("-o", "--output_path", help="output path", default='')
    parser.add_argument("-d", "--default_namespace", help="default namespace of graph",\
                        default="http://www.example.org/")
    parser.add_argument("-f", "--serialization_format", help="serialization format of output",\
                        choices=["n3", "nquads", "ntriples", "pretty-xml", "trig", "trix", "turtle", "xml"], default='turtle')
    parser.add_argument("--version", help="version of this tool", action="store_true")
    parser.add_argument("--ignore_version", help="force processing unsupported version of pakbon",\
                        action="store_true")
    parser.add_argument("--align", help="align encountered resources with default graph, via endpoint, or both",\
                        choices=["local", "global", "both"], default="off")
    parser.add_argument("--enable_georesolver", help="resolve and link geospatial resources",\
                        action="store_true")
    parser.add_argument("--align_with", help="one or more graphs to align with if align is set to 'local' or 'both'",\
                        nargs="*", default=[])
    parser.add_argument("--endpoint", help="SPARQL endpoint to align with if align is set to 'global' or 'both'", default='')
    parser.add_argument("--interactive", help="alignment mode", action="store_true")
    parser.add_argument("--generate_ontology", help="generate and write ontology", action="store_true")
    parser.add_argument("--generate_vocabulary", help="generate and write vocabulary", action="store_true")
                        
    main(parser)
