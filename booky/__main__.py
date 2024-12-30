### __main__.py


import logging
import os.path
from tomllib import load, TOMLDecodeError
import importlib.metadata
import argparse
import pprint
import platform
import os
import pathlib

from pydantic import ValidationError

from .messages import (display_welcome, 
                       display_error, 
                       display_toml_error,
                       display_warning,
                       display_info)
from .publication import (PubDB,
                          load_pubdb,
                          display_pubdb_narrow,
                          display_pubdb_wide,
                          search_keys_pubdb,
                          search_titles_pubdb)
from .ticket import (TicketDefinition,
                     Ticket,
                     BookletDefinition,
                     Booklet,
                     load_booklet,
                     preview_booklet,
                     augment_booklet,
                     latex_write)


from .config import load_config, display_config


_DISTRIBUTION_METADATA = importlib.metadata.metadata('Booky')
version = _DISTRIBUTION_METADATA['Version']

logger = logging.getLogger('booky')
logging.basicConfig(level=logging.DEBUG)

CONFIG_FILENAME = "configure.toml"


def get_config():
    config_dict = load_config(CONFIG_FILENAME)
    pdb = load_pubdb(config_dict['pub-db-filename'])
    return config_dict


def get_pubdb():
    config_dict = load_config(CONFIG_FILENAME)
    pdb = load_pubdb(config_dict['pub-db-filename'])
    return (config_dict, pdb)


def main():
    display_welcome(version)

    parser = argparse.ArgumentParser(
            description='Booky command-line tool.',
            epilog='Choose an option.')

    group = parser.add_mutually_exclusive_group()
    
    group.add_argument('-g', '--config',
                       help="Show Booky configuration parameters.",
                       action="store_true")

    group.add_argument('-l', '--list',
                       help="List keys and titles in the database.",
                       action="store_true")

    group.add_argument('-L', '--list-full',
                       help="List full publication entries.",
                       action="store_true")
    
    group.add_argument('-c', '--check-key',
                       help="Checks if given key is available (unique).",
                       action='store',
                       metavar='')

    group.add_argument('-s', '--search-keys',
                       help=("Search of publication keys." 
                             "If you use a wildcard like *, "
                             "enclose the search term in quotes."),
                       action='store',
                       metavar='')

    group.add_argument('-S', '--search-titles',
                       help=("Search of publication titles. "
                             "If you use a wildcard like * in your search term, "
                             "enclose the term in quotes."),
                       action='store',
                       metavar='')

    group.add_argument('-b', '--preview-booklet',
                       help=("Preview booklet onto terminal display."),
                       action='store',
                       metavar='')

    group.add_argument('-B', '--make-booklet',
                       help=("Make tex booklet and build pdf."),
                       action='store',
                       metavar='')

    args = parser.parse_args()

    if args.config:
        config_dict = get_config()
        display_config(CONFIG_FILENAME, config_dict)
    
    elif args.list:
        config_dict, pdb = get_pubdb()
        display_pubdb_narrow('Publications', pdb)

    elif args.list_full:
        cd, pdb = get_pubdb()
        display_pubdb_wide('Publications (full)', pdb)

    elif args.search_keys:
        cd, pdb = get_pubdb()
        result = search_keys_pubdb(args.search_keys, pdb)
        display_pubdb_wide("Search keys result", result)

    elif args.search_titles:
        cd, pdb = get_pubdb()
        result = search_titles_pubdb(args.search_titles, pdb)
        display_pubdb_wide("Search titles result", result)
        
    elif args.check_key:
        cd, pdb = get_pubdb()
        if args.check_key in pdb.keys():
            display_warning((f"Key {args.check_key} already exists in pub database:\n" 
                             f"{args.check_key}... {pdb[args.check_key]['title']}"))
        else:
            display_info(f"Key {args.check_key} is ok!\n"
                          "No publication uses this key!")

    elif args.preview_booklet:
        cd, pdb = get_pubdb()
        bd = load_booklet(args.preview_booklet)
        preview_booklet(args.preview_booklet, pdb, bd)

    elif args.make_booklet:
        cd, pdb = get_pubdb()
        bd = load_booklet(args.make_booklet)
        output_filename = pathlib.Path(args.make_booklet).stem + '.tex'
        ab = augment_booklet(cd, pdb, bd, output_filename)
        latex_write(ab)
        if platform.system() == 'Darwin':
            os.system("/Library/TeX/texbin/pdflatex " + ab['output-filename'])
        else:
            os.system("pdflatex " + ab['output-filename'])    
                             
    else:
        parser.print_help()


main()


