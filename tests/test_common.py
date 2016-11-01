# -*- coding: utf-8 -*-
import cPickle as pkl
import logging as log
import os

from time import time
from unittest import TestCase
from mock import MagicMock

import parxe.common as common

OBJ = {"id":4, "data":"datum"}
HELLO_WORLD_STR = "Hello World!"

@common.Singleton
class SingletonClass(object):
    def __init__(self):
        pass

class TestSingleton(TestCase):

    def test_init_exception(self):
        with self.assertRaises(TypeError):
            obj = SingletonClass()

    def test_get_instance(self):
        obj1 = SingletonClass.get_instance()
        obj2 = SingletonClass.get_instance()
        self.assertEqual(obj1, obj2)


class TestOverrides(TestCase):

    def test_overrides(self):
        class BaseInterface(object):
            def __init__(self):
                pass
            def foo(self):
                pass
        with self.assertRaises(AssertionError):
            class ConcreteFaultyImplementer(BaseInterface):
                @common.overrides(BaseInterface)
                def bar(self):
                    pass

class TestCommonFunctions(TestCase):

    def test_popen(self):
        with common.popen("echo '%s'" % HELLO_WORLD_STR) as f_cmd:
            hello_world_str = f_cmd.readline().rstrip()
            self.assertEqual(hello_world_str, HELLO_WORLD_STR)

    def test_mktempfile(self):
        f_handler, f_hash = common.mktempfile()
        self.assertTrue(f_hash in f_handler.name)
        f_handler.close()

    def test_serialize(self):
        class MockSocket:
            def __init__(self):
                self.data = None
            def send(self, data):
                self.data = data
        socket = MockSocket()
        common.serialize(OBJ, socket)
        self.assertEqual(socket.data, pkl.dumps(OBJ))

    def test_deserialize(self):
        class MockSocket:
            def __init__(self):
                pass

            def recv(self):
                return pkl.dumps(OBJ)
        obj = common.deserialize(MockSocket())
        self.assertEqual(obj, OBJ)

class TestWaitUntilExists(TestCase):
    def setUp(self):
        self.isfile = os.path.isfile
        self.filename = "/tmp/dummy"
        os.path.isfile = MagicMock()
        log.basicConfig(level=log.ERROR)

    def tearDown(self):
        os.path.isfile = self.isfile
        log.basicConfig(level=log.INFO)

    def test_wait_until_exists(self):
        t0 = time()
        os.path.isfile.return_value = False
        result = common.wait_until_exists(self.filename,
                                          timeout=0.01,
                                          wait_step=0.001)

        self.assertFalse(result)

        os.path.isfile.return_value = True
        result = common.wait_until_exists(self.filename,
                                          timeout=0.1,
                                          wait_step=0.01)

        self.assertTrue(result)
        self.assertTrue((time() - t0) < 0.02)
