# -*- coding: utf-8 -*-
"""This module implements base class for engine objects in PARXE and other
common utilities.

Every engine is implemented in its own Python module inside parxe.engines
path. The module should declare a singleton instance for the corresponding
engine. Engines API is known by parxe.Scheduler, being the later responsible for
resource acounting, engine execution, task serialization, reply deserialization,
etc."""

import parxe.common as common

class EngineInterface(object):
    """This class is the base interface for engines in PARXE"""

    def __init__(self):
        pass

    def connect(self):
        """Opens a server connection using nanomsg and returns the socket"""
        raise NotImplementedError
    
    def abort(self, task):
        """Aborts the given task object"""
        raise NotImplementedError

    def execute(self, task, stdout, stderr):
        """Executes the given task object gathering output log into stdout and stderr"""
        raise NotImplementedError

    def finished(self, task):
        """Indicates if the given task object has finished or not"""
        raise NotImplementedError

    def accepting_tasks(self):
        """Indicates if this engine accepts more tasks for execution"""
        raise NotImplementedError

    def get_max_tasks(self):
        """Returns the maximum number of supported concurrent task"""
        raise NotImplementedError

def get_num_cores():
    """Returns the number of cores available in the host"""
    with common.popen("getconf _NPROCESSORS_ONLN") as f:
        return int(f.readline().rstrip())
