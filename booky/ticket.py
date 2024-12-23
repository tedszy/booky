
"""
Module: ticket

Classes:
    TicketDefinition

Functions:

Constants:

Authors:
    Ted Szylowiec

Notes:

"""

from typing import List, Dict, Union
from tomllib import load, TOMLDecodeError
import fnmatch
from pydantic import BaseModel, ValidationError, Field 
from pydantic import ConfigDict, field_validator
from rich.table import Table
from rich.console import Console
from .config import BOOKY_CONFIG


class TicketDefinition(BaseModel):
    """Class that represents the data defining one ticket.

    A ticket definition object has a publication key and a list of so-called volumes.
    The pub key allows the system to look up the publication that this ticket
    refers to. Volumes are years or collections of years of this particular
    publication. Each volume has a string label (years) and an integer value
    for the thickness of the volume. Volumes are to be bound together into
    one book. Knowing the volume thicknesses and the publication key,
    the application can then calculate all the bookbinding dimensions
    to be printed on the pdf tickets.
    
    We use "Ticket Definition" to refer to the information in the toml
    file which defines the tickets that will be computed and typeset by LaTex.
    "Ticket" will refer to the latex or pdf printed form of the ticket,
    which is the finished product appearing in a ticket booklet.

    Attributes:
        pub_key str: the publication key which is its handle in the Pubs database.
        volumes List[List[str, int]]: a list of pair-lists. Each pair is a volume
                                      label (usually a date or date range) and a 
                                      thickness dimension. This dimension, along
                                      with data looked up in Pubs, is what the final
                                      ticket computations are based on.

    Methods:
        display: prints the ticket to terminal. 

    """
    
    pub_key: str = Field(alias='pub-key')
    volumes: List[List[str | int]]
    
    def display(self):
        """We will use this for debugging."""
        table = Table(title='Ticket definition', show_header=False, box=None)
        table.add_column('',  justify='right', style='white')
        table.add_column('', style='cyan')
        table.add_row('Publication key:', self.pub_key)
        table.add_row('Volumes:', str(self.volumes))
        console = Console()
        print()
        console.print(table)
        print()


class BookletDefinition(BaseModel):
    """Class representing the data defning a booklet of tickets.

    This data comes from the ticket-booklet toml file. There is a dictionary
    of ticket definitions, a filename for the finished tex and pdf files,
    and a list of pages. 

    Pages are lists of lists of strings, each string being a key 
    for a ticket definition. Each sublist defines one page of the booklet.

    Attributes:
        filename
        pages
    
    Methods:
        display()

    """
    
    # ticket_dict: Dict[str, TicketDefinition] = Field(alias='ticket')
    filename: str
    pages: List[List[TicketDefinition]]

    def display(self, pub_db):
        """We will use this for debugging."""

        table = Table(title='Booklet definition', show_header=False, box=None)
       
        table.add_column('', justify='right', style='white bold')
        table.add_column('', justify='left', style='white')
        table.add_column('', style='cyan')
        table.add_row('TeX output:', self.filename)
        table.add_row('Pages:')

        for n,p in enumerate(self.pages):
            for m,t in enumerate(p):
                label = str(n+1) if m==0 else '' 
                table.add_row(label, pub_db[t.pub_key].title, str(t.volumes))
            table.add_row()

        console = Console()
        print()
        console.print(table)
        print()



              
