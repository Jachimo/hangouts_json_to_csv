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
    
    print("Reading " + json_path)
    
    with open(json_path, 'r') as json_file:
        data = ijson.items(json_file, 'item')
        participants_id_map = get_participants(data)  # returns dictionary of {userid:username}
        chats = {}
        message_count = 0
        
        print("Found " + str(len(participants_id_map)) + " participants")
        
        for event in find_nodes(data, 'event'):
            for conversation in event:
                conversation_id = find_node(conversation, 'id')
                timestamp = int(find_node(conversation, 'timestamp')) / 10**6
                timestamp = dt.fromtimestamp(timestamp).strftime(DATE_FORMAT)
                
                sender_id = find_node(conversation['sender_id'], 'gaia_id')
                sender = participants_id_map[sender_id]
                
                msgs = [msg.encode('utf-8') for msg in find_nodes(conversation, 'text') if msg.strip()]
                for msg in msgs:
                    message_count = message_count + 1
                    chats.setdefault(conversation_id, []).append('{}\t{}\t{}'.format(timestamp, sender, msg))
        
        print("Found " + str(len(chats)) + " chats")
        print("and " + str(message_count) + " messages")
        print() # blank line
        
        print("PARTICIPANTS\n============")
        for userid in participants_id_map:
            print("\t" + participants_id_map[userid] + "\t" + userid)

def find_nodes(root, query):
    """ Interprets json as tree and finds all nodes with given string. """

    if not isinstance(root, dict):
        return []

    rv = []
    for key, value in root.items():
        if key == query:
            rv.append(value)
            continue

        if not isinstance(value, list):
            # single json entry, make json array
            value = [value]

        for node in value:
            rv.extend(find_nodes(node, query))

    return rv

def find_node(root, query):
    """ Interprets JSON as tree and finds first node with givens string. """

    if not isinstance(root, dict):  # skip leaf
        return None

    for key, value in root.items():
        if key == query:
            return value

        if not isinstance(value, list):
            value = [value]

        for node in value:
            rv = find_node(node, query)
            if rv:
                return rv
    return None


def get_participants(json_data):
    """ Finds all participants in Google Hangouts JSON log and returns dictionary
        { user_id : username }. """

    all_participant_data = find_nodes(json_data, 'participant_data')

    participants_id_map = {}
    for conv_participants in all_participant_data:
        for participant in conv_participants:
            username = participant['fallback_name'].encode('utf-8')
            user_id = find_node(participant['id'], 'gaia_id')
            participants_id_map[user_id] = username

    return participants_id_map

def verbose_usage_and_exit():
    """ Prints usage and exits. """

    sys.stderr.write('Usage:\n')
    sys.stderr.write('\tpython <script_name> <file_json> <out_dir>\n'.format(sys.argv[0]))
    exit(0)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    if len(sys.argv) == 2:
        describe(sys.argv[1])
    else:
        verbose_usage_and_exit()
