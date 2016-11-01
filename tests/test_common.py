# -*- coding: utf-8 -*-
import cPickle as pkl
import unittest
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
        
    def test_serialize(self):
        class MockSocket:
            def __init__(self):
                pass

            def recv(self):
                return pkl.dumps(OBJ)
        obj = common.deserialize(MockSocket())
        self.assertEqual(obj, OBJ)
