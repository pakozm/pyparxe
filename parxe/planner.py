# -*- coding: utf-8 -*-
"""This module implements Planner class."""

from parxe.common import Singleton, serialize, deserialize

@Singleton
class Planner(object):
    """This class purpose is to instantiate a singleton object

    which allow to enqueue tasks for execution.

    The planner depends on how a particularly chosen engine executes
    the tasks in a particular worker host. When a task is enqueued,
    a Task object is constructed and a future is returned. This future
    allow to control the operation result in an asynchronous way.
    """

    def __init__(self):
        # Used in nmsg.poll() function
        self._poll_fds = {}
        # A dictionary indexed by task id with futures related to run
        # tasks
        self._pending_futures = {}
        self._pending_tasks = []
        
