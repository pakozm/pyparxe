# -*- coding: utf-8 -*-
"""Common utilities for PARXE"""

import os
import cPickle as pkl
import logging as log
import os
import tempfile

from time import sleep, time

DEFAULT_POPEN_BUFSIZE = 4096
DEFAULT_FILESYSTEM_TIMEOUT = 60 # seconds
DEFAULT_FILESYSTEM_WAIT_STEP = 1 # seconds

def overrides(interface_class):
    """Throws error if the method doesn't exists"""
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

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

def wait_until_exists(filename,
                      timeout=DEFAULT_FILESYSTEM_TIMEOUT,
                      wait_step=DEFAULT_FILESYSTEM_WAIT_STEP):
    """Waits until the given filename exists.

    Depending on NFS synchronization or similar shared disk storage
    drivers, it can be necessary to wait for a filename to exists.
    """

    t0 = time()
    timedout = False
    while not os.path.isfile(filename) and not timedout:
        log.info("Waiting disk sync: %.0f more seconds, %.0f seconds elapsed",
                 wait_step, time() - t0)
        sleep(wait_step)
        if time() - t0 > timeout:
            log.warning("File system wait timedout!")
            timedout = True
        wait_step *= 2.0
    return not timedout
