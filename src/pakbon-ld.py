#!/usr/bin/python3

import sys
import getopt
import data.reader as reader
import data.writer as writer
import translator

supported_version = '3.1.0'
version = '0.1'


def main(argv):
    ifile = ''
    ofile = ''
    sformat = 'turtle'
    ignore_version = False

    try:
        opts, args = getopt.getopt(argv, "hi:o:f:", ["if=", "of=", "format=", "ignore_version", "version"])
    except getopt.GetoptError:
        print('pakbon-ld.py -i <inputfile> [-o <outputfile> -f <serialization format> --ignore_version, --version]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(str('A tools to translate the SIKB archaeological protocol, aka the Pakbon, to its Semantic Web ' +
                      'equivalent.\nNote that only version {0} of this protocol is supported, and that the used data '.format(supported_version) +
                      'model may change in subsequent updates.\nUsage:\n\t' +
                      'pakbon-ld.py -i <inputfile> [-o <outputfile> -f <serialization format> -ignore_version]'))
            sys.exit(0)
        elif opt in ("-i", "--ifile"):
            ifile = arg
        elif opt in ("-o", "--ofile"):
            ofile = arg
        elif opt in ("-f", "--format"):
            sformat = arg
        elif opt in ("--ignore_version"):
            ignore_version = True
        elif opt in ("--version"):
            print('Pakbon-ld v{0}'.format(version))
            sys.exit(0)

    if ifile == '':
        print('Missing input file.\nUse \'pakbon-ld.py -h\' for help.')
        sys.exit(1)

    if ofile == '':
        ofile = ifile.rstrip('xml') + 'rdf'

    (et, tree, current_version) = reader.read(ifile, ignore_version)
    writer.write(translator.translate(et, tree, current_version), ofile, sformat)


def translate(tree=None):
    if tree is None:
        raise ValueError()

    return translate.translate(tree)

if __name__ == "__main__":
    main(sys.argv[1:])
