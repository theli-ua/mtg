# !/usr/bin/python
import sys
import csv
import requests

sets = requests.get('https://mtgjson.com/json/SetList.json').json()
sets_dict = {x['name']: x['code'] for x in sets}
with open(sys.argv[1], 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Foil'] == 'foil':
            row['Name'] = row['Name'] + ' *F*'
        row['Edition'] = sets_dict[row['Edition']]
        print('{} {} ({})'.format(row['Count'], row['Name'], row['Edition']))
