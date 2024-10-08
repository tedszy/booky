# publication.py

from typing import List, Dict
from tomllib import load, TOMLDecodeError
import fnmatch
from pydantic import BaseModel, ValidationError, Field 
from pydantic import ConfigDict, field_validator
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from .config import BOOKY_CONFIG


# Validate the publication validation constraints 
# specified in the configure.toml file.

# Pub is the class for instances that hold bookbinding 
# data about a single publication.


class Pub(BaseModel):
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


# PubDB is the dictionary of all publications.
# It is loaded from pubs.toml (or the file defined in configure.toml)
# and validated with the above pydantic models.


def sorted_rows(pub_dict):
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

    data: Dict[str, Pub]

    def display_narrow(self):
        # We take only the key and title of each row.
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
        print_wide_table('Publications (full data)', self.data)

    def search_keys(self, search_arg):
        result = {}
        for key in sorted(self.data.keys()):
            if fnmatch.fnmatchcase(key.upper(), search_arg.upper()):
                result[key] = self.data[key]
        print_wide_table("Search keys result", result)

    def search_titles(self, search_arg):
        result = {}
        for key in sorted(self.data.keys()):
            if fnmatch.fnmatchcase(self.data[key].title.upper(), 
                                   search_arg.upper()):
                result[key] = self.data[key]
        print_wide_table('Search titles result', result)




