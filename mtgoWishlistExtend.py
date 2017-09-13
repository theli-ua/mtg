# !/usr/bin/python
# Merge all duplicated cards, limit to max(4, current max between variants)
# Add all variants of each card with the same amount
import xml.etree.ElementTree as etree
import sys
import os
from collections import defaultdict
from glob import glob
from xml.dom import minidom

wishlist = etree.fromstring(open(sys.argv[1]).read())
quantities = defaultdict(int)
names_to_ids = defaultdict(set)
ids_to_name = {}
cards_to_names = {}
clones = {}

# wishlist = input_tree.getroot()

# Calc quantities
for card in wishlist.findall('Cards'):
    quantities[card.get('Name')] = \
            max(quantities[card.get('Name')], int(card.get('Quantity')),1)
    wishlist.remove(card)

# Get all ids
WINEPREFIX = os.environ.get('WINEPREFIX') or '~/wine'
WINEPREFIX = os.path.expandvars(os.path.expanduser(WINEPREFIX))

# Find MTGO Dir
mtgo_path = glob(os.path.join(WINEPREFIX, 'drive_c', 'users', '*', 
                              'Local Settings', 'Application Data', 'Apps', 
                              '*', '*', '*', '*', 'CardDataSource'))
if len(mtgo_path) < 1:
    print('Could not find mtgo path, exiting', file=sys.stderr)
    sys.exit(2)
else:
    mtgo_path = mtgo_path[0]
    print('Using: {}'.format(mtgo_path), file=sys.stderr)
string_names = etree.parse(os.path.join(mtgo_path, 'CARDNAME_STRING.xml')).getroot()
ids_to_name = {node.get('id'):
               node.text for node in 
               string_names.findall('CARDNAME_STRING_ITEM')}

for xml in glob(os.path.join(mtgo_path, '*.xml')):
    try:
        root = etree.parse(xml).getroot()
    except:
        continue
    for card in root.findall('DigitalObject'):
        card_id = card.get('DigitalObjectCatalogID')[4:]
        try:
            name_id = card.find('CARDNAME_STRING').get('id')
            name = ids_to_name[name_id]
            if name in quantities:
                names_to_ids[name].add(card_id)
                cards_to_names[card_id] = name
        except:
            clones[card_id] = card.find('CLONE_ID').get('value')[4:]


def cloned_to_name(cloned_id):
    if cloned_id in clones:
        return cloned_to_name(clones[cloned_id])
    return cards_to_names.get(cloned_id)

for clone in clones:
    name = cloned_to_name(clone)
    if name is not None:
        names_to_ids[name].add(clone)

for name, ids in names_to_ids.items():
    for _id in ids:
        etree.SubElement(wishlist, 'Cards',
                         {
                            'Quantity': str(quantities[name]),
                            'CatID': _id,
                            'Sideboard': 'false',
                            'Name': name
                            })
print(minidom.parseString(etree.tostring(wishlist)).toprettyxml())
