# config.py


import logging

#from typing import List, Dict
from tomllib import load, TOMLDecodeError
#from pydantic import BaseModel, ValidationError, Field 
#from pydantic import ConfigDict, field_validator
from rich.table import Table
from rich.console import Console

from .messages import display_error, display_toml_error





# ============================ booky 2.1 ======================


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
            config_dict = load(f)
    except TOMLDecodeError: 
        display_toml_error(config_filename)
        exit(1)
    except ValidationError as v:
        display_error(v.errors())
        exit(1)
    except FileNotFoundError as f:
        display_error(str(f))
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
        display_error(v)
        exit(1)
    except ValueError as v:
        display_error(v)
        exit(1)

    return config_dict


def display_config(config_filename, config_dict):
    data_color = 'white'
    table = Table(title="Booky configuration", show_lines=False)
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
        console = Console()
        print()
        console.print(table)
        print()





# ==============================================================


# def check_limits(limits, description):
#     """Check that limits is a length 2 list [a,b] with a<b.
    
#     Args:
#         limits [int, int]: typical limits for bookbinding dimensions.
#                            Usually these are millimeters.
#         description str: a string describing something about limits,
#                          which is used if exception is thrown.

#     Returns:
#         [int, int]

#     Exceptions:
#         Throws ValueError if limits doesn't pass.

#     Examples:
#         check_limits([100,200], "block-height") => [100, 200]
#         check_limits([200,100], "block-height") => ValueError

#     Notes: 
#         This function is used a few times in PubValidationConfig
#         to reduce repetition of code.
#     """
#     if not len(limits)==2:
#         raise ValueError(f"{description} must have length 2, given: {limits}.")
#     a, b = limits
#     if not (a>0 and b> 0 and (limits[0]<limits[1])):
#         raise ValueError(f"{description} must be [a, b] with 0 < a < b.")
#     else:
#         return limits


# class PubValidationConfig(BaseModel):
#     """Class for representing publication validation constraints.

#     Attributes:
#         colors List[str]: list of allowed colors.
#         block_limits [int, int]: upper and lower bounds on block dimensions.
#         cover_limits [int, int]: upper and lower bounds on cover dimensions.

#     Methods:
#         ensure_block_limits: Pydantic validator for block_limits.
#         ensure_cover_limits: Pydantic validator for cover_limits.
#         unique_colors: Pydantic validator for list of allowed colors.

#     """
#     colors: List[str]
#     block_limits: List[int] = Field(alias='block-limits')
#     cover_limits: List[int] = Field(alias='cover-limits')

#     @field_validator('block_limits')
#     @classmethod
#     def ensure_block_limits(cls, limits):
#         check_limits(limits, 'block_limits')
#         return limits

#     @field_validator('cover_limits')
#     @classmethod
#     def ensure_cover_limits(cls, limits):
#         check_limits(limits, 'cover_limits')
#         return limits

#     @field_validator('colors')
#     @classmethod
#     def unique_colors(cls, colors):
#         if not len(colors) == len(set(colors)):
#             raise ValueError((f'colors must be unique: '
#                               f'there is a duplicate color in {colors}'))
#         else:
#             return colors


# class TicketLayoutConfig(BaseModel):
#     """Class representing how tickets and booklets of tickets are set up.
    
#     This is a Pydantic-derived class with simple checks on types.
#     If the ticket layout data in configuration toml file is of
#     the wrong type, exeption will be thrown.

#     Attributes are typographical parameters for Latexing the tickets 
#     and the booklets of tickets.

#     Attributes:
#         left_margin int:
#         right_margin int:
#         upper_margin int:
#         lower_margin int:
#         font_size int:
#         vertical_stretch float:
#         title_width int:
#         title_styling str:
#         label_width int: 
#         volume_separation int:
#         ticket_spacing int:
#         cardboard_label str:
#         paper_label str:
#         buckram_label str: 
#         backcard_label str:

#     Methods:
#         None.

#     """
#     left_margin: int = Field(alias='left-margin')
#     right_margin: int = Field(alias='right-margin')
#     upper_margin: int = Field(alias='upper-margin')
#     lower_margin: int = Field(alias='lower-margin')
#     font_size: int = Field(alias='font-size')
#     vertical_stretch: float = Field(alias='vertical-stretch')
#     title_width: int = Field(alias='title-width')
#     title_styling: str = Field(alias='title-styling')
#     label_width: int = Field(alias='label-width')
#     volume_separation: int = Field(alias='volume-separation')
#     ticket_spacing: int = Field(alias='ticket-spacing')
#     cardboard_label: str = Field(alias='cardboard-label')
#     paper_label: str = Field(alias='paper-label')
#     buckram_label: str = Field(alias='buckram-label')
#     backcard_label: str = Field(alias='backcard-label')


# class BookyConfig(BaseModel):
#     """Class representing Booky master configuration.

#     Derived from Pydantic BaseModel. An instance of this class 
#     has all the information needed to validate publications 
#     and set up the ticket/booklet Latex layout.

#     Attributes:
#         config_filename str: configuration toml file.
#         pub_db_filename str: publication database toml file.
#         pub_validation PubValidationConfig: constraints for validating pubs.
#         ticket_layout TicketLayoutConfig: ticket/booklet config info.

#     Methods:
#         good_color(c str) bool: check publication color.
#         good_block_height(bh int) bool: check publication block height.
#         good_block_width(bw int) bool: check publication block width.
#         good_cover_height(ch int) bool: check publication cover height.
#         good_cover_width(cw int) bool: check publication cover width.
#         display(): print table of configuration settings.

#     Notes:
#         The configuration toml filename is added as an attribute,
#         for convenience. But this filename must be known before
#         a BookyConfig object can be created.

#     """
#     model_config = ConfigDict(populate_by_name=True)  # Might need this.
#     config_filename: str = ""
#     pub_db_filename: str = Field(alias='pub-db-filename')
#     pub_validation: PubValidationConfig = Field(alias='pub-validation')
#     ticket_layout: TicketLayoutConfig = Field(alias='ticket-layout')

#     def good_color(self, c):
#         return c in self.pub_validation.colors

#     def good_block_height(self, bh):
#         a, b = self.pub_validation.block_limits
#         return (a <= bh) and (bh <= b)

#     def good_block_width(self, bw):
#         a, b = self.pub_validation.block_limits
#         return (a <= bw) and (bw <= b)

#     def good_cover_height(self, ch):
#         a, b = self.pub_validation.cover_limits
#         return (a <= ch) and (ch <= b)

#     def good_cover_width(self, cw):
#         a, b = self.pub_validation.cover_limits
#         return (a <= cw) and (cw <= b)

    # def display(self):
    #     data_color = 'white'
    #     table = Table(title="Booky configuration", show_lines=False)
    #     table.add_column('Parameter', justify='right', style='green')
    #     table.add_column('Value', style='white')
    #     table.add_row('Configuration file', self.config_filename)
    #     table.add_row('Publication database file', self.pub_db_filename)

    #     stl = self.ticket_layout
    #     for col1, col2 in [('Ticket left margin', stl.left_margin), 
    #                        ('Ticket right margin', stl.right_margin),
    #                        ('Ticket upper margin', stl.upper_margin),
    #                        ('Ticket lower margin', stl.lower_margin),
    #                        ('Ticket font size', stl.font_size),
    #                        ('Title width', stl.title_width),
    #                        ('Title LaTex styling', stl.title_styling),
    #                        ('Vertical stretch', stl.vertical_stretch),
    #                        ('Volume separation', stl.volume_separation),
    #                        ('Ticket spacing', stl.ticket_spacing),
    #                        ('Element label width', stl.label_width),
    #                        ('Cardboard element label', stl.cardboard_label),
    #                        ('Paper element label', stl.paper_label),
    #                        ('Buckram element label', stl.buckram_label),
    #                        ('Backcard element label',stl.backcard_label)]:
    #         table.add_row(col1, str(col2))
    #     console = Console()
    #     print()
    #     console.print(table)
    #     print()





if __name__ == '__main__':
    config_filename = '../sample-project/configure.toml'
    config_dict = load_config(config_filename)

    display_config(config_filename, config_dict)
    
    #pprint.pprint(config_dict)




    

#else:
    # CONFIG_FILENAME = "configure.toml"
    # with open(CONFIG_FILENAME, 'rb') as f:
    #     data = load(f)
    #     # Create the BOOKY_CONFIG object and add the configuration
    #     # toml filename as an attribute.
    #     BOOKY_CONFIG = BookyConfig.model_validate(data)
    #     BOOKY_CONFIG.config_filename = CONFIG_FILENAME

    
