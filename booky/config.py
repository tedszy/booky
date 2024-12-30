### config.py


import logging
import tomllib
import rich.table, rich.console
import booky.messages


logger = logging.getLogger('booky')
logging.basicConfig(level=logging.DEBUG)


config_toplevel_keys = [('pub-db-filename', str),
                        ('pub-validation', dict),
                        ('ticket-layout', dict)]

config_pub_validation_keys = [('colors', list),
                              ('block-limits', list),
                              ('cover-limits', list)]

config_ticket_layout_keys = [('left-margin', (int, float)),
                             ('right-margin', (int, float)),
                             ('upper-margin', (int, float)),
                             ('lower-margin', (int, float)),
                             ('font-size', int),
                             ('vertical-stretch', (int, float)),
                             ('title-width', (int, float)),
                             ('title-styling', str),
                             ('label-width', (int, float)),
                             ('volume-separation', (int, float)),
                             ('ticket-spacing', (int, float)),
                             ('cardboard-label', str),
                             ('paper-label', str),
                             ('buckram-label', str),
                             ('backcard-label', str)]

type_msg = {int: 'an integer', (int, float): 'a number', str: 'a string',
            list: 'a list', dict: 'a dict'}


def config_check_for_unwanted_keys(config_filename, config_dict):
    for key in config_dict.keys():
        if key not in [k[0] for k in config_toplevel_keys]:
            raise KeyError(f"bad key {key} in {config_filename}.")
            
    for key in config_dict['pub-validation'].keys():
        if key not in [k[0] for k in config_pub_validation_keys]:
            raise KeyError(f"bad key {key} in pub-validation of {config_filename}.")

    for key in config_dict['ticket-layout'].keys():
        if key not in [k[0] for k in config_ticket_layout_keys]:
            raise KeyError(f"bad key {key} in {config_filename} ticket-layout.")


def config_check_for_required_keys(config_filename, config_dict):
        for key in [k[0] for k in config_toplevel_keys]:
            if key not in config_dict.keys():
                raise KeyError(f"missing key {key} in {config_filename}.")

        for key in [k[0] for k in config_pub_validation_keys]:
            if key not in config_dict['pub-validation'].keys():
                raise KeyError(f"missing key {key} in {config_filename} pub-validation.")

        for key in [k[0] for k in config_ticket_layout_keys]:
            if key not in config_dict['ticket-layout'].keys():
                raise KeyError(f"missing key {key} in {config_filename} ticket-layout.")


def config_check_toplevel_values(config_filename, config_dict):
    def check_toplevel_value_types(toplevel_key, instance_type):
        x = config_dict[toplevel_key]
        if not isinstance(x, instance_type):
            raise ValueError(
                f"in {config_filename}, {toplevel_key} value {x} should be {type_msg[instance_type]}")     

    for t in config_toplevel_keys:
        check_toplevel_value_types(*t)


def config_check_pub_validation_values(config_filename, config_dict):
    def check_value_types(pub_validation_key, instance_type):
        x = config_dict['pub-validation'][pub_validation_key]
        if not isinstance(x, instance_type):
            raise ValueError(
                f"in {config_filename}, {pub_validation_key} value {x} should be {type_msg[instance_type]}")     

    for t in config_pub_validation_keys:
        check_value_types(*t)

    d = config_dict['pub-validation']
    
    for c in d['colors']:
        if not (isinstance(c, str) and len(c)==3):
            raise ValueError(f"in {config_filename}, color {c} should be string of length 3.")

    bl = d['block-limits']
    if not (len(bl)==2 and isinstance(bl[0], int) and isinstance(bl[1], int)):
            raise ValueError(f"in {config_filename}, bad block-limits {bl}.")
        
    cl = d['cover-limits']
    if not (len(cl)==2 and isinstance(cl[0], int) and isinstance(cl[1], int)):
            raise ValueError(f"in {config_filename}, bad cover-limits {cl}.")

        
def config_check_ticket_layout_values(config_filename, config_dict):
    def check_layout_value_types(layout_key, instance_type):
        x = config_dict['ticket-layout'][layout_key]
        if not isinstance(x, instance_type):
            raise ValueError(
                f"in {config_filename}, {layout_key} value {x} should be {type_msg[instance_type]}")     

    for t in config_ticket_layout_keys:
        check_layout_value_types(*t)
        

def load_config(config_filename):
    """Load configuration.toml into config_dict and verify it."""
    
    try:
        with open(config_filename, 'rb') as f:
            config_dict = tomllib.load(f)
    except tomllib.TOMLDecodeError: 
        booky.messages.display_toml_error(config_filename)
        exit(1)
    except FileNotFoundError as f:
        booky.messages.display_error(str(f))
        exit(1)

    logger.info('config_dict loaded.')

    # Verify that the config_dict keys are what we expect.
    
    try:
        config_check_for_unwanted_keys(config_filename, config_dict)
        config_check_for_required_keys(config_filename, config_dict)                
        logger.info('config_dict keys are ok.')
        config_check_toplevel_values(config_filename, config_dict)
        config_check_pub_validation_values(config_filename, config_dict)
        config_check_ticket_layout_values(config_filename, config_dict)
        logger.info('config_dict values are ok.')
        
    except KeyError as v: 
        booky.messages.display_error(v)
        exit(1)
    except ValueError as v:
        booky.messages.display_error(v)
        exit(1)

    return config_dict


def display_config(config_filename, config_dict):
    data_color = 'white'
    table = rich.table.Table(title="Booky configuration", show_lines=False)
    table.add_column('Parameter', justify='right', style='green')
    table.add_column('Value', style='white')
    table.add_row('Configuration file', config_filename)
    table.add_row('Publication database file', config_dict['pub-db-filename'])
    tl = config_dict['ticket-layout']
    for col1, col2 in [('Ticket left margin', tl['left-margin']), 
                       ('Ticket right margin', tl['right-margin']),
                       ('Ticket upper margin', tl['upper-margin']),
                       ('Ticket lower margin', tl['lower-margin']),
                       ('Ticket font size', tl['font-size']),
                       ('Title width', tl['title-width']),
                       ('Title LaTex styling', tl['title-styling']),
                       ('Vertical stretch', tl['vertical-stretch']),
                       ('Volume separation within tickets', tl['volume-separation']),
                       ('Spacing between tickets', tl['ticket-spacing']),
                       ('Label width', tl['label-width']),
                       ('Cardboard alternate label', tl['cardboard-label']),
                       ('Paper alternate label', tl['paper-label']),
                       ('Buckram alternate label', tl['buckram-label']),
                       ('Backcard alternate label',tl['backcard-label'])]:
        table.add_row(col1, str(col2))
        console = rich.console.Console()
        print()
        console.print(table)
        print()


