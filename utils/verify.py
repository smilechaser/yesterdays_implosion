#!/usr/bin/env python3

'''
Quick tool to parse and dump a YAML file.
'''

import pprint
import sys
import yaml

PRINT_WIDTH = 120

for filename in sys.argv[1:]:

    print('*' * PRINT_WIDTH)
    print('*{}*'.format(filename.center(PRINT_WIDTH-2)))
    print('*' * PRINT_WIDTH)

    with open(filename, 'r') as fin:

        docs = yaml.load_all(fin)

        for doc in docs:

            pprint.pprint(doc, width=PRINT_WIDTH)

            print('-' * PRINT_WIDTH)
