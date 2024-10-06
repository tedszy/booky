# display.py
#
# Messages and tables using Rich.

from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.console import Console


def display_welcome(version):
    rprint(f"[white bold]Booky version {version}.")
    #    rprint(Panel(f"[white bold]Booky version {version}",
    #             style='green',
    #             expand=False))
           

def display_error(message):
    rprint(Panel(f"[white]{message}",
                 style='red',
                 title='ERROR',
                 subtitle='ERROR',
                 expand=False))


def display_warning(message):
    rprint(Panel(f"[white]{message}",
                 style='yellow',
                 title='warning',
                 subtitle='',
                 expand=False))


def display_info(message):
    rprint(Panel(f"[white]{message}",
                 style='green',
                 title='',
                 subtitle='',
                 expand=False))


def display_toml_error(filename):
    display_error(f"Bad TOML file: {filename}: possible duplicate key or bad syntax.")


def pubs_to_sorted_rows(pub_dict):
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


def display_pubs_narrow(table_title, pub_dict):
    # We take only the key and title of each row.
    key_style = 'bold magenta'
    title_style = 'white'
    table = Table(title=table_title)
    table.add_column('Key', justify='right', style=key_style)
    table.add_column('Title', style=title_style)
    for row in pubs_to_sorted_rows(pub_dict):
        table.add_row(row[0], row[1])
    console = Console()
    print()
    console.print(table)
    print()


def display_pubs_wide(table_title, pub_dict):
    data_color = 'white'
    table = Table(title=table_title, show_lines=True)
    table.add_column('Key', justify='right', style='bold magenta')
    table.add_column('Title', style='white')
    table.add_column('BH',style=data_color)
    table.add_column('BW',style=data_color)
    table.add_column('CH',style=data_color)
    table.add_column('CW',style=data_color)
    table.add_column('Color',style=data_color)
    for row in pubs_to_sorted_rows(pub_dict):
        table.add_row(*row)
    console = Console()
    print()
    console.print(table)
    print()


def display_config(config, config_filename):
    data_color = 'white'
    table = Table(title="Booky configuration", show_lines=False)
    table.add_column('Parameter', justify='right', style='green')
    table.add_column('Value', style='white')

    table.add_row('Configuration file', config_filename)
    table.add_row('Publication database file', config.pub_db_filename)

    table.add_row('Ticket left margin', str(config.ticket_layout.left_margin))
    table.add_row('Ticket right margin', str(config.ticket_layout.right_margin)) 
    table.add_row('Ticket upper margin', str(config.ticket_layout.upper_margin))
    table.add_row('Ticket lower margin', str(config.ticket_layout.lower_margin))
    table.add_row('Ticket font size', str(config.ticket_layout.font_size))
    table.add_row('Title width', str(config.ticket_layout.title_width))
    table.add_row('Title LaTex styling', config.ticket_layout.title_styling)
    table.add_row('Vertical stretch', str(config.ticket_layout.vertical_stretch))
    table.add_row('Volume separation', str(config.ticket_layout.volume_separation))
    table.add_row('Ticket spacing', str(config.ticket_layout.ticket_spacing))
    table.add_row('Element label width', str(config.ticket_layout.label_width))
    table.add_row('Cardboard element label', str(config.ticket_layout.cardboard_label))
    table.add_row('Paper element label', config.ticket_layout.paper_label)
    table.add_row('Buckram element label', config.ticket_layout.buckram_label)
    table.add_row('Backcard element label', config.ticket_layout.backcard_label)

    console = Console()
    print()
    console.print(table)
    print()





