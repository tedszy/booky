# booky.py
#
# Load publications.toml into data structure.
# Validate the data in the toml file.
# Create in-memory sqlite3 database.

import sqlite3
import operator
from tabulate import tabulate

# In case using python version < 3.11.
try:
    import tomllib
except ImportError:
    import toml as tomllib


class PublicationTable:

    def __init__(self, publication_filename):
        self.headers = ['key', 'title', 'BH', 'BW', 'CH', 'CW', 'CLR']
        self.filename = publication_filename
        with open(self.filename, 'rb') as f:
            self.data = tomllib.load(f)
        self.table = [[k, v['title'], v['block-height'], v['block-width'],
                          v['cover-height'], v['cover-width'], v['color']] 
                      for k, v in self.data.items()] 
        self.table_string = tabulate(sorted(self.table, 
                                            key=operator.itemgetter(0), 
                                            reverse=False), 
                                     self.headers, 
                                     tablefmt="grid", 
                                     floatfmt=".4f")  
             

if __name__ == '__main__':
    PT = PublicationTable("publication.toml")
    print(PT.table_string)
    print('Done.')



