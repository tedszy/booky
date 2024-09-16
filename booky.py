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
import logging
import os.path
from tabulate import tabulate


logger = logging.getLogger('booky')
logging.basicConfig(level=logging.DEBUG)


class BadKey(Exception):
    pass


class MissingKey(Exception):
    pass


class BadDBFilename(Exception):
    pass


class ConfigurationValidator:
    '''Loads configuration settings into an instance.'''
    
    config_filename = 'configure.toml'
    toplevel_keys = ['database-filenames', 'validation']
    validation_keys = ['block-limits', 'cover-limits', 'colors'] 

    def __init__(self):

        # Handle possible missing or corrupt toml file with try... except.
        with open('configure.toml', 'rb') as f:
            data = tomllib.load(f)

        logger.debug(f"{self.config_filename} data loaded.")

        # Check config data keys before proceeding.
        
        # Toplevel keys.
        for k in data:
            if k not in self.toplevel_keys:
                raise BadKey(f"bad toplevel key: '{k}'.")
        for k in self.toplevel_keys:
            if k not in data:
                raise MissingKey(f"missing toplevel key: '{k}'.")

        # Validation keys.
        for k in data['validation']:
            if k not in self.validation_keys:
                raise BadKey(f"bad validation key: '{k}'.")
        for k in self.validation_keys:
            if k not in data['validation']:
                raise MissingKey(f"missing validation key: '{k}'.")

        logging.debug(f"{self.config_filename} keys are OK.")

        # Check that publication database files exist.
        for filename in data['database-filenames']:
            if not os.path.isfile(filename):
                raise BadDBFilename(f"database file '{filename}' isn't in pwd.")

        # Check that colors are all 3-character numeric strings.
        if all(isinstance(c, str) and len(c)==3 for c in data['validation']['colors']):
            logging.debug(f"{self.config_filename} colors are OK.")
        else:
            raise ValueError(f"bad color value in {self.config_filename}.")

        # Check that block-limits and cover-limits 
        # are lists of two integers [a,b] with a < b.
        u = data['validation']['block-limits']
        if len(u)==2 and isinstance(u[0],int) and isinstance(u[1],int) and u[0]<u[1]:
            logging.debug(f"{self.config_filename} block-limits are OK.")
        else:
            raise ValueError(f"bad block-limits in {self.config_filename}.")
        u = data['validation']['cover-limits']
        if len(u)==2 and isinstance(u[0],int) and isinstance(u[1],int) and u[0]<u[1]:
            logging.debug(f"{self.config_filename} cover-limits are OK.")
        else:
            raise ValueError(f"bad cover-limits in {self.config_filename}.")

        self.pub_db_filenames = data['database-filenames']
        self.valid_colors = data['validation']['colors']
        self.block_limits = data['validation']['block-limits']
        self.cover_limits = data['validation']['cover-limits']


class Publication:
    '''Each instance holds the bookbinding specs of a publication db entry.'''
    
    def __init__(self, data):
        self.title = data['title']
        self.block_height = data['block-height']
        self.block_width = data['block-width']
        self.cover_heigth = data['cover-height']
        self.cover_width = data['cover-width']
        self.color = data['color']


class PublicationValidator(ConfigurationValidator):
    '''Validate contents of publication database files.
    Walk through each publication and check the sanity of the 
    values in the data fields.'''

    unique_keys = []

    def __init__(self):
        super().__init__()
















# ----------------------------------------------------------------------

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
#    warning = {'color':False, 'block-height':False,
#               'block-width':False, 'cover-height':False,
#               'cover-width':False}
#    for publication_key, val in publication_data.items():    
#
#        if not valid_color(val['color']):
#            validation_report(publication_key, 'color', 'Warning: unknown color')
#            warning['color'] = True
#        
#        if not valid_block_height(val['block-height']):
#            validation_report(publication_key, 'block-height', 'Warning: bad block height')
#            warning['block-height'] = True
#        
#        if not valid_block_width(val['block-width']):
#            validation_report(publication_key, 'block-width', 'Warning: bad block width')
#            warning['block-width'] = True
#        
#        if not valid_cover_height(val['cover-height']):
#            validation_report(publication_key, 'cover-height', 'Warning: bad cover height')
#            warning['cover-height'] = True
#
#        if not valid_cover_width(val['cover-width']):
#            validation_report(publication_key, 'cover-width', 'Warning: bad cover width')
#            warning['cover-width'] = True
#
#    if not warning['color']: print('colors ok.')
#    if not warning['block-height']: print('block heights ok.')
#    if not warning['block-width']: print('block widths ok.')
#    if not warning['cover-height']: print('cover heights ok.')
#    if not warning['cover-width']: print('cover widths ok.')

    my = PublicationValidator()



