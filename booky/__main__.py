
# booky2.py


import logging
import os.path
from tomllib import load, TOMLDecodeError
import importlib.metadata
import argparse

from pydantic import ValidationError

from .messages import (display_welcome, 
                       display_error, 
                       display_toml_error,
                       display_warning,
                       display_info)
from .publication import PubDB

_DISTRIBUTION_METADATA = importlib.metadata.metadata('Booky')
version = _DISTRIBUTION_METADATA['Version']

logger = logging.getLogger('booky')
logging.basicConfig(level=logging.DEBUG)


try:
    from .config import BOOKY_CONFIG
    # from .config import BookyConfig, BOOKY_CONFIG
except TOMLDecodeError: 
    display_toml_error(CONFIG_FILENAME)
    exit(1)
except ValidationError as v:
    display_error(v.errors())
    exit(1)
except FileNotFoundError as f:
    display_error(str(f))
    exit(1)

logger.info('BOOKY_CONFIG instance ok')


def main():

    # Load the publications database into pbd.
    # Pdb is an object holding a dict of Pub objects keyed by their
    # unique identifier code.

    try:
        with open(BOOKY_CONFIG.pub_db_filename, 'rb') as f:
            data = load(f)
            pdb = PubDB.model_validate({'data':data})
    except TOMLDecodeError:
        display_toml_error(BOOKY_CONFIG.pub_db_filename)
        exit(1)
    except ValidationError as v:
        display_error(v.errors())
        exit(1)
    except FileNotFoundError as f:
        display_error(str(f))
        exit(1)

    logger.info('Pub database loaded ok.')
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
                       help="Checks if given key is available (unique).")

    group.add_argument('-s', '--search-keys',
                       help="Search of publication keys. If you use a wildcard like *, enclose the search term in double quotes """)

    group.add_argument('-S', '--search-titles',
                       help="Search of publication titles. If you use a wildcard like * in your search term, enclose the term in double quotes.")

    args = parser.parse_args()

    if args.list:
        pdb.display_narrow()

    elif args.list_full:
        pdb.display_wide()
    
    elif args.check_key:
        if args.check_key in pdb.data.keys():
            display_warning(f"Key {args.check_key} already exists in database:\n {args.check_key} {pdb.data[args.check_key].title}")
        else:
            display_info(f"key {args.check_key} is ok!\n No publication uses this key!")

    elif args.search_keys:
        pdb.search_keys(args.search_keys)

    elif args.search_titles:
        pdb.search_titles(args.search_titles)

    elif args.config:
        BOOKY_CONFIG.display()

    else:
        parser.print_help()





main()


