# booky.py
#
# Load publications.toml into data structure.
# Validate the data in the toml file.
# Create in-memory sqlite3 database.
#
# * Multiple publication toml files.
# * add prefix OBV to buckram colors.


import argparse
import operator
import sqlite3
import tomllib
from tabulate import tabulate


field_keys = ['block-height', 'block-width', 'color', 'cover-height', 
              'cover-width', 'title']


with open('configure.toml', 'rb') as config_file:
    config_data = tomllib.load(config_file)


with open('publication.toml', 'rb') as publication_file:
    publication_data = tomllib.load(publication_file)


def valid_color(color):
    return color in config_data['validation']['colors']


def valid_block_height(block_height):
    a, b = config_data['validation']['block-limits']
    return a <= block_height <= b


def valid_block_width(block_width):
    a, b = config_data['validation']['block-limits']
    return a <= block_width <= b


def valid_cover_height(cover_height):
    a, b = config_data['validation']['cover-limits']
    return a <= cover_height <= b


def valid_cover_width(cover_width):
    a, b = config_data['validation']['cover-limits']
    return a <= cover_width <= b


def validation_report(publication_key, issue_key, message):
    print()
    print(message + ' ...')
    for field_key in field_keys:
        if field_key == issue_key:
            print('{0} = {1}   <===== *** HERE ***'
                  .format(field_key, publication_data[publication_key][field_key]))
        else:

            print('{0} = {1}'
                  .format(field_key, publication_data[publication_key][field_key]))
    print()


class PublicationTable:

    def __init__(self, publication_filename):
        self.headers = ['key', 'title', 'BH', 'BW', 'CH', 'CW', 'CLR']
        self.filename = publication_filename
        with open(self.filename, 'rb') as f:
            self.data = tomllib.load(f)
        self.table = [[k, v['title'], 
                          v['block-height'], 
                          v['block-width'],
                          v['cover-height'], 
                          v['cover-width'], 
                          v['color']] 
                      for k, v in self.data.items()] 
        self.table_string = tabulate(sorted(self.table, 
                                            key=operator.itemgetter(0), 
                                            reverse=False), 
                                     self.headers, 
                                     tablefmt="grid", 
                                     floatfmt=".4f")  
             

if __name__ == '__main__':
    for publication_key, val in publication_data.items():    

        if not valid_color(val['color']):
            validation_report(publication_key, 'color', 'Warning: unknown color')
        
        if not valid_block_height(val['block-height']):
            validation_report(publication_key, 'block-height', 'Warning: bad block height')
        
        if not valid_block_width(val['block-width']):
            validation_report(publication_key, 'block-width', 'Warning: bad block width')
        
        if not valid_cover_height(val['cover-height']):
            validation_report(publication_key, 'cover-height', 'Warning: bad cover height')

        if not valid_cover_width(val['cover-width']):
            validation_report(publication_key, 'cover-width', 'Warning: bad cover width')






