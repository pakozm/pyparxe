# -*- coding: utf-8 -*-
import cPickle as pkl
import logging as log
import os

from time import time
from unittest import TestCase
from mock import MagicMock, patch

import parxe.tests # should be imported before parxe for proper mocking
import parxe.common as common

OBJ = {"id":4, "data":"datum"}
DUMMY_FILENAME = "/tmp/dummy"
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

        class ConcreteImplementer(BaseInterface):
            @common.overrides(BaseInterface)
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

        with f_handler:
            self.assertTrue(f_hash in f_handler.name)

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
        self.filename = DUMMY_FILENAME
        log.basicConfig(level=log.ERROR)

    def tearDown(self):
        log.basicConfig(level=log.INFO)

    def test_wait_until_exists(self):
        t0 = time()
        with patch('os.path.isfile', MagicMock(return_value=False)):
            result = common.wait_until_exists(self.filename,
                                              timeout=0.01,
                                              wait_step=0.001)

        self.assertFalse(result)

        with patch('os.path.isfile', MagicMock(return_value=True)):
            result = common.wait_until_exists(self.filename)

        self.assertTrue(result)
        self.assertTrue((time() - t0) < 0.04)

class TestCache(TestCase):
    def test_cache_call(self):
        arg = 12
        return_value = 144
        func = MagicMock(return_value=return_value)

        result = common.cache(func, arg)

        func.assert_called_once_with(arg)
        self.assertEqual(result, return_value)
        func.reset_mock()

        result = common.cache(func, arg)

        func.assert_not_called()
        self.assertEqual(result, return_value)
