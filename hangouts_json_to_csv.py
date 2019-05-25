#!/usr/bin/env python3

import json
import ijson
from datetime import datetime as dt
import sys
import os

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'  # desired output format, strftime

def main(json_path, out_dir_path):
    """ Converts Google Hangouts log given in JSON format
        and stores them in location given as second argument.
        Logs are stored in CSV format, one file per conversaton. """

    if not os.path.isdir(out_dir_path):
        os.mkdir(out_dir_path)
        print("Created {} directory".format(out_dir_path))

    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
        participants_id_map = get_participants(data)
        chats = {}

        for event in find_nodes(data, 'event'):
            for conversation in event:
                conversation_id = find_node(conversation, 'id')
                timestamp = int(find_node(conversation, 'timestamp')) / 10**6
                timestamp = dt.fromtimestamp(timestamp).strftime(DATE_FORMAT)

                sender_id = find_node(conversation['sender_id'], 'gaia_id')
                sender = participants_id_map[sender_id]

                msgs = [msg.encode('utf-8') for msg in find_nodes(conversation, 'text') if msg.strip()]
                for msg in msgs:
                    chats.setdefault(conversation_id, []).append('{}\t{}\t{}'.format(timestamp, sender, msg))

        for chat_id in chats:
            file_path = '{}/{}.csv'.format(out_dir_path, chat_id)
            with open(file_path, 'w') as out:
                print("Created {} log file".format(file_path))
                for msg in sorted(chats[chat_id]):
                    out.write(msg + '\n')

def describe(json_path):
    """ Prints information about the contents of a Google Hangouts
        JSON log to standard output."""
    
    if debug:
        print("Reading " + json_path + " in describe mode")
    
    with open(json_path, 'rb') as json_file:
        
        print("Generating participant ID map")
        participants_id_map = get_participants(json_file)  # returns dictionary of {userid:username}
        print("Participant ID map complete")
        print("\tFound " + str(len(participants_id_map)) + " participants\n")
        
        chats = {}
        message_count = 0
        invalid_count = 0
        
        for event in ijson.items(json_file, 'conversations.item.events.item'):
            if 'chat_message' not in event:
                invalid_count += 1
                continue  # if the event doesn't contain chat message data, skip it
            
            conversation_id = event['conversation_id']['id']
            timestamp = int(event['timestamp']) / 10**6
            timestamp = dt.fromtimestamp(timestamp).strftime(DATE_FORMAT)
            
            try:
                sender_chat_id = event['chat_message']['sender_id']['chat_id']
            except KeyError: 
                if debug:
                    print("Sender chat ID not found for " + conversation_id + ", set to None")
                sender_chat_id = None
            
            try:
                sender_gaia_id = event['chat_message']['sender_id']['gaia_id']
            except KeyError:
                if debug:
                    print("Sender gaia ID not found for " + conversation_id + ", set to None")
                sender_gaia_id = None
            
            if sender_chat_id is None and sender_gaia_id is None:
                if debug:
                    print("Sender ID could not be determined, skipping event")
                invalid_count += 1
                continue  # there's no point continuing if both the sender IDs are empty
            
            sender_id = ( sender_chat_id , sender_gaia_id )
                
            
            #  Determine using participants_id_map[user_id] = username  (see below)
            sender = participants_id_map[sender_id]
            
            for msg in event['chat_message']:
                message_count = message_count + 1
                print("Message count is now " + str(message_count))
                
                if conversation_id not in chats:
                    chats[conversation_id] = []  # initialize as empty
                    # chats is a dictionary by conversation_id
                    # each chat within it is a list
                    # each entry in the list is a tuple of (timestamp,sender,msg)
                
                for segment in event['chat_message']['message_content']['segment']:
                    segment_message = (timestamp, sender_id, segment['text'])
                    chats[conversation_id].append( segment_message )
        
        if debug:
            print("Found " + str(len(chats)) + " total chats")
            print("and " + str(message_count) + " messages")
            print("not including " + str(invalid_count) + " invalid events\n\n")
            print("PARTICIPANTS\n============")
            for userid in participants_id_map:
                print("\t" + str(participants_id_map[userid]) + "\t" + str(userid))

def get_participants(json_file):
    """ Finds all participants in Google Hangouts JSON log and returns dictionary
        { user_id : username }. """
    
    json_file.seek(0)  # ensure we are at beginning of file
    
    all_participant_data = ijson.items(json_file, 'conversations.item.conversation.conversation.participant_data')
    
    participants_id_map = {}
    for conv_participants in all_participant_data:
        for participant in conv_participants:
            user_id = ( participant['id']['chat_id'], participant['id']['gaia_id'] )
            try:
                username = participant['fallback_name'].encode('utf-8')  # this sometimes throws KeyError
                if debug:
                    print('Found user ' + str(username))
            except KeyError:
                username = 'user_' + user_id[0]  # use user id if we can't determine name
                if debug:
                    print('Username not present, defaulting to ' + str(username))
            participants_id_map[user_id] = username

    json_file.seek(0)  # reset for reuse
    return participants_id_map

def verbose_usage_and_exit():
    """ Prints usage and exits. """

    sys.stderr.write('Usage:\n')
    sys.stderr.write('\tpython <script_name> <file_json> <out_dir>\n'.format(sys.argv[0]))
    exit(1)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        debug = False
        main(sys.argv[1], sys.argv[2])
    if len(sys.argv) == 2:
        debug = True
        describe(sys.argv[1])
    else:
        verbose_usage_and_exit()
