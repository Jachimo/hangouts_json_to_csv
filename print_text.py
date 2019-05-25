#!/usr/bin/env python3

# Quick-n-dirty script to parse a Hangouts JSON archive file
#  and dump all the text elements/messages

import ijson
import sys
import pprint

def main(json_path):
    with open(json_path, 'rb') as json_file:
        print("Processing " + json_path)
        i=0
        for item in ijson.items(json_file, 'conversations.item.events.item.chat_message.message_content.segment.item.text'):
            if i >= 5:
                break
            print("--- BEGIN TEXT ELEMENT")
            pprint.pprint(item)
            print("--- END EVENT ITEM")
            i += 1

if __name__ == '__main__':
    main(sys.argv[1])
