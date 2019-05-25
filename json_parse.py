#!/usr/bin/env python3

# Quick-n-dirty script to parse a JSON file and show its structure...
#  Uses ijson (pip install ijson) to process arbitrarily large files

# Based on sample code from http://www.aylakhan.tech/?p=27

import ijson
import sys

# Change this based on number of nodes you want to print
MAX_OUT = 100

def main(json_path):
    with open(json_path, 'rb') as json_file:
        parsed = ijson.parse(json_file)
        i=0
        for prefix, datatype, value in parsed:
            if i >= MAX_OUT:
                break
            print('prefix={}, type={}, value={}'.format(prefix, datatype, value))

if __name__ == '__main__':
    main(sys.argv[1])
