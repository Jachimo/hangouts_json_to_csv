#!/usr/bin/env python3

# Quick-n-dirty script to parse a Hangouts JSON archive file
#  and dump participant data items

import ijson
import sys
import pprint

MAX_OUT = 3

def main(json_path):
    with open(json_path, 'rb') as json_file:
        i=0
        all_participant_data = ijson.items(json_file, 'conversations.item.conversation.conversation.participant_data')
        for conv_participants in all_participant_data:
            if i >= MAX_OUT:
                break
            print("--- BEGIN conv_participant")
            for participant in conv_participants:
                print("Raw participant data: " + str(participant))
#                user_id = find_node(participant['id'], 'gaia_id')
#                print("User ID is " + user_id)
#                try:
#                    username = participant['fallback_name'].encode('utf-8')  # this sometimes throws KeyError
#                    print('Found user ' + str(username))
#                except KeyError:
#                    username = 'user_' + user_id  # use user id if we can't determine name
#                    print('Username not present, defaulting to ' + str(username))
            print("Raw conv_participants data:  " + str(conv_participants))
            i += 1

            
if __name__ == '__main__':
    main(sys.argv[1])
