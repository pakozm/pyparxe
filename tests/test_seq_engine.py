# -*- coding: utf-8 -*-
import unittest
import sys

import tests

import nanomsg as nmsg
import parxe.engines.seq as seq_engine

from unittest import TestCase
# from mock import MagicMock
from parxe.task import Task
from parxe.common import deserialize

ID = 0
STDOUT = "/dev/null"
STDERR = "/dev/null"

class TestSeqEngine(TestCase):

    def setUp(self):
        self.engine = seq_engine.get_instance()

    def tearDown(self):
        pass

    def test_default_values(self):
        self.assertEqual(len(self.engine._results), 0)

    def test_connect(self):
        socket = self.engine.connect()
        self.assertIsInstance(socket, nmsg.Socket)

    def test_execute(self):
        socket = self.engine.connect()
        def func(x):
            return x**2
        args = [4]
        task = Task(ID, func, args=args)
        self.engine.execute(task, STDOUT, STDERR)
        output = deserialize(self.engine._client)

        self.assertEqual(output["id"], ID)
        self.assertTrue(output["reply"])
        self.assertEqual(output["hash"], self.engine._hash)
        self.assertEqual(output["result"], func(*args))

        self.engine.execute(task, STDOUT, STDERR)
        self.engine.finished(task)

        self.assertEqual(len(nmsg.STREAMS[socket.uri]), 0)
