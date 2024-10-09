"""
Module: publication

Classes:
    Pub: single publication instances. The attributes are
         verified by Pydantic field validators.
    PubDB: Publications database.

Functions:
    sorted_rows(pub_dict): returns a sorted list of tuples 
                           for table building.
    print_wide_table(title, data_dict): pass in a dict keyed by
                                        publication keys and it formats
                                        them into a table. Used several 
                                        times here to reduce code duplication.

Constants:
    None.

Authors:
    Ted Szylowiec

Notes:
    

"""

from typing import List, Dict
from tomllib import load, TOMLDecodeError
import fnmatch
from pydantic import BaseModel, ValidationError, Field 
from pydantic import ConfigDict, field_validator
from rich.table import Table
from rich.console import Console
from .config import BOOKY_CONFIG


class Pub(BaseModel):
    """Class that represents one publication.
    
    The bookbinding data and title is held in Pub objects.
    These attributes are validated with Pydandic field validators.

    Attributes:
        block_height int: bookbinding dimension specific 
                          to the publication.
        block_width int:  ditto.
        cover_height int: ditto.
        cover_width int:  ditto.
        color string: ditto

    Methods:
        None.

    """
    title: str
    block_height: int = Field(alias='block-height')
    block_width: int = Field(alias='block-width')
    cover_height: int = Field(alias='cover-height')
    cover_width: int = Field(alias='cover-width')
    color: str

    @field_validator('color')
    @classmethod
    def valid_color(cls, color):
        if not BOOKY_CONFIG.good_color(color):
            raise ValueError(f'Bad color: {color}')
        else:
            return color

    @field_validator('block_height')
    @classmethod
    def valid_block_height(cls, block_height):
        if not BOOKY_CONFIG.good_block_height(block_height):
            raise ValueError((f'Bad block_height: '
                              f'{block_height}, limits: ' 
                              f'{BOOKY_CONFIG.pub_validation.block_limits}'))
        else:
            return block_height

    @field_validator('block_width')
    @classmethod
    def valid_block_width(cls, block_width):
        if not BOOKY_CONFIG.good_block_width(block_width):
            raise ValueError((f'Bad block_width: '
                              f'{block_width}, limits: '
                              f'{BOOKY_CONFIG.pub_validation.block_limits}'))
        else:
            return block_width

    @field_validator('cover_height')
    @classmethod
    def valid_cover_height(cls, cover_height):
        if not BOOKY_CONFIG.good_cover_height(cover_height):
            raise ValueError((f'Bad cover_height: '
                              f'{cover_height}, limits: '
                              f'{BOOKY_CONFIG.pub_validation.cover_limits}'))
        else:
            return cover_height

    @field_validator('cover_width')
    @classmethod
    def valid_cover_width(cls, cover_width):
        if not BOOKY_CONFIG.good_cover_width(cover_width):
            raise ValueError((f'Bad cover_width: '
                              f'{cover_width}, limits: '
                              f'{BOOKY_CONFIG.pub_validation.cover_limits}'))
        else:
            return cover_width


def sorted_rows(pub_dict):
    """Sorts a dictionary of Pub instances and changes them into a list of rows.
   
    To build tables with Rich, we need lists of tuples representing the rows.
    This function sorts a dictionary of Pub instances by keys, and then
    reduces the attribute data of each Pub intance into a row.

    Args:
        pub_dict: dictionary of Pub instances, keyed by the publication key code.

    Returns:
        sorted rows of tuples of publication bookbinding data.

    Notes: 

    """
    result = []
    for key in sorted(pub_dict.keys()):
        result.append((key, 
                        pub_dict[key].title,
                        str(pub_dict[key].block_height),
                        str(pub_dict[key].block_width),
                        str(pub_dict[key].cover_height),
                        str(pub_dict[key].cover_width),
                        pub_dict[key].color))
    return result


def print_wide_table(title, data_dict):
    """Prints a table of Pub dictionary entries, sorted by keys.

    The dict of Pub instances could be the whole in-memory publication
    database or it could be the result of key or title searches.
    The data_dict is reduced to sorted rows and the passed to
    Rich for printing as a nice looking table. The format is "wide"
    in the sense that all the Publication bookbinding parameters
    are displayed in the columns.

    Args:
        title string: the title you want for the table.
        data_dict: dictionary of Pub instances.

    Returns:
        sorted rows of tuples of publication bookbinding data.

    Notes: 

    """
    data_color = 'white'
    table = Table(title=title, show_lines=True)
    table.add_column('Key', justify='right', style='bold magenta')
    table.add_column('Title', style='white')
    table.add_column('BH',style=data_color)
    table.add_column('BW',style=data_color)
    table.add_column('CH',style=data_color)
    table.add_column('CW',style=data_color)
    table.add_column('Color',style=data_color)
    for row in sorted_rows(data_dict):
        table.add_row(*row)
    console = Console()
    print()
    console.print(table)
    print()


class PubDB(BaseModel):
    """Class that represents the in-memory database of publications.
   
    The entries of the publication toml file are transformed into Pub instances
    and these instances are put into a dictionary keyed by the mnemonic code 
    (usually referred to as "the key".) The mnemonic code acts as a handle
    to get at all the publication's bookbinding parameters.

    this dictionary is the main in-memory database which is further
    processed or searced invarious way. Ticket computations look up
    publication keys in this database.

    Attributes:
        data: dictionary of Pub instances, keyed by the mnemonic key code.

    Methods:
        display_narrow(): compact display of publication database contents.
        display_wide(): table of database entries with full data.
        search_keys(arg): search database by key.
        search_titles(arg): search by title.

    """
    data: Dict[str, Pub]

    def display_narrow(self):
        """Print compact table: only the key and the publication title."""
        key_style = 'bold magenta'
        title_style = 'white'
        table = Table(title='Publications')
        table.add_column('Key', justify='right', style=key_style)
        table.add_column('Title', style=title_style)
        for row in sorted_rows(self.data):
            table.add_row(row[0], row[1])
        console = Console()
        print()
        console.print(table)
        print()

    def display_wide(self):
        """Display full publication table with all parameters."""
        print_wide_table('Publications (full data)', self.data)

    def search_keys(self, search_arg):
        """Search the database by key or part of key. 

        Args:
            search_arg string: accepts globbing characters * and ?.

        """
        result = {}
        for key in sorted(self.data.keys()):
            if fnmatch.fnmatchcase(key.upper(), search_arg.upper()):
                result[key] = self.data[key]
        print_wide_table("Search keys result", result)

    def search_titles(self, search_arg):
        """Search the database by title or part of title. 

        Args:
            search_arg string: accepts globbing characters * and ?.

        """
        result = {}
        for key in sorted(self.data.keys()):
            if fnmatch.fnmatchcase(self.data[key].title.upper(), 
                                   search_arg.upper()):
                result[key] = self.data[key]
        print_wide_table('Search titles result', result)




