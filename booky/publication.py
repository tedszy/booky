### publication.py


import tomllib
import fnmatch
import rich.table, rich.console
import booky.messages


def load_pubdb(pubdb_filename):
    """Load publication.toml database into pubdb_dict and verify it (to do)."""    
    try:
        with open(pubdb_filename, 'rb') as f:
            pubdb_dict = tomllib.load(f)
    except tomllib.TOMLDecodeError: 
        booky.messages.display_toml_error(config_filename)
        exit(1)
    except FileNotFoundError as f:
        booky.messages.display_error(str(f))
        exit(1)

    return pubdb_dict


def display_pubdb_narrow(title, pubdb_dict):
    key_style = 'bold magenta'
    title_style = 'white'
    table = rich.table.Table(title=title)
    table.add_column('Key', justify='right', style=key_style)
    table.add_column('Title', style=title_style)
    for key in sorted(pubdb_dict.keys()):
        table.add_row(key, pubdb_dict[key]['title'])
    console = rich.console.Console()
    print()
    console.print(table)
    print()


def display_pubdb_wide(title, pubdb_dict):
    data_color = 'white'
    table = rich.table.Table(title=title, show_lines=True)
    table.add_column('Key', justify='right', style='bold magenta')
    table.add_column('Title', style='white')
    table.add_column('BH',style=data_color)
    table.add_column('BW',style=data_color)
    table.add_column('CH',style=data_color)
    table.add_column('CW',style=data_color)
    table.add_column('Color',style=data_color)
    for key in sorted(pubdb_dict.keys()):
        table.add_row(key,
                      pubdb_dict[key]['title'],
                      str(pubdb_dict[key]['block-height']),
                      str(pubdb_dict[key]['block-width']),
                      str(pubdb_dict[key]['cover-height']),
                      str(pubdb_dict[key]['cover-width']),
                      str(pubdb_dict[key]['color']))
    console = rich.console.Console()
    print()
    console.print(table)
    print()


def search_keys_pubdb(search_arg, pubdb_dict):
    result = {}
    for key in sorted(pubdb_dict.keys()):
        if fnmatch.fnmatchcase(key.upper(), search_arg.upper()):
            result[key] = pubdb_dict[key]
    return result

           
def search_titles_pubdb(search_arg, pubdb_dict):
    result = {}
    for key in sorted(pubdb_dict.keys()):
        if fnmatch.fnmatchcase(pubdb_dict[key]['title'].upper(), 
                               search_arg.upper()):
            result[key] = pubdb_dict[key]
    return result

