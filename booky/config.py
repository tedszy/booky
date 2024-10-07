# config.py

from typing import List, Dict
from tomllib import load, TOMLDecodeError
from pydantic import BaseModel, ValidationError, Field 
from pydantic import ConfigDict, field_validator
from rich.panel import Panel
from rich.table import Table
from rich.console import Console


def check_limits(limits, desc):
    if not len(limits)==2:
        raise ValueError(f"desc must have length 2, given: {limits}.")
    a, b = limits
    if not (a>0 and b> 0 and (limits[0]<limits[1])):
        raise ValueError(f"{desc} must be [a, b] with 0 < a < b.")
    else:
        return limits


class PubValidationConfig(BaseModel):
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
            raise ValueError(f'colors must be unique: there is a duplicate color in {colors}')
        else:
            return colors


class TicketLayoutConfig(BaseModel):
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

        table.add_row('Ticket left margin', str(self.ticket_layout.left_margin))
        table.add_row('Ticket right margin', str(self.ticket_layout.right_margin)) 
        table.add_row('Ticket upper margin', str(self.ticket_layout.upper_margin))
        table.add_row('Ticket lower margin', str(self.ticket_layout.lower_margin))
        table.add_row('Ticket font size', str(self.ticket_layout.font_size))
        table.add_row('Title width', str(self.ticket_layout.title_width))
        table.add_row('Title LaTex styling', self.ticket_layout.title_styling)
        table.add_row('Vertical stretch', str(self.ticket_layout.vertical_stretch))
        table.add_row('Volume separation', str(self.ticket_layout.volume_separation))
        table.add_row('Ticket spacing', str(self.ticket_layout.ticket_spacing))
        table.add_row('Element label width', str(self.ticket_layout.label_width))
        table.add_row('Cardboard element label', str(self.ticket_layout.cardboard_label))
        table.add_row('Paper element label', self.ticket_layout.paper_label)
        table.add_row('Buckram element label', self.ticket_layout.buckram_label)
        table.add_row('Backcard element label', self.ticket_layout.backcard_label)

        console = Console()
        print()
        console.print(table)
        print()


# The BOOKY_CONFIG object holds all the configuration info
# and the validation constraints. This is a global object
# created at runtime.

# You must create the one and only BOOKY_CONFIG
# instance before using Pub and PubDB.
# This can throw exceptions so we check them
# whenever we import this module.

CONFIG_FILENAME = "configure.toml"

with open(CONFIG_FILENAME, 'rb') as f:
        data = load(f)
        BOOKY_CONFIG = BookyConfig.model_validate(data)
        BOOKY_CONFIG.config_filename = CONFIG_FILENAME


