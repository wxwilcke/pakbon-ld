#!/usr/bin/python3

import sys
import data.reader as reader
import data.writer as writer
import translator

sformat = 'turtle'

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        raise RuntimeError('Wrong number of arguments.\nUsage: python pakbon-ld.py <input_file.xml> [output_file.rdf]')

    ifile = sys.argv[1]
    ofile = sys.argv[2] if len(sys.argv) == 3 else ifile.rstrip('xml') + 'rdf'

    (et, tree) = reader.read(ifile)
    writer.write(translator.translate(et, tree), ofile, sformat)


def translate(tree=None):
    if tree is None:
        raise ValueError()

    return translate.translate(tree)
