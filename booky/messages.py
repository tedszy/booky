### messages.py


from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.console import Console


def display_welcome(version):
    rprint(f"[white bold]Booky version {version}.")
           

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



