
# booky2.py
#
# * CLI check a proposed publication key to see if it's not taken
# * Panel functions for stylized errors.


import logging
import os.path
from tomllib import load, TOMLDecodeError
from rich import print
from rich.panel import Panel
from pydantic import ValidationError

try:
    from .validation import BookyConfig, PubDB, BOOKY_CONFIG
except TOMLDecodeError: 
    print(Panel(str(f"Bad TOML file syntax: {CONFIG_FILENAME}: possibly duplicate key.")))
    exit(1)
except ValidationError as v:
    print(Panel(str(v.errors())))
except FileNotFoundError as f:
    print(Panel(str(f)))
    exit(1)


logger = logging.getLogger('booky')
logging.basicConfig(level=logging.DEBUG)


def main():
    try:

        with open(BOOKY_CONFIG.pub_db_filename, 'rb') as f:
            data = load(f)
            pdb = PubDB.model_validate({'data':data})
    
    except TOMLDecodeError:
        print(Panel(f"Bad TOML file syntax: {booky_config.pub_db_filename}: possibly a duplicate key?"))
        exit(1)
    except ValidationError as v:
        print(Panel(str(v.errors())))
        exit(1)
    except FileNotFoundError as f:
        print(Panel(str(v.errors())))
        exit(1)

    logger.info('Pub database loaded ok.')

    # print(Panel(str(pdb.model_dump(by_alias=True))))
    # print(pdb)

    print("Welcome to Booky 2.0.0")


main()


