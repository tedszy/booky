# display.py
#
# Messages and tables using Rich.

from rich import print as rprint
from rich.panel import Panel


def display_welcome(version):
    rprint(Panel(f"[white bold]Booky version {version}",
                 style='green'))
           

def display_error(message):
    rprint(Panel(f"[white]{message}",
                 style='red',
                 title='ERROR',
                 subtitle='ERROR'))


def display_warning(message):
    rprint(Panel(f"[white]{message}",
                 style='yellow',
                 title='warning',
                 subtitle=''))


def display_info(message):
    rprint(Panel(f"[white]{message}",
                 style='blue',
                 title='',
                 subtitle=''))


def display_toml_error(filename):
    display_error(f"Bad TOML file: {filename}: possible duplicate key or bad syntax.")
