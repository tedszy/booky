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
















