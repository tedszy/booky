
# booky2.py

import tomllib
import logging
import os.path


logger = logging.getLogger('booky')
logging.basicConfig(level=logging.DEBUG)


def check_color(color):
    '''color is 3 character string.'''
    return isinstance(color, str) and len(color)==3


def check_limits(limits):
    '''Sanity check for block and cover limits. '''
    return (len(limits)==2 
            and isinstance(limits[0], int) 
            and isinstance(limits[1], int) 
            and limits[0] < limits[1])


def is_within_limits(x, limits):
    '''limits [a,b], a <= x <= b'''
    return (limits[0] <= x <= limits[1])


def missing_keys(keys_A, keys_B):
    '''Keys in keys_A that do not appear in keys_B.'''
    return [x for x in keys_A if x not in keys_B]


def extra_keys(keys_A, keys_B):
    '''Keys in keys_B that are not in keys_A.'''
    return [x for x in keys_B if x not in keys_A]


class ValidationError(Exception):
    '''Booky configuration or publication validation error.'''

    def __init__(self, message, value, filename=None):
        super().__init__()
        self.message = message
        self.value = value
        self.filename = filename
        if self.filename:
            self.user_message = f"{message} '{value}' in file '{filename}'"
        else:
            self.user_message = f"{message} '{value}'"


class ConfigError(ValidationError):
    '''Bad or missing keys in config file.'''

    def __str__(self):
        return 'ConfigError... ' + self.user_message


class PubError(ValidationError):
    '''Bad publication data.'''

    def __str__(self):
        return 'PubError... ' + self.user_message


class ConfigValidator:
    '''Makes sure configure.toml is sane.'''

    config_filename = 'configure.toml'
    toplevel_keys = ['pub-db-filenames', 'pub-fields', 'validation']
    validation_keys = ['block-limits', 'cover-limits', 'colors'] 

    def __init__(self):

        try:
            with open(self.config_filename, 'rb') as f:
                data = tomllib.load(f)
        except FileNotFoundError as fnf:
            raise ConfigError('config file not found', 
                              self.config_filename, None)
        except tomllib.TOMLDecodeError as tde:
            raise ConfigError('Unreadable TOML in config file', 
                              self.config_filename, None)

        logger.debug(f"{self.config_filename} TOML read ok.")

        # Check toplevel keys.
        missing = missing_keys(self.toplevel_keys, data.keys())
        extra = extra_keys(self.toplevel_keys, data.keys())
        if len(missing) > 0:
            raise ConfigError('Missing toplevel keys', 
                              missing, self.config_filename)
        if len(extra) > 0:
            raise ConfigError('Extra toplevel keys', 
                              extra, self.config_filename)

        logger.debug(f"{self.config_filename} toplevel keys ok.")

        # Check validation keys.
        missing = missing_keys(self.validation_keys, data['validation'].keys())
        extra = extra_keys(self.validation_keys, data['validation'].keys())
        if len(missing) > 0:
            raise ConfigError('Missing validation keys', 
                              missing, self.config_filename)
        if len(extra) > 0:
            raise ConfigError('Extra validation keys', 
                              extra, self.config_filename)

        logging.debug(f"{self.config_filename} validation keys ok.")

        # Check that publication db files exist.
        for filename in data['pub-db-filenames']:
            if not os.path.isfile(filename):
                raise ConfigError("Pub db file doesn't exist:", 
                                  filename, None)

        logging.debug(f"{self.config_filename} pub-db files exist ok.")

        # Check colors.
        for color in data['validation']['colors']:
            if not check_color(color):
                raise ConfigError(f"bad color value", color, self.config_filename)

        logging.debug(f"{self.config_filename} colors are OK.")

        # Check block-limits and cover-limits. 
        block_limits = data['validation']['block-limits']
        if not check_limits(block_limits):
            raise ConfigError("Bad block limits", block_limits, self.config_filename)
        cover_limits = data['validation']['cover-limits']
        if not check_limits(cover_limits):
            raise ConfigError("Bad cover limits", cover_limits, self.config_filename)

        logging.debug(f"{self.config_filename} block and cover limits ok.")

        self.pub_db_filenames = data['pub-db-filenames']
        self.pub_fields = data['pub-fields']
        self.valid_colors = data['validation']['colors']
        self.block_limits = data['validation']['block-limits']
        self.cover_limits = data['validation']['cover-limits']


class Pub:
    '''Each instance holds the bookbinding specs of a publication db entry.'''
    
    def __init__(self, data):
        self.title = data['title']
        self.block_height = data['block-height']
        self.block_width = data['block-width']
        self.cover_heigth = data['cover-height']
        self.cover_width = data['cover-width']
        self.color = data['color']

    def __repr__(self):
        return f"<Pub {self.title}>"


class PubValidator(ConfigValidator):
    '''Validate contents of publication database files.
    Walk through each publication and check the sanity of the 
    values in the data fields against what is specified
    in the configuration file.'''

    unique_keys = []

    def __init__(self):
        super().__init__()
       
        # Maintain a list of publication keys for testing uniqueness.
        self.pub_keys = []

        # Maintain a dict of publication instances.
        self.pubs = {}

        # Go through publication data files and build self.pubs list. 
        # TOML format requires unique keys, so within the file this
        # is guaranteed.
        for filename in self.pub_db_filenames:

            # Check file existence and toml read.
            try:
                with open(filename, 'rb') as f:
                    data = tomllib.load(f)
            except FileNotFoundError:
                raise PubError('Publication db file not found', filename, None)
            except tomllib.TOMLDecodeError:
                raise PubError('Unreadable TOML in Pub db file', filename, None)

            for key, value in data.items():
                # Check for duplicate key.
                if key in self.pub_keys:
                    raise PubError("Duplicate key", key, filename)
                else:
                    # Check that publication field keys are good.
                    # Can make this more specific: show missing or extra field keys.
                    if not set(self.pub_fields)==set(value.keys()):
                        raise PubError("Bad or missing pub field key in", key, filename)
                    
                    # Check if pub color is valid.
                    c = value['color']
                    if c not in self.valid_colors:
                        raise PubError("Bad color", (key, c), filename)
                    
                    # Check if block height is valid.
                    bh = value['block-height']
                    if not is_within_limits(bh, self.block_limits):
                        raise PubError("Block height outside limits:", (key, bh), filename)
                    
                    # Check if block width is valid.
                    bw = value['block-width']
                    if not is_within_limits(bw, self.block_limits):
                        raise PubError("Block width outside limits:", (key, bw), filename)
                    
                    # Check if cover height is valid.
                    ch = value['cover-height']
                    if not is_within_limits(ch, self.cover_limits):
                        raise PubError("Cover height outside limits:", (key, ch), filename)

                    # Check if cover width is valid.
                    cw = value['cover-width']
                    if not is_within_limits(cw, self.cover_limits):
                        raise PubError("Cover height outside limits:", (key, cw), filename)

                    # Checks pass, add key to key cache and Pub object to list..
                    self.pub_keys.append(key)
                    self.pubs[key] = Pub(value)

            logging.debug(f"{filename} pub db entries are OK.")










if __name__ == '__main__':
    try:
        PV = PubValidator()
    except ConfigError as e:
        print(e)
        exit(1)
    except PubError as pe:
        print(pe)
        exit(1)




