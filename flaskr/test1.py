import json

def get_codes():
    with open('flaskr/data/codes.json', 'r') as json_file:
        codes = json.load(json_file)
        json_file.close()
    return codes["ICSI"]


codes = get_codes()

for key, value in codes.items():
    print(key)
    print(value)