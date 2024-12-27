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
        self.cardboard_label = booky_config.ticket_layout.cardboard_label
        self.paper_label = booky_config.ticket_layout.paper_label
        self.buckram_label = booky_config.ticket_layout.buckram_label
        self.backcard_label = booky_config.ticket_layout.backcard_label
        
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
        
        self.volumes = [ {'volume_label': vol[0],
                          'cardboard_height': self.cover_height, 
                          'cardboard_width': self.cover_width,
                          'paper_height': self.cover_height + 30,
                          'paper_width': vol[1] + 50 + 2*self.cover_width,
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
        """H and W header labels on the multicolumns.
        For 4-volume ticket, it should look like this:

        & & H & W & & H & W & & H & W & & H & W\\
        
        """
        result = ""
        for k in range(self.number_of_volumes):
            result += " & & H & W"
        result += "\\\\\n"
        return result

    def latex_body_cline(self):
        """Column lines separating rows in the body of the ticket table.
        For example, ticket with 4 volumes:

        \cline{2-2}\cline{3-4}\cline{6-7}\cline{9-10}\cline{12-13}

        """
        result = "\\cline{2-2}"
        for k in range(self.number_of_volumes):
            result += f"\\cline{{{3*(k+1)}-{3*(k+1)+1}}}"
        result += "\n"
        return result

    # Computed bookbinding elements.
    
    def latex_cardboard_row(self):
        """Example, for a 4-volume ticket:

        & carton  & 241 & 144 & & 241 & 144 & & 241 & 144 & & 241 & 144 \\

        Here we have a user-set french label (carton) for the cardboard row label.

        """

        result = f"& {self.cardboard_label}"
        for k,vol in enumerate(self.volumes):
            result += f" & {vol['cardboard_height']} & {vol['cardboard_width']} &"
        # Strip off the last &
        result = result[0:-1]
        result += "\\\\\n"
        return result
                
    
    def latex_paper_row(self):
        """Example, for a 4-volume ticket:

        & papier  & 271 & 378 & & 271 & 378 & & 271 & 372 & & 271 & 379 \\
        
        It's constructed almost the same as cardboard row.
        All these data rows are very similar.

        """

        result = f"& {self.paper_label}"
        for k,vol in enumerate(self.volumes):
            result += f" & {vol['paper_height']} & {vol['paper_width']} &"
        # Strip off the last &
        result = result[0:-1]
        result += "\\\\\n"
        return result
    
    def latex_buckram_row(self):
        """Example with 4-volume ticket:

        & buckram  & 281 & 140 & & 281 & 140 & & 281 & 134 & & 281 & 141 \\
        
        """
        result = f"& {self.buckram_label}"
        for k,vol in enumerate(self.volumes):
            result += f" & {vol['buckram_height']} & {vol['buckram_width']} &"
        # Strip off the last &
        result = result[0:-1]
        result += "\\\\\n"
        return result

    def latex_backcard_row(self):
        """Example, for a 4-volume ticket:

        & carte-a-dos  & 241 & 40 & & 241 & 40 & & 241 & 34 & & 241 & 41 \\

        Here the user has supplied his own label "carte-a-dos" for the backcard.

        """
        result = f"& {self.backcard_label}"
        for k,vol in enumerate(self.volumes):
            result += f" & {vol['backcard_height']} & {vol['backcard_width']} &"
        # Strip off the last &
        result = result[0:-1]
        result += "\\\\\n"
        return result
    
    def latex_ticket(self):
        """Latex code for entire ticket-table."""
        
        result = self.latex_table_begin()
        result += self.latex_multirow_spec()
        result += self.latex_header_cline()
        result += self.latex_header_HW()
        result += self.latex_cardboard_row()
        result += self.latex_body_cline()
        result += self.latex_paper_row()
        result += self.latex_body_cline()
        result += self.latex_buckram_row()
        result += self.latex_body_cline()
        result += self.latex_backcard_row()
        result += self.latex_body_cline()
        result += self.latex_table_end()
        return result


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
        self.ticket_spacing = booky_config.ticket_layout.ticket_spacing
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
        print(ticket.latex_ticket())
        print(self.latex_end())

    def write_latex(self):
        """Generate all latex for the complete booklet and write it to file."""
        
        between_tickets = f"\n\\vskip {self.ticket_spacing}mm\n\n"
        between_pages = "\n\\vfill\\newpage\n"
        result = []
        result.append(self.latex_begin())
        for page in self.pages:
            for ticket in page:
                result.append(ticket.latex_ticket())
                result.append(between_tickets)
            result.append(between_pages)

        # chop off the last between_tickets string.
        # Then join everything together and write to file.

        result = result[0:-1]
        result.append(self.latex_end())
        with open(self.filename + '.tex', 'w') as f:
            f.write("".join(result))
                


# (define (write-to-tex-file filename tickets)
#   (call-with-output-file filename #:exists 'replace
#     (lambda (out)
#       (display
#        (doc-setup
#         (string-join
#          (map (lambda (my-ticket)
#                 (if (eqv? my-ticket 'newpage)
#                     (format "\n\\vfill\\newpage\n")
#                     (table-setup
#                      (column-args (length (ticket-volume-data-list my-ticket)))
#                      (table-body (ticket-title my-ticket)
#                                  (ticket-color my-ticket)
#                                  (ticket-volume-data-list my-ticket)))))
#               tickets)
#          (format "\n\\vskip ~amm\n\n" (ticket-spacing))))
#        out))))



    
