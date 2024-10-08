"""
Module: config

Classes:
    PubValidationConfig: pydantic-derived class for holding 
                         constraints on publication bookbinding data.
    TicketLayoutConfig: Pydantic derived class for holding ticket 
                        and booklet configuration parameters.
    BookyConfig: The master Pydantic-derived class holding all 
                 sanity-checked configuration information
                 and publication validation information, 
                 as specified in the configuration toml file.

Functions:
    check_limits(limits, desc): Performs a sanity check on given limits.

Constants:
    CONFIG_FILENAME: All configuration data is defined in this file.
                     This is the logical entry point where everything begins.
    BOOKY_CONFIG: The unique BookyConfig instance that contains
                  all the configuration parameters, validation parameters,
                  validation functions and typography settings.

Authors:
    Ted Szylowiec

Notes:
    When this module is imported, the BOOKY_CONFIG instance is 
    created from CONFIG_FILENAME. Thus it's possible that importing
    this module can throw a FileNotFound exception.
"""

from typing import List, Dict
from tomllib import load, TOMLDecodeError
from pydantic import BaseModel, ValidationError, Field 
from pydantic import ConfigDict, field_validator
from rich.table import Table
from rich.console import Console


def check_limits(limits, description):
    """Check that limits is a length 2 list [a,b] with a<b.
    
    Args:
        limits [int, int]: typical limits for bookbinding dimensions.
                           Usually these are millimeters.
        description str: a string describing something about limits,
                         which is used if exception is thrown.

    Returns:
        [int, int]

    Exceptions:
        Throws ValueError if limits doesn't pass.

    Examples:
        check_limits([100,200], "block-height") => [100, 200]
        check_limits([200,100], "block-height") => ValueError

    Notes: 
        This function is used a few times in PubValidationConfig
        to reduce repetition of code.
    """
    if not len(limits)==2:
        raise ValueError(f"{description} must have length 2, given: {limits}.")
    a, b = limits
    if not (a>0 and b> 0 and (limits[0]<limits[1])):
        raise ValueError(f"{description} must be [a, b] with 0 < a < b.")
    else:
        return limits


class PubValidationConfig(BaseModel):
    """Class for representing publication validation constraints.

    Attributes:
        colors List[str]: list of allowed colors.
        block_limits [int, int]: upper and lower bounds on block dimensions.
        cover_limits [int, int]: upper and lower bounds on cover dimensions.

    Methods:
        ensure_block_limits: Pydantic validator for block_limits.
        ensure_cover_limits: Pydantic validator for cover_limits.
        unique_colors: Pydantic validator for list of allowed colors.

    """
    colors: List[str]
    block_limits: List[int] = Field(alias='block-limits')
    cover_limits: List[int] = Field(alias='cover-limits')

    @field_validator('block_limits')
    @classmethod
    def ensure_block_limits(cls, limits):
        check_limits(limits, 'block_limits')
        return limits

    @field_validator('cover_limits')
    @classmethod
    def ensure_cover_limits(cls, limits):
        check_limits(limits, 'cover_limits')
        return limits

    @field_validator('colors')
    @classmethod
    def unique_colors(cls, colors):
        if not len(colors) == len(set(colors)):
            raise ValueError((f'colors must be unique: '
                              f'there is a duplicate color in {colors}'))
        else:
            return colors


class TicketLayoutConfig(BaseModel):
    """Class representing how tickets and booklets of tickets are set up.
    
    This is a Pydantic-derived class with simple checks on types.
    If the ticket layout data in configuration toml file is of
    the wrong type, exeption will be thrown.

    Attributes are typographical parameters for Latexing the tickets 
    and the booklets of tickets.

    Attributes:
        left_margin int:
        right_margin int:
        upper_margin int:
        lower_margin int:
        font_size int:
        vertical_stretch float:
        title_width int:
        title_styling str:
        label_width int: 
        volume_separation int:
        ticket_spacing int:
        cardboard_label str:
        paper_label str:
        buckram_label str: 
        backcard_label str:

    Methods:
        None.

    """
    left_margin: int = Field(alias='left-margin')
    right_margin: int = Field(alias='right-margin')
    upper_margin: int = Field(alias='upper-margin')
    lower_margin: int = Field(alias='lower-margin')
    font_size: int = Field(alias='font-size')
    vertical_stretch: float = Field(alias='vertical-stretch')
    title_width: int = Field(alias='title-width')
    title_styling: str = Field(alias='title-styling')
    label_width: int = Field(alias='label-width')
    volume_separation: int = Field(alias='volume-separation')
    ticket_spacing: int = Field(alias='ticket-spacing')
    cardboard_label: str = Field(alias='cardboard-label')
    paper_label: str = Field(alias='paper-label')
    buckram_label: str = Field(alias='buckram-label')
    backcard_label: str = Field(alias='backcard-label')


class BookyConfig(BaseModel):
    """Class representing Booky master configuration.

    Derived from Pydantic BaseModel. An instance of this class 
    has all the information needed to validate publications 
    and set up the ticket/booklet Latex layout.

    Attributes:
        config_filename str: configuration toml file.
        pub_db_filename str: publication database toml file.
        pub_validation PubValidationConfig: constraints for validating pubs.
        ticket_layout TicketLayoutConfig: ticket/booklet config info.

    Methods:
        good_color(c str) bool: check publication color.
        good_block_height(bh int) bool: check publication block height.
        good_block_width(bw int) bool: check publication block width.
        good_cover_height(ch int) bool: check publication cover height.
        good_cover_width(cw int) bool: check publication cover width.
        display(): print table of configuration settings.

    Notes:
        The configuration toml filename is added as an attribute,
        for convenience. But this filename must be known before
        a BookyConfig object can be created.

    """
    model_config = ConfigDict(populate_by_name=True)  # Might need this.
    config_filename: str = ""
    pub_db_filename: str = Field(alias='pub-db-filename')
    pub_validation: PubValidationConfig = Field(alias='pub-validation')
    ticket_layout: TicketLayoutConfig = Field(alias='ticket-layout')

    def good_color(self, c):
        return c in self.pub_validation.colors

    def good_block_height(self, bh):
        a, b = self.pub_validation.block_limits
        return (a <= bh) and (bh <= b)

    def good_block_width(self, bw):
        a, b = self.pub_validation.block_limits
        return (a <= bw) and (bw <= b)

    def good_cover_height(self, ch):
        a, b = self.pub_validation.cover_limits
        return (a <= ch) and (ch <= b)

    def good_cover_width(self, cw):
        a, b = self.pub_validation.cover_limits
        return (a <= cw) and (cw <= b)

    def display(self):
        data_color = 'white'
        table = Table(title="Booky configuration", show_lines=False)
        table.add_column('Parameter', justify='right', style='green')
        table.add_column('Value', style='white')
        table.add_row('Configuration file', self.config_filename)
        table.add_row('Publication database file', self.pub_db_filename)

        stl = self.ticket_layout
        for col1, col2 in [('Ticket left margin', stl.left_margin), 
                           ('Ticket right margin', stl.right_margin),
                           ('Ticket upper margin', stl.upper_margin),
                           ('Ticket lower margin', stl.lower_margin),
                           ('Ticket font size', stl.font_size),
                           ('Title width', stl.title_width),
                           ('Title LaTex styling', stl.title_styling),
                           ('Vertical stretch', stl.vertical_stretch),
                           ('Volume separation', stl.volume_separation),
                           ('Ticket spacing', stl.ticket_spacing),
                           ('Element label width', stl.label_width),
                           ('Cardboard element label', stl.cardboard_label),
                           ('Paper element label', stl.paper_label),
                           ('Buckram element label', stl.buckram_label),
                           ('Backcard element label',stl.backcard_label)]:
            table.add_row(col1, str(col2))
        console = Console()
        print()
        console.print(table)
        print()


CONFIG_FILENAME = "configure.toml"


with open(CONFIG_FILENAME, 'rb') as f:
        data = load(f)
        # Create the BOOKY_CONFIG object and add the configuration
        # toml filename as an attribute.
        BOOKY_CONFIG = BookyConfig.model_validate(data)
        BOOKY_CONFIG.config_filename = CONFIG_FILENAME


