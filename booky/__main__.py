
# booky2.py
#
# * CLI check a proposed publication key to see if it's not taken
# * Panel functions for stylized errors.


import logging
import os.path
from tomllib import load, TOMLDecodeError
import importlib.metadata
import argparse

from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from pydantic import ValidationError

from .display import display_welcome, display_error, display_toml_error
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


# Load the publication database.


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

    list_group = parser.add_mutually_exclusive_group()
    list_group.add_argument('-l', '--list',
                            help="List keys and titles in the database.",
                            action="store_true")
    list_group.add_argument('-L', '--list-full',
                            help="List full publication entries.",
                            action="store_true")

    args = parser.parse_args()

    if args.list:
        table = Table(title='Publications')
        table.add_column('Key', justify='right', style='cyan')
        table.add_column('Title', style='white')
        for key in sorted(pdb.data.keys()):
            table.add_row(key, pdb.data[key].title)
        console = Console()
        print()
        console.print(table)
        print()
    elif args.list_full:
        table = Table(title='Publications (full data)', show_lines=True)
        table.add_column('Key', justify='right', style='cyan')
        table.add_column('Title', style='white')
        table.add_column('BH',style='yellow')
        table.add_column('BW',style='yellow')
        table.add_column('CH',style='yellow')
        table.add_column('CW',style='yellow')
        table.add_column('Color',style='yellow')
        for key in sorted(pdb.data.keys()):
            table.add_row(key, 
                          pdb.data[key].title, 
                          str(pdb.data[key].block_height),
                          str(pdb.data[key].block_width),
                          str(pdb.data[key].cover_height),
                          str(pdb.data[key].cover_width),
                          pdb.data[key].color)
        console = Console()
        print()
        console.print(table)
        print()


# table.add_column("Name",justify='right',style='cyan',no_wrap=True)                                    
                                                                                                      









main()


