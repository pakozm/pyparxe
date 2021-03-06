# -*- coding: utf-8 -*-
"""This module implements Task class."""

class Task(object):
    """This class is intented as a simple container of data.
    
    It principal attributes are an id value, the working directory in the
    worker host, the function to be executed, and the args and kwargs required
    by the function. Finally, the result of the operation will be also tracked
    by instances of this class."""
    def __init__(self, id, func, working_dir="./", args=[], kwargs={}):
        self._id = id
        self._working_dir = working_dir
        self._func = func
        self._args = args
        self._kwargs = kwargs

    @property
    def wd(self):
        return self._working_dir

    @property
    def func(self):
        return self._func

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def id(self):
        return self._id

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
