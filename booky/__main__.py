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


# Try importing the BOOKY_CONFIG object from 
# the config module.

# try:
#     from .config import BOOKY_CONFIG
# except TOMLDecodeError: 
#     display_toml_error(CONFIG_FILENAME)
#     exit(1)
# except ValidationError as v:
#     display_error(v.errors())
#     exit(1)
# except FileNotFoundError as f:
#     display_error(str(f))
#     exit(1)

# logger.info('BOOKY_CONFIG instance ok')


def main():
    """Entry point for the Booky application.
    
    This function parses command line arguments and takes the 
    specified actions. It first loads the publication database
    into a PubDB instance called pdb. Then it processes the
    command line arguments.

    Successes along the way are logged.

    """

    # try:
    #     with open(BOOKY_CONFIG.pub_db_filename, 'rb') as f:
    #         data = load(f)
    #         pdb = PubDB.model_validate({'data':data})
    # except TOMLDecodeError:
    #     display_toml_error(BOOKY_CONFIG.pub_db_filename)
    #     exit(1)
    # except ValidationError as v:
    #     display_error(v.errors())
    #     exit(1)
    # except FileNotFoundError as f:
    #     display_error(str(f))
    #     exit(1)

    # logger.info('Pub database loaded ok.')

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
            



        
# =====================================================================    
        
            
    elif args.xmake_booklet:
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

                booklet_dict = {'filename': pathlib.Path(args.make_booklet).stem + '.tex',
                                'pages': [[ticket_instances_dict[u] for u in page]
                                         for page in data['booklet']['pages']]}
                
                bd = BookletDefinition.model_validate(booklet_dict)
                booklet = Booklet(BOOKY_CONFIG, pdb.data, bd)
                booklet.write_latex()
                logger.info(f"latex output to {bd.filename + '.tex.'}")

                if platform.system() == 'Darwin':
                    os.system("/Library/TeX/texbin/pdflatex " + bd.filename + '.tex')
                else:
                    os.system("pdflatex " + bd.filename + '.tex')
                logger.info(f"build pdf {bd.filename + '.pdf.'}") 
                
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


