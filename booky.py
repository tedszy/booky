# booky.py
#
# Load publications.toml into data structure,
# create in-memory sqlite3 database.

import sqlite3
import operator
import tabulate

try:
    import tomllib
except ImportError:
    import toml as tomllib


publication_filename = "publication.toml"

with open(publication_filename, "rb") as f:
    data = tomllib.load(f)

headers = ['key', 'title', 'BH', 'BW', 'CH', 'CW', 'CLR']
table = [[k, v['title'], v['block-height'], v['block-width'],
             v['cover-height'], v['cover-width'], v['color']] for k,v in data.items()] 

print(tabulate.tabulate(sorted(table, key=operator.itemgetter(0), reverse=False), 
                        headers, tablefmt="grid", floatfmt=".4f"))  

print('done.')
