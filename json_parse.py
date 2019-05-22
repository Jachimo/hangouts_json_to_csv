#!/usr/bin/env python3

# Quick-n-dirty script to parse a JSON file and show its structure...
#  Uses ijson (pip install ijson) to process arbitrarily large files

import ijson
import sys

def main(json_path):
    with open(json_path, 'rb') as json_file:
        parsed = ijson.parse(json_file)

        for prefix, datatype, value in parsed:
            print('prefix={}, type={}, value={}'.format(prefix, datatype, value))


if __name__ == '__main__':
    main(sys.argv[1])
