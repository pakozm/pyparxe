# -*- coding: utf-8 -*-
import cPickle as pkl
import unittest
import sys

from unittest import TestCase
from mock import mock_open, patch, MagicMock, Mock

import nanomsg as nmsg
import parxe.engines.seq as seq_engine

from parxe.task import Task
from parxe.common import deserialize

ID = 0
STDOUT = "/dev/null"
STDERR = "/dev/null"

class TestSeqEngine(TestCase):

    def setUp(self):
        self.engine = seq_engine.get_instance()
        self.server_mock = Mock()
        self.client_mock = Mock()
        self.engine._server = self.server_mock
        self.engine._client = self.client_mock

    def tearDown(self):
        pass

    def test_default_values(self):
        self.assertEqual(len(self.engine._results), 0)

    #def test_connect(self):
    #    socket = self.engine.connect()
    #    self.assertIsInstance(socket, nmsg.Socket)

    def test_execute(self):
        def func(x):
            return x**2
        args = [4]

        self.client_mock.recv = MagicMock(
            return_value=pkl.dumps({
                "id" : ID,
                "reply" : True,
                "hash" : self.engine._hash,
                "result" : func(*args)
            })
        )

        socket = self.engine.connect()
        task = Task(ID, func, args=args)
        self.engine.execute(task, STDOUT, STDERR)
        self.engine.finished(task)

        self.client_mock.send.assert_called_once()
        self.client_mock.recv.assert_called_once()
