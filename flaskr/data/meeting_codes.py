import os
import json
from os import listdir
from os.path import isfile, join


codes = dict()
codes['ICSI'] = dict()

input_dir = 'flaskr/data/ICSI_json'

onlyfiles = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]

id = 0

for file in onlyfiles:
    codes['ICSI'][100 + id] = str(file).split('/')[-1]
    id += 1


codes['com'] = dict()

input_dir = 'flaskr/data/com'

onlyfiles = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]

id = 0

for file in onlyfiles:
    codes['com'][200 + id] = str(file).split('/')[-1]
    id += 1


with open('flaskr/data/codes.json', 'w+') as outfile:
    json.dump(codes, outfile)
    outfile.close()