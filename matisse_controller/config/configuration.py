import copy
import json
import operator
from functools import reduce
from os import path

CONFIGURATION = {}
DEFAULTS = {
    'matisse': {
        'device_id': 'USB0::0x17E7::0x0102::07-40-01::INSTR',
        'wavelength': {
            'lower_limit': 700,
            'upper_limit': 800
        },
        'scanning': {
            'birefringent_filter': {
                'range': 400,
                'range_small': 200,  # TODO: Check the 'small' scan ranges
                'step': 4,
                'show_plots': True,
                'smoothing_filter': {
                    'window': 31,
                    'polyorder': 3
                }
            },
            'thin_etalon': {
                'range': 2000,
                'range_small': 1000,
                'step': 20,
                'nudge': 50,  # TODO: Confirm this parameter is ok to use, flank seems to default to 'left'?
                'show_plots': True,
                'smoothing_filter': {
                    'window': 21,
                    'polyorder': 3
                }
            },
            'refcell': {
                'rising_speed': 0.005,
                'falling_speed': 0.005
            },
            'wavelength_drift': {
                'large': 0.3,
                'medium': 0.1,
                'small': 0.02
            },
        },
        'locking': {
            'timeout': 7.0
        },
        'stabilization': {
            'rising_speed': 0.005,
            'falling_speed': 0.005,
            'delay': 0.5,
            'tolerance': 0.0005
        },
        'correction': {
            'piezo_etalon_pos_upper': 0.8,
            'slow_piezo_pos_upper': 0.5,  # TODO: Not used yet
            'refcell_pos_upper': 0.5,
            'piezo_etalon_pos_mid': 0.0,
            'slow_piezo_pos_mid': 0.35,
            'refcell_pos_mid': 0.35,  # TODO: Not used yet
            'piezo_etalon_pos_lower': -0.8,
            'slow_piezo_pos_lower': 0.2,  # TODO: Not used yet
            'refcell_pos_lower': 0.2
        }
    },
    'wavemeter': {
        'port': 'COM5',
        'precision': 3
    },
    'gui': {}
}


def get(name: str):
    """Fetch the global configuration value represented by the specified name."""
    keys = name.split('.')
    return reduce(operator.getitem, keys, CONFIGURATION)


def set(name: str, value):
    """Set the global configuration value represented by the specified name."""
    keys = name.split('.')
    cfg = CONFIGURATION
    for key in keys[:-1]:
        cfg = cfg.get(key)
    cfg[keys[-1]] = value


def load(filename: str):
    """Load configuration data from a file into the global configuration dictionary."""
    with open(filename, 'r') as config_file:
        global CONFIGURATION
        CONFIGURATION = json.load(config_file)


def save():
    """Save the global configuration data to a config.json file."""
    with open('config.json', 'w') as config_file:
        json.dump(CONFIGURATION, config_file, indent=4)


def restore_defaults():
    """Overwrite the global configuration with the defaults, specified by configuration.DEFAULTS."""
    global CONFIGURATION
    CONFIGURATION = copy.deepcopy(DEFAULTS)


if path.exists('config.json'):
    load('config.json')
else:
    restore_defaults()
