#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Summary

Description
"""

__version__ = '0.1.0'

__author__ = 'Francisco Zamora-Martinez'
__copyright__ = 'Copyright 2016, Francisco Zamora-Martinez'
__credits__ = []
__license__ = 'MIT'
__maintainer__ = 'Francisco Zamora-Martinez'
__email__ = 'pakozm@gmail.com'
__status__ = 'Development' # Production when ready for it

import os

from ConfigParser import ConfigParser

import parxe.engines.seq
import parxe.engines.local

# from parxe.planner import planner
# from parxe.dmap import dmap
from parxe.common import Singleton, cache

DEFAULT_CONFIG_FOLDER = '.pyparxe'
DEFAULT_CONFIG_FILENAME = 'config.ini'
MAIN_SECTION = 'main'
ENGINE_OPTION = 'engine'

DEFAULT_CONFIG_PATH = os.path.join(
    os.getenv('HOME', '/etc/'),
    DEFAULT_CONFIG_FOLDER,
    DEFAULT_CONFIG_FILENAME,
)

CONFIG_DEFAULTS = {
    ENGINE_OPTION : parxe.engines.seq.get_instance,
}

ENGINES = {
    'seq' : parxe.engines.seq.get_instance,
    # 'local' : parxe.engines.local.get_instance,
}

@Singleton
class Configuration(object):
    def __init__(self):
        self._engine = None

    # TODO: Control engine set when it has been started
    def set_engine(self, engine):
        """Sets the engine given the engine string"""
        self._engine = ENGINES[engine]()

    @property
    def engine(self):
        """Returns engine instance of class EngineInterface"""
        return self._engine

def _as_dict(options_list):
    """Builds a disctionary from a list of key,value option pairs"""
    return {key: value for key, value in options_list}

def _construct_config_parser(config_path):
    reader = ConfigParser(default=CONFIG_DEFAULTS)
    reader.read(config_path)
    return reader

def _load_configuration(config_path=DEFAULT_CONFIG_PATH,
                        engine=None):
    """Loads the configuration stored at config_path

    The engine argument allow to overwrite its corresponding option.
    """
    reader = cache(_construct_config_parser, config_path)
    if engine is not None:
        assert isinstance(engine, str), "engine should be a string"
        reader.set(MAIN_SECTION, engine)
        engine_str = engine
    else:
        engine_str = reader.get(MAIN_SECTION, ENGINE_OPTION)
    conf = Configuration.get_instance()
    conf.set_engine(engine_str)
    conf.engine.set_options(_as_dict(reader.items(engine_str)))

def start(config_path=DEFAULT_CONFIG_PATH, engine=None):
    """Starts the parallel tasks planner with an optionally given engine.

    Parameters
        engine : string
        config_path : string

    In case it has been started, this method will throw an
    error. Otherwise, the planner will be started using the engine given
    at set_engine() method or the default selected engine.
    The engine cannot be changed after start() call, unless calling
    stop() function.
    """
    _load_configuration(config_path, engine)
    planner.start(engine=Configuration.get_instance().engine)

def stop():
    """Stops the planner process.
    
    No more parallel executions will be possible unless calling
    again start() function. Stopping allows to change the engine
    by means of set_engine() method.
    """
    planner.stop()
