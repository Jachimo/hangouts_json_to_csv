#!/usr/bin/env python3

import json
import ijson
from datetime import datetime as dt
import sys
import os

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'  # desired output format, strftime

MAX_OUT = 10

def main(json_path):
    
    print("Reading " + json_path )
    
    with open(json_path, 'rb') as json_file:
        
        chats = {}
        message_count = 0
        
        for event in ijson.items(json_file, 'conversations.item.events.item'):
            
            if message_count >= MAX_OUT:
                break
            
            if 'chat_message' not in event:
                continue  # if the event doesn't contain chat message data, skip it
            
            conversation_id = event['conversation_id']['id']
            timestamp = int(event['timestamp']) / 10**6
            timestamp = dt.fromtimestamp(timestamp).strftime(DATE_FORMAT)
            
            sender_id = ( event['chat_message']['sender_id']['chat_id'], event['chat_message']['sender_id']['gaia_id'] )
            
            for msg in event['chat_message']:
                message_count = message_count + 1
                print("Message count is now " + str(message_count))
                
                if conversation_id not in chats:
                    chats[conversation_id] = []  # initialize as empty
                    # chats is a dictionary by conversation_id
                    # each chat within it is a list
                    # each entry in the list is a tuple of (timestamp,sender,msg)
                
                for segments in event['chat_message']['message_content']['segment']:
                    for segment in segments:
                        # each segment is a list of dicts, each dict is {text : type}
                        chats[conversation_id] = chats[conversation_id].append( (timestamp, sender, segment['text']) )
        
        print("Found " + str(len(chats)) + "total chat conversations")
        print("and " + str(message_count) + " messages")

if __name__ == '__main__':
    main(sys.argv[1]
