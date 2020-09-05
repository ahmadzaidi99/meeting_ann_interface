import os
import json
from os.path import isfile, join

def get_meeting(meeting_id):
    with open('flaskr/data/codes.json', 'r') as json_file:
        codes = json.load(json_file)
        json_file.close()
    print(codes)
    file = codes['ICSI'].get(str(meeting_id))
    print(file)

get_meeting(100)