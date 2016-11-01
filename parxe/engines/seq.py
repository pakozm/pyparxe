# -*- coding: utf-8 -*-
"""Summary"""

import os

import nanomsg as nmsg
import parxe.common as common

from parxe.engines import EngineInterface
from parxe.common import Singleton, overrides, serialize, deserialize

@Singleton
class SeqEngine(EngineInterface):
    """Sequential engine class"""

    def __init__(self):
        """Initializes the engine.

        This method is not callable directly because this class is a
        singleton, you should use get_instance() instead"""

        # hash_value is used for identification of this engine client
        # connections
        tmpfile, hash_value = common.mktempfile()
        self._tmpfile = tmpfile
        self._hash = hash_value
        # The URI describes how nanomsg will connect to this engine
        self._uri = "inproc://" + self._hash
        self._results = []
        # Forward declaration of server socket and binded endpoint identifier,
        # for attention of the reader.
        self._server = None
        self._server_endpoint = None
        self._client = None
        self._client_endpoint = None
        # FIXME: Are this two properties required by this object???
        self._server_url = None
        self._client_url = None

    @overrides(EngineInterface)
    def connect(self):
        if self._server is None:
            self._server = nmsg.Socket(nmsg.REP)
            self._server_endpoint = self._server.bind(self._uri)
            self._client = nmsg.Socket(nmsg.REQ)
            self._client_endpoint = self._client.connect(self._uri)
        return self._server

    @overrides(EngineInterface)
    def abort(self, task):
        """Aborts the given task id"""
        raise NotImplementedError

    @overrides(EngineInterface)
    def execute(self, task, stdout, stderr):
        os.chdir(task.wd)
        func = task.func
        args = task.args
        kwargs = task.kwargs
        result = func(*args, **kwargs)
        open(stdout, "w").close()
        open(stderr, "w").close()
        serialize({"id":task.id, "result":result,
                   "hash":self._hash, "reply":True},
                  self._client)

    @overrides(EngineInterface)
    def finished(self, task):
        _ = deserialize(self._client)

    @overrides(EngineInterface)
    def accepting_tasks(self):
        return True

    @overrides(EngineInterface)
    def get_max_tasks(self):
        return 1
    
def get_instance():
    """Wrapper of SeqEngine.get_instance()"""
    return SeqEngine.get_instance()
