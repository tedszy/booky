"""
Module: ticket

    Definitions necessary to create a booklet of tickets.
    Bookbinding calculations, tex output and pdf building.

    We use "Ticket Definition" to refer to the information in the toml
    file which defines the tickets that will be computed and typeset by LaTex.

    Instances of "Booklet Definition" contain what is needed to compute
    and typeset a final boolet of tickets. 

    The Booklet class does the heavy lifting of bookbinding computations
    and LaTeX generation. A Booklet instance depends on a Booklet Definition,
    a BookyConfig instance and a PubDB instance. 

Classes:
    TicketDefinition
    BookletDefinition
    Booklet

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
    publication. Each volume has a string label (usually years) and an integer value
    for the thickness of the volume. Volumes are to be bound together into
    one book. Knowing the volume thicknesses and the publication key,
    Booky can then calculate all the bookbinding dimensions to be printed 
    on the pdf tickets.
    
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

        
class Ticket:
    """Computes a ticket from ticket definition, booky_config and pub db.
    Everything that we need to create the latex code for one ticket is here."""

    def __init__(self, booky_config, pub_db, ticket_definition):
        pk = ticket_definition.pub_key
        self.title = pub_db[pk].title
        self.color = pub_db[pk].color
        self.cover_height = pub_db[pk].cover_height
        self.cover_width = pub_db[pk].cover_width
        self.label_width = booky_config.ticket_layout.label_width
        self.volume_separation = booky_config.ticket_layout.volume_separation
        self.vertical_stretch = booky_config.ticket_layout.vertical_stretch
        self.title_width = booky_config.ticket_layout.title_width
        self.title_styling = booky_config.ticket_layout.title_styling
        
        # a volume is of the form
        #
        #    [vol[0], vol[1]] = [volume_label, backcard_width]
        #
        # volumes are then [[volume_label, backcard_width], ... ]]
        #
        # In booky1, 'volume_label' was called 'edition'.
        #
        # Here, unlike booky1, we have factored out computations
        # that do not depend on the volume backcard_width.
        
        self.volumes = [ {'volume_label':vol[0],
                          'paper_height': self.cover_height + 30,
                          'paper-width': vol[1] + 50 + 2*self.cover_width,
                          'buckram_height': self.cover_height + 40,
                          'buckram_width': vol[1] + 100,
                          'backcard_height': self.cover_height,
                          'backcard_width': vol[1]
                          } for vol in ticket_definition.volumes]
        self.number_of_volumes = len(self.volumes)
        

    def latex_table_begin(self):
        """A ticket latex table depends on the number of volumes.
        Here is the beginning fragment of a table for a 4-volume ticket.

        {\renewcommand{\arraystretch}{1.2}
        \begin{tabular}{|c|p{18mm}|c|c|p{0mm}|c|c|p{0mm}|c|c|p{0mm}|c|c|}
        \hline

        We need the arraystretch line and then the argument to the begin{tabular}
        environment. This argument consists of 4 segments of column-specification codes."""

        columns_spec = f"|c|p{{{self.label_width}mm}}|"
        for k in range(self.number_of_volumes - 1):
            columns_spec += f"c|c|p{{{self.volume_separation}mm}}|"
        columns_spec += "c|c|"
        result = f"{{\\renewcommand{{\\arraystretch}}{{{self.vertical_stretch}}}\n"
        result += f"\\begin{{tabular}}{{{columns_spec}}}\n"
        result += "\\hline\n"
        return result
        
    def latex_table_end(self):
        """Ticket latex table ending fragment."""

        return "\\hline\n\\end{tabular}}\n"

    def latex_multirow_spec(self):
        """The multirow-multicolumn specification line. 
        This depends on the number of volumes in the ticket.
        Here is an example for a 4-volume ticket:

        \multirow{6}{26mm}{\large Etudes}& \multirow{2}{*}{\Large 320} &\multicolumn{2}{c|}{2020-1} 
        & & \multicolumn{2}{c|}{2020-2} & & \multicolumn{2}{c|}{2021-1} & & \multicolumn{2}{c|}{2021-2} \\

        """

        result = f"\\multirow{{6}}{{{self.title_width}mm}}{{{self.title_styling} {self.title}}}"
        result += f" & \\multirow{{2}}{{*}}{{\\Large {self.color}}} &"

        # Iterate over the editions, aka volume labels.

        for k,vol in enumerate(self.volumes):
            result += f"\\multicolumn{{2}}{{c|}}{{{vol['volume_label']}}}"
            if k != self.number_of_volumes - 1:
                result += " & & "
        result += " \\\\\n"
        return result

    def latex_header_cline(self):
        """There are the column lines in the header, and the column lines in the
        table body. These are the specifications for the header clines (column-lines).

        For example, a 4-volume ticket:

        \cline{3-4}\cline{6-7}\cline{9-10}\cline{12-13}

        """

        result = ""
        for k in range(self.number_of_volumes):
            result += f"\\cline{{{3*(k + 1)}-{3*(k + 1) + 1}}}"
        result += "\n"
        return result

        
    def latex_header_HW(self):
        """H and W header labels on the multicolumns."""
        pass
        
        
        


    







    
    
    
    def latex_ticket_body(self):
        """Latex code for the ticket which goes into the tabular environment."""
        pass


   


    

    






   

        

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

        
class Booklet:
    """All the data needed to create a latex/pdf booklet is collected
    and organized in this class."""

    def __init__(self, booky_config, pub_db, booklet_definition):
        self.filename = booklet_definition.filename
        self.font_size = booky_config.ticket_layout.font_size
        self.left_margin = booky_config.ticket_layout.left_margin
        self.right_margin = booky_config.ticket_layout.right_margin
        self.upper_margin = booky_config.ticket_layout.upper_margin
        self.lower_margin = booky_config.ticket_layout.lower_margin
        self.pages = [[Ticket(booky_config, pub_db, td)
                       for td in page] for page in booklet_definition.pages]
        
    def latex_begin(self):
        return "\n".join([
            f"\\documentclass[{self.font_size}pt,a4paper]{{memoir}}",
            f"\\setlrmarginsandblock{{{self.left_margin}mm}}{{{self.right_margin}mm}}{{*}}",
            f"\\setulmarginsandblock{{{self.upper_margin}mm}}{{{self.lower_margin}mm}}{{*}}",
            "\\fixthelayout",
            "\\renewcommand{\\familydefault}{\\sfdefault}",
            "\\usepackage{multirow}",
            " ",
            "\\begin{document}",
            " "])

    def latex_end(self):
        return "\n\n\\vfill\n\\end{document}\n"



    


    
        
    def display_latex(self):
        """For debugging."""

        ticket = self.pages[0][4]
        
        print(self.latex_begin())

        print(ticket.latex_table_begin())
        print(ticket.latex_multirow_spec())
        print(ticket.latex_header_cline())
        
        print()
        print("foo")

        print(ticket.latex_table_end())
        
        print(self.latex_end())

        

    def write_latex(self):
        """Generate all latex for the complete booklet and write it to file."""
        
        ticket = self.pages[0][4]
        
        with open(self.filename + '.tex', 'w') as f:
            f.write(self.latex_begin())
            f.write(ticket.latex_table_begin())
            f.write(ticket.latex_multirow_spec())
            f.write(ticket.latex_header_cline())
            f.write('foo\\\\\n')
            f.write(ticket.latex_table_end())
            f.write(self.latex_end())



    
