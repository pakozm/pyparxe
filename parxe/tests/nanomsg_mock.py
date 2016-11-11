# -*- coding: utf-8 -*-

REP=0
REQ=1

STREAMS = {}

class Socket(object):
    def __init__(self, *args, **kwargs):
        self.uri = None

    def bind(self, uri, *args, **kwargs):
        self.uri = uri

    def connect(self, uri, *args, **kwargs):
        self.uri = uri

    def send(self, msg, *args, **kwargs):
        STREAMS.setdefault(self.uri, []).append(msg)

    def recv(self, *args, **kwargs):
        return STREAMS[self.uri].pop(0)
