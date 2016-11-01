# -*- coding: utf-8 -*-

REP=0
REQ=1

STREAMS = {}

class Socket(object):
    def __init__(self, *args, **kwargs):
        self._uri = None

    def bind(self, uri, *args, **kwargs):
        self._uri = uri

    def connect(self, uri, *args, **kwargs):
        self._uri = uri

    def send(self, msg, *args, **kwargs):
        STREAMS.setdefault(self._uri, []).append(msg)

    def recv(self, *args, **kwargs):
        return STREAMS.setdefault(self._uri, []).pop(0)
