#!/usr/bin/env python3

# Quick-n-dirty script to parse a Hangouts JSON archive file
#  and dump all the "conversation events"

import ijson
import sys
import pprint

def main(json_path):
    with open(json_path, 'rb') as json_file:
        i=0
        for event in ijson.items(json_file, 'conversations.item.events.item'):
            if i >= 5:
                break
            print("--- BEGIN EVENT ITEM")
            for key, value in event.items():
                print("KEY: " + str(key) + "\n\tVALUE: " +  str(value))
            i += 1
            print("--- END EVENT ITEM")

if __name__ == '__main__':
    main(sys.argv[1])
