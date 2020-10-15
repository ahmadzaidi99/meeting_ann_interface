import json
import os
from os import listdir
from os.path import isfile, join


class get_json:

    def read_file(self, filename):
        with open(filename) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        return content

    def get_info(self, filename):
        self.meeting['metadata']['meeting_name'] = str(filename).split('/')[-1]

    def get_turns(self, content):
        turn_num = 1
        for line in content:
            contribution = line.split(':')[1]
            role_init = line.split('(')[1]
            role_final = role_init.split(')')[0]
            id_init = line.split(',')[1]
            id_final = id_init.split('(')[0].strip()
            self.meeting['turns'].append({
                'turn': turn_num,
                'name': role_final,
                'id': id_final,
                'contribution': contribution
            })
            turn_num += 1


    def __init__(self, input_file, output_dir):
        self.meeting = dict()
        self.meeting['metadata'] = dict()
        self.meeting['turns'] = []
        self.numturns = 0

        content = self.read_file(input_file)
        self.get_info(input_file)
        self.get_turns(content)

        name = self.meeting['metadata'].get('meeting_name')

        filename = name + '.json'

        path = output_dir

        if not os.path.exists(path):
            os.makedirs(path)

        with open(os.path.join(path, filename), 'w+') as outfile:
            json.dump(self.meeting, outfile)
            outfile.close()


def run(input_dir, output_dir):
    onlyfiles = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
    for file in onlyfiles:
        get_json(os.path.join(input_dir, file), output_dir)

def test():
    get_json('flaskr/data/ICSI_txt/Bdb001', 'flaskr/data/test/')

run('flaskr/data/ICSI_txt/', 'flaskr/data/ICSI_json/')