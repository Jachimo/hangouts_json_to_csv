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
            print("--- Processing event with ID " + event['event_id'])
            
            if message_count >= MAX_OUT:
                break
            
            if 'chat_message' not in event:
                print("No chat_message found in event; skipping")
                continue  # if the event doesn't contain chat message data, skip it
            
            conversation_id = event['conversation_id']['id']
            timestamp = int(event['timestamp']) / 10**6
            timestamp = dt.fromtimestamp(timestamp).strftime(DATE_FORMAT)
            
            sender_id = ( event['sender_id']['chat_id'], event['sender_id']['gaia_id'] )
            
            for msg in event['chat_message']:
                message_count = message_count + 1
                print("-- Processing message (count is now " + str(message_count) + ")")
                
                if conversation_id not in chats:
                    print("New conversation ID; creating empty list")
                    chats[conversation_id] = []  # initialize as empty
                    print(chats)
                    # chats is a dictionary by conversation_id
                    # each chat within it is a list
                    # each entry in the list is a tuple of (timestamp,sender,msg)
                
                for segment in event['chat_message']['message_content']['segment']:
                    print("- Processing segment: " + str(segment))
                    segment_message = (timestamp, sender_id, segment['text'])
                    print("Appending to chat " + str(conversation_id) + ": " + str(segment_message))
                    print("Contents of chats before append: " + str(chats))
                    print("Chats has type " + str(type(chats)) + " and chats[conversation_id] has type " + str(type(chats[conversation_id])))
                    print("Content (of type " + str(type(segment_message)) + ") being appended: " + str(segment_message))
                    chats[conversation_id].append( segment_message )
                    print("Contents of chats after append: " + str(chats))
        
        print("Found " + str(len(chats)) + "total chat conversations")
        print("and " + str(message_count) + " messages")
        print("---- MESSAGE CONTENT")
        for chat in chats:
            print(str(chat))

if __name__ == '__main__':
    main(sys.argv[1])
