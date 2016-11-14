# -*- coding: utf-8 -*-
import os
import sys
import unittest

import numpy as np

from unittest import TestCase
from mock import mock_open, patch, MagicMock

import parxe as px
import parxe.engines.seq as seq_engine

class TestMap(TestCase):
    def setUp(self):
        px.set_engine(seq_engine.get_instance())
        px.start()

    def tearDown(self):
        px.stop()

    def test_list_dmap(self):
        def func(x):
            return 2*x
        in_list = range(10000)
        expected_result = map(func, in_list)
        result = px.dmap(func, in_list).get()
        self.assertEqual(expected_result, result)
