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
        """connect() -> A nanomsg SP socket

        Opens the engine connection using nanomsg and returns the
        underlying SP socket for communication.
        """
        raise NotImplementedError
    
    def abort(self, task):
        """abort(task : Task)

        Aborts the given task object
        """
        raise NotImplementedError

    def execute(self, task, stdout_path, stderr_path):
        """execute(task : Task, stdout_path : str, stderr_path : str)
        
        Executes the given task object using as output log the given
        stdout_path and stderr_path
        """
        raise NotImplementedError

    def finished(self, task):
        """finished(task : Task)

        Use this method to indicate the engine that a particular task
        has finished its execution. The scheduler is responsible to call
        this method when the task operation finishes.
        """
        raise NotImplementedError

    def accepting_tasks(self):
        """accepting_tasks() -> boolean
    
        Indicates if this engine accepts more tasks for execution
        """
        raise NotImplementedError

    def get_max_tasks(self):
        """get_max_tasks() -> int
        
        Returns the maximum number of supported concurrent task
        """
        raise NotImplementedError

def get_num_cores():
    """get_num_cores() -> int
    
    Returns the number of cores available in the host.
    """
    with common.popen("getconf _NPROCESSORS_ONLN") as f:
        return int(f.readline().rstrip())
