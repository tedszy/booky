### ticket.py

import logging
import fnmatch
import tomllib
import rich.table, rich.console
import booky.messages

logger = logging.getLogger('booky')
logging.basicConfig(level=logging.DEBUG)


def load_booklet(booklet_filename):
    """Load booklet toml into booklet_dict and verify it."""
    
    try:
        with open(booklet_filename, 'rb') as f:
            booklet_dict = tomllib.load(f)
    except tomllib.TOMLDecodeError: 
        booky.messages.display_toml_error(config_filename)
        exit(1)
    except FileNotFoundError as f:
        booky.messages.display_error(str(f))
        exit(1)

    logger.info('booklet_dict loaded.')

    # Verify that the config_dict keys are what we expect.
    
    try:

        # To do: type and value checks for booklet data.
        
        pass
    
    except KeyError as v: 
        booky.messages.display_error(v)
        exit(1)
    except ValueError as v:
        booky.messages.display_error(v)
        exit(1)

    return booklet_dict


def preview_booklet(booklet_filename, pubdb_dict, booklet_dict):
    table = rich.table.Table(title='Booklet definition', show_header=False, box=None)
    table.add_column('', justify='right', style='white bold')
    table.add_column('', justify='left', style='white')
    table.add_column('', style='cyan')
    table.add_row('TOML file:', booklet_filename)
    table.add_row('Pages:')
    
    for n,page in enumerate(booklet_dict['booklet']['pages']):
        for m,t in enumerate(page):
            label = str(n+1) if m==0 else ''
            pub_key = booklet_dict['ticket'][t]['pub-key']
            volumes = booklet_dict['ticket'][t]['volumes']
            table.add_row(label, pubdb_dict[pub_key]['title'], str(volumes))
        table.add_row()

    console = rich.console.Console()
    print()
    console.print(table)
    print()

    
def augment_booklet(config_dict, pubdb_dict, booklet_dict, output_filename):
    """Creates a dictionary containing the complete data needed to typeset
    a booklet of tickets. The ticket parameters are computed here."""

    def compute_ticket_parameters(ticket_dict):
        key = ticket_dict['pub-key']
        cover_height = pubdb_dict[key]['cover-height']
        cover_width = pubdb_dict[key]['cover-width']
        result = {'pub-key': key,
                  'title': pubdb_dict[key]['title'],
                  'color': pubdb_dict[key]['color'],
                  'volumes': [{'volume-label': vol[0],
                               'cardboard-height': cover_height, 
                               'cardboard-width': cover_width,
                               'paper-height': cover_height + 30,
                               'paper-width': vol[1] + 50 + 2*cover_width,
                               'buckram-height': cover_height + 40,
                               'buckram-width': vol[1] + 100,
                               'backcard-height': cover_height,
                               'backcard-width': vol[1]}
                              for vol in ticket_dict['volumes']]}
        return result

    result = {}
    for key in config_dict['ticket-layout'].keys():
        result[key] = config_dict['ticket-layout'][key]
    result['output-filename'] = output_filename
    result['pages'] = [[compute_ticket_parameters(booklet_dict['ticket'][tt])
                        for tt in page] for page in booklet_dict['booklet']['pages']]
    return result


# LaTeX components...

  
def latex_begin(augmented_booklet):
    font_size = augmented_booklet['font-size']
    left_margin = augmented_booklet['left-margin']
    right_margin = augmented_booklet['right-margin']
    upper_margin = augmented_booklet['upper-margin']
    lower_margin = augmented_booklet['lower-margin']
    return "\n".join([
        f"\\documentclass[{font_size}pt,a4paper]{{memoir}}",
        f"\\setlrmarginsandblock{{{left_margin}mm}}{{{right_margin}mm}}{{*}}",
        f"\\setulmarginsandblock{{{upper_margin}mm}}{{{lower_margin}mm}}{{*}}",
        "\\fixthelayout",
        "\\renewcommand{\\familydefault}{\\sfdefault}",
        "\\usepackage{multirow}",
        " ",
        "\\begin{document}",
        " "])


def latex_end():
    return "\n\n\\vfill\n\\end{document}\n"    
    

def latex_table_begin(bd, ticket_dict):
    """A ticket latex table depends on the number of volumes.
    Here is the beginning fragment of a table for a 4-volume ticket.
    
    {\renewcommand{\arraystretch}{1.2}
    \begin{tabular}{|c|p{18mm}|c|c|p{0mm}|c|c|p{0mm}|c|c|p{0mm}|c|c|}
    \hline

    """
    label_width = bd['label-width']
    volume_separation = bd['volume-separation']
    vertical_stretch = bd['vertical-stretch']
    number_of_volumes = len(ticket_dict['volumes'])
    columns_spec = f"|c|p{{{label_width}mm}}|"
    for k in range(number_of_volumes - 1):
        columns_spec += f"c|c|p{{{volume_separation}mm}}|"
    columns_spec += "c|c|"
    result = f"{{\\renewcommand{{\\arraystretch}}{{{vertical_stretch}}}\n"
    result += f"\\begin{{tabular}}{{{columns_spec}}}\n"
    result += "\\hline\n"
    return result


def latex_table_end():
    return "\\hline\n\\end{tabular}}\n"


def latex_multirow_spec(augmented_booklet, ticket_dict):
    """Here is an example for a 4-volume ticket:

    \multirow{6}{26mm}{\large Etudes}& \multirow{2}{*}{\Large 320} &\multicolumn{2}{c|}{2020-1} 
    & & \multicolumn{2}{c|}{2020-2} & & \multicolumn{2}{c|}{2021-1} & & \multicolumn{2}{c|}{2021-2} \\

    """
    title_width = augmented_booklet['title-width']
    title_styling = augmented_booklet['title-styling']
    title = ticket_dict['title']
    color = ticket_dict['color']
    number_of_volumes = len(ticket_dict['volumes'])
    
    result = f"\\multirow{{6}}{{{title_width}mm}}{{{title_styling} {title}}}"
    result += f" & \\multirow{{2}}{{*}}{{\\Large {color}}} &"
    for k,vol in enumerate(ticket_dict['volumes']):
        result += f"\\multicolumn{{2}}{{c|}}{{{vol['volume-label']}}}"
        if k != number_of_volumes - 1:
            result += " & & "
    result += " \\\\\n"
    return result


def latex_header_cline(ticket_dict):
    """There are the column lines in the header, and the column lines in the
    table body. These are the specifications for the header clines (column-lines).
    
    For example, a 4-volume ticket:

    \cline{3-4}\cline{6-7}\cline{9-10}\cline{12-13}

    """
    number_of_volumes = len(ticket_dict['volumes'])
    result = ""
    for k in range(number_of_volumes):
        result += f"\\cline{{{3*(k + 1)}-{3*(k + 1) + 1}}}"
    result += "\n"
    return result


def latex_header_HW(ticket_dict):
    """H and W header labels on the multicolumns.
    For 4-volume ticket, it should look like this:
    
    & & H & W & & H & W & & H & W & & H & W\\
        
    """
    number_of_volumes = len(ticket_dict['volumes'])
    result = ""
    for k in range(number_of_volumes):
        result += " & & H & W"
    result += "\\\\\n"
    return result


def latex_body_cline(ticket_dict):
    """Column lines separating rows in the body of the ticket table.
    For example, ticket with 4 volumes:

    \cline{2-2}\cline{3-4}\cline{6-7}\cline{9-10}\cline{12-13}

    """
    number_of_volumes = len(ticket_dict['volumes'])
    result = "\\cline{2-2}"
    for k in range(number_of_volumes):
        result += f"\\cline{{{3*(k+1)}-{3*(k+1)+1}}}"
    result += "\n"
    return result


def latex_cardboard_row(augmented_booklet, ticket_dict):
    """Example, for a 4-volume ticket:

    & carton  & 241 & 144 & & 241 & 144 & & 241 & 144 & & 241 & 144 \\

    Here we have a user-set french label (carton) for the cardboard row label.
    
    """
    cardboard_label = augmented_booklet['cardboard-label']
    result = f"& {cardboard_label}"
    for k,vol in enumerate(ticket_dict['volumes']):
        result += f" & {vol['cardboard-height']} & {vol['cardboard-width']} &"
    # Strip off the last &
    result = result[0:-1]
    result += "\\\\\n"
    return result
                

def latex_paper_row(augmented_booklet, ticket_dict):
    """Example, for a 4-volume ticket:

    & papier  & 271 & 378 & & 271 & 378 & & 271 & 372 & & 271 & 379 \\
        
    It's constructed almost the same as cardboard row.
    All these data rows are very similar.

    """
    paper_label = augmented_booklet['paper-label']
    result = f"& {paper_label}"
    for k,vol in enumerate(ticket_dict['volumes']):
        result += f" & {vol['paper-height']} & {vol['paper-width']} &"
    # Strip off the last &
    result = result[0:-1]
    result += "\\\\\n"
    return result


def latex_buckram_row(augmented_booklet, ticket_dict):
    """Example with 4-volume ticket:

    & buckram  & 281 & 140 & & 281 & 140 & & 281 & 134 & & 281 & 141 \\
        
    """
    buckram_label = augmented_booklet['buckram-label']
    result = f"& {buckram_label}"
    for k,vol in enumerate(ticket_dict['volumes']):
        result += f" & {vol['buckram-height']} & {vol['buckram-width']} &"
    # Strip off the last &
    result = result[0:-1]
    result += "\\\\\n"
    return result


def latex_backcard_row(augmented_booklet, ticket_dict):
    """Example, for a 4-volume ticket:

    & carte-a-dos  & 241 & 40 & & 241 & 40 & & 241 & 34 & & 241 & 41 \\

    Here the user has supplied his own label "carte-a-dos" for the backcard.

    """
    backcard_label = augmented_booklet['backcard-label']
    result = f"& {backcard_label}"
    for k,vol in enumerate(ticket_dict['volumes']):
        result += f" & {vol['backcard-height']} & {vol['backcard-width']} &"
    # Strip off the last &
    result = result[0:-1]
    result += "\\\\\n"
    return result


def latex_between_tickets(augmented_booklet):
    ticket_spacing = augmented_booklet['ticket-spacing']
    return f"\n\\vskip {ticket_spacing}mm\n\n"


def latex_between_pages():
    return "\n\\vfill\\newpage\n"


def latex_write(augmented_booklet):
    # my_ticket = augmented_booklet['pages'][0][4]
    with open(augmented_booklet['output-filename'], 'w') as f:
        f.write(latex_begin(augmented_booklet))
        for page in augmented_booklet['pages']:
            for my_ticket in page:
                f.write(latex_table_begin(augmented_booklet, my_ticket))
                f.write(latex_multirow_spec(augmented_booklet, my_ticket))
                f.write(latex_header_cline(my_ticket))
                f.write(latex_header_HW(my_ticket))
                f.write(latex_cardboard_row(augmented_booklet, my_ticket))
                f.write(latex_body_cline(my_ticket))
                f.write(latex_paper_row(augmented_booklet, my_ticket))
                f.write(latex_body_cline(my_ticket))
                f.write(latex_buckram_row(augmented_booklet, my_ticket))
                f.write(latex_body_cline(my_ticket))
                f.write(latex_backcard_row(augmented_booklet, my_ticket))
                f.write(latex_body_cline(my_ticket))
                f.write(latex_table_end())
                f.write(latex_between_tickets(augmented_booklet))
            f.write(latex_between_pages())
        f.write(latex_end())

