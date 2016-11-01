# -*- coding: utf-8 -*-
"""Common utilities for PARXE"""

import os
import cPickle as pkl
import tempfile

DEFAULT_POPEN_BUFSIZE = 4096

class Overrides(object):
    """Does nothing, just decorator"""
    def __init__(self, decorated):
        pass

class Singleton(object):
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `get_instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    See http://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons-in-python
    """

    def __init__(self, decorated):
        self._decorated = decorated
        self._instance = None

    def get_instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        if self._instance is None:
            self._instance = self._decorated()
        return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `get_instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
    
def popen(cmd, mode="r"):
    """Executes the given command string using a shell"""
    return os.popen(cmd, mode, DEFAULT_POPEN_BUFSIZE)

def mktempfile():
    """Returns a file handler and its file name hash"""
    f_handler = tempfile.NamedTemporaryFile()
    f_hash = f_handler.name[-6:]
    return f_handler, f_hash

def serialize(obj, socket):
    """Serializes the given object through the given SP socket"""
    socket.send(pkl.dumps(obj))

def deserialize(socket):
    """Deserializes one object from the given SP socket"""
    return pkl.loads(socket.recv())
