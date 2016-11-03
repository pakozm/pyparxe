#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Summary

Description
"""

__version__ = "0.1.0"

__author__ = "Francisco Zamora-Martinez"
__copyright__ = "Copyright 2016, Francisco Zamora-Martinez"
__credits__ = []
__license__ = "MIT"
__maintainer__ = "Francisco Zamora-Martinez"
__email__ = "pakozm@gmail.com"
__status__ = "Development" # Production when ready for it

# from parxe.planner import planner
# from parxe.dmap import dmap

def set_engine(engine):
    """set_engine(EngineInterface)

       Uses the given engine for parallel execution.
    """
    planner.set_engine(engine)

def start():
    """Starts the parallel tasks planner.
    
    In case it has been started, this method will throw an
    error. Otherwise, the planner will be started using the engine given
    at set_engine() method or the default selected engine.
    The engine cannot be changed after start() call, unless calling
    stop() function.
    """
    planner.start()

def stop():
    """Stops the planner process.
    
    No more parallel executions will be possible unless calling
    again start() function. Stopping allows to change the engine
    by means of set_engine() method.
    """
    planner.stop()

