
# booky2.py


import logging
import os.path
from tomllib import load, TOMLDecodeError
import importlib.metadata
import argparse
import fnmatch

from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from pydantic import ValidationError

from .display import (display_welcome, 
                      display_error, 
                      display_toml_error,
                      display_warning,
                      display_info,
                      display_pubs_narrow,
                      display_pubs_wide)
from .config import CONFIG_FILENAME


_DISTRIBUTION_METADATA = importlib.metadata.metadata('Booky')
version = _DISTRIBUTION_METADATA['Version']

logger = logging.getLogger('booky')
logging.basicConfig(level=logging.DEBUG)


try:
    from .validation import BookyConfig, PubDB, BOOKY_CONFIG
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
    group.add_argument('-l', '--list',
                            help="List keys and titles in the database.",
                            action="store_true")
    group.add_argument('-L', '--list-full',
                            help="List full publication entries.",
                            action="store_true")
    group.add_argument('-c', '--check-key',
                       help="Checks if given key is available (unique).")
    group.add_argument('-s', '--search-keys',
                       help="Wildcard search of publication keys")
    group.add_argument('-S', '--search-titles',
                       help="Wildcard search of publication titles")

    args = parser.parse_args()

    if args.list:
        display_pubs_narrow('Publications', pdb.data)

    elif args.list_full:
        display_pubs_wide('Publications (full data)', pdb.data)
    
    elif args.check_key:
        if args.check_key in pdb.data.keys():
            display_warning(f"Key {args.check_key} already exists in database:\n {args.check_key} {pdb.data[args.check_key].title}")
        else:
            display_info(f"key {args.check_key} is ok!\n No publication uses this key!")

    elif args.search_keys:
        result = {}
        for key in sorted(pdb.data.keys()):
            if fnmatch.fnmatch(key, args.search_keys):
                result[key] = pdb.data[key]
        display_pubs_wide('Search keys result', result)

    elif args.search_titles:
        result = {}
        for key in sorted(pdb.data.keys()):
            if fnmatch.fnmatch(pdb.data[key].title, args.search_titles):
                result[key] = pdb.data[key]
        display_pubs_wide('Search titles result', result)








main()


