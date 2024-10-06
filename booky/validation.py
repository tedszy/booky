# validation.py


from typing import List, Dict
from tomllib import load, TOMLDecodeError
from pydantic import BaseModel, ValidationError, Field 
from pydantic import ConfigDict, field_validator
from .config import CONFIG_FILENAME


def check_limits(limits, desc):
    if not len(limits)==2:
        raise ValueError(f"desc must have length 2, given: {limits}.")
    a, b = limits
    if not (a>0 and b> 0 and (limits[0]<limits[1])):
        raise ValueError(f"{desc} must be [a, b] with 0 < a < b.")
    else:
        return limits


# Validate the publication validation constraints 
# specified in the configure.toml file.


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


# The BOOKY_CONFIG object holds all the configuration info
# and the validation constraints. This is a global object
# created at runtime.


class BookyConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # Might need this.
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


# You must create the one and only BOOKY_CONFIG
# instance before using Pub and PubDB.
# This can throw exceptions so we check them
# whenever we import this module.


with open(CONFIG_FILENAME, 'rb') as f:
        data = load(f)
        BOOKY_CONFIG = BookyConfig.model_validate(data)


# Pub is the class for instances that hold bookbinding 
# data about a single publication.


class Pub(BaseModel):
    title: str
    block_height: int = Field(alias='block-height')
    block_width: int = Field(alias='block-width')
    cover_height: int = Field(alias='cover-height')
    cover_width: int = Field(alias='cover-width')
    color: str

    @field_validator('color')
    @classmethod
    def valid_color(cls, color):
        if not BOOKY_CONFIG.good_color(color):
            raise ValueError(f'Bad color: {color}')
        else:
            return color

    @field_validator('block_height')
    @classmethod
    def valid_block_height(cls, block_height):
        if not BOOKY_CONFIG.good_block_height(block_height):
            raise ValueError(f'Bad block_height: {block_height}, limits: {BOOKY_CONFIG.pub_validation.block_limits}')
        else:
            return block_height

    @field_validator('block_width')
    @classmethod
    def valid_block_width(cls, block_width):
        if not BOOKY_CONFIG.good_block_width(block_width):
            raise ValueError(f'Bad block_width: {block_width}, limits: {BOOKY_CONFIG.pub_validation.block_limits}')
        else:
            return block_width

    @field_validator('cover_height')
    @classmethod
    def valid_cover_height(cls, cover_height):
        if not BOOKY_CONFIG.good_cover_height(cover_height):
            raise ValueError(f'Bad cover_height: {cover_height}, limits: {BOOKY_CONFIG.pub_validation.cover_limits}')
        else:
            return cover_height

    @field_validator('cover_width')
    @classmethod
    def valid_cover_width(cls, cover_width):
        if not BOOKY_CONFIG.good_cover_width(cover_width):
            raise ValueError(f'Bad cover_width: {cover_width}, limits: {BOOKY_CONFIG.pub_validation.cover_limits}')
        else:
            return cover_width


# PubDB is the dictionary of all publications.
# It is loaded from pubs.toml (or the file defined in configure.toml)
# and validated with the above pydantic models.


class PubDB(BaseModel):
    data: Dict[str, Pub]




