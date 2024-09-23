
# booky2.py
#
# * CLI check a proposed publication key to see if it's not taken
# * Panel functions for stylized errors.


import logging
import os.path
from tomllib import load, TOMLDecodeError
import importlib.metadata
from rich import print
from rich.panel import Panel
from pydantic import ValidationError
from .display import display_welcome, display_error, display_toml_error
from .config import CONFIG_FILENAME


_DISTRIBUTION_METADATA = importlib.metadata.metadata('Booky')
version = _DISTRIBUTION_METADATA['Version']


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


logger = logging.getLogger('booky')
logging.basicConfig(level=logging.DEBUG)


# Load the publication database.


def main():
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


main()


