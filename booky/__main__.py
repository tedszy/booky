"""
Module: __main__

Classes:
    None

Functions:
    main(): entry point of the Booky application.

Constants:
    _DISTRIBUTION_METADATA: python info about the Booky module.
    version: from _DISTRIBUTION_METADATA dictionary.
    logger: logger object. 

Authors:
    Ted Szylowiec

Notes:

"""

import logging
import os.path
from tomllib import load, TOMLDecodeError
import importlib.metadata
import argparse
import pprint

from pydantic import ValidationError

from .messages import (display_welcome, 
                       display_error, 
                       display_toml_error,
                       display_warning,
                       display_info)
from .publication import PubDB
from .ticket import TicketDefinition, Ticket, BookletDefinition

_DISTRIBUTION_METADATA = importlib.metadata.metadata('Booky')
version = _DISTRIBUTION_METADATA['Version']

logger = logging.getLogger('booky')
logging.basicConfig(level=logging.DEBUG)

# Try importing the BOOKY_CONFIG object from 
# the config module.

try:
    from .config import BOOKY_CONFIG
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
    """Entry point for the Booky application.
    
    This function parses command line arguments and takes the 
    specified actions. It first loads the publication database
    into a PubDB instance called pdb. Then it processes the
    command line arguments.

    Successes along the way are logged.

    """

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
                       help=("Search of publication keys." 
                             "If you use a wildcard like *, "
                             "enclose the search term in quotes."))

    group.add_argument('-S', '--search-titles',
                       help=("Search of publication titles. "
                             "If you use a wildcard like * in your search term, "
                             "enclose the term in quotes."))

    group.add_argument('-b', '--make-booklet',
                       help=("Make booklet of tickets from booklet toml file."))
    
    args = parser.parse_args()

    if args.list:
        pdb.display_narrow()

    elif args.list_full:
        pdb.display_wide()
    
    elif args.check_key:
        if args.check_key in pdb.data.keys():
            display_warning((f"Key {args.check_key} already exists in database:\n" 
                             f"{args.check_key} {pdb.data[args.check_key].title}"))
        else:
            display_info(f"key {args.check_key} is ok!\n No publication uses this key!")

    elif args.search_keys:
        pdb.search_keys(args.search_keys)

    elif args.search_titles:
        pdb.search_titles(args.search_titles)

    elif args.config:
        BOOKY_CONFIG.display()

    elif args.make_booklet:
        try:
            with open(args.make_booklet, 'rb') as f:

                data = load(f)

                # Construct a dictionary from which we can model_validate
                # and create the pydantic derived BookletDevinition.
                # as it is, 'data' straight from the tickets toml file
                # is not exactly in the shape we want,
                #
                #  {'filename' : filename,
                #   'pages' : [[t1_instance, t2_instance, ...],
                #             [t5_instance, t6_instance, ...],
                #              ...]}
                #
                # Notice that we have discarded the 't1', 't2' etc labels.
                # We dont need them now that we have the objects themselves
                # in the pages array.

                ticket_instances_dict = {k:TicketDefinition.model_validate(v) 
                                         for k,v in data['ticket'].items()}

                # We no longer need the ticket names for the construction
                # of the booklet instance.

                booklet_dict = {'filename': data['booklet']['filename'],
                                'pages': [[ticket_instances_dict[u] for u in page]
                                         for page in data['booklet']['pages']]}
                                
                bd = BookletDefinition.model_validate(booklet_dict)

                # We must pass in pdb.data so that display can look up
                # the titles when making a nice table.

                bd.display(pdb.data)

                print()
                pprint.pprint(vars(Ticket(pdb.data, bd.pages[0][4])))
                
        except TOMLDecodeError:
            display_toml_error(args.make_tickets)
            exit(1)
        except ValidationError as v:
            display_error(v.errors())
            exit(1)
        except FileNotFoundError as ff:
            display_error(str(ff))
            exit(1)



            


                             
    else:
        parser.print_help()



main()


