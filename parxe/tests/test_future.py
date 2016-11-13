# -*- coding: utf-8 -*-
import os
import sys
import unittest

from unittest import TestCase
from mock import mock_open, patch, MagicMock

import parxe.tests # should be imported before parxe for proper mocking

from parxe.future import (
    Future,
    ConditionedFuture,
    UnionFuture,
    NonFuture,
)

ARG = 10
DUMMY_STDOUT = "/tmp/dummy_stdout"
DUMMY_STDERR = "/tmp/dummy_stderr"
F1_VALUE = 20
F2_VALUE = 5
DATA='\n'.join([
    "first line",
    "second line",
    "third line",
])

def square(self, x):
    self.set_as_running()
    return x**2

class TestFuture(TestCase):

    def setUp(self):
        self.fut = Future(square, ARG)
        self.fut.set_stdout(DUMMY_STDOUT)
        self.fut.set_stderr(DUMMY_STDERR)

    def tearDown(self):
        pass

    def test_get_stdout(self):
        m = mock_open(read_data=DATA)
        with patch('os.path.isfile', MagicMock(return_value=True)):
            with patch('parxe.future.open', m):
                data = self.fut.get_stdout()
        self.assertEqual(data, DATA)
        m.assert_called_once_with(DUMMY_STDOUT)

    def test_get_stderr(self):
        m = mock_open(read_data=DATA)
        with patch('os.path.isfile', MagicMock(return_value=True)):
            with patch('parxe.future.open', m):
                data = self.fut.get_stderr()
        self.assertEqual(data, DATA)
        m.assert_called_once_with(DUMMY_STDERR)

class TestFutureOperators(TestCase):
    
    def test_add(self):
        f1 = NonFuture(F1_VALUE)
        f2 = NonFuture(F2_VALUE)
        f3 = f1 + f2

        self.assertEqual(f3.get(), F1_VALUE + F2_VALUE)

    def test_sub(self):
        f1 = NonFuture(F1_VALUE)
        f2 = NonFuture(F2_VALUE)
        f3 = f1 - f2

        self.assertEqual(f3.get(), F1_VALUE - F2_VALUE)

    def test_mul(self):
        f1 = NonFuture(F1_VALUE)
        f2 = NonFuture(F2_VALUE)
        f3 = f1 * f2

        self.assertEqual(f3.get(), F1_VALUE * F2_VALUE)
        
    def test_div(self):
        f1 = NonFuture(F1_VALUE)
        f2 = NonFuture(F2_VALUE)
        f3 = f1 / f2

        self.assertEqual(f3.get(), F1_VALUE / F2_VALUE)
        
    def test_mod(self):
        f1 = NonFuture(F1_VALUE)
        f2 = NonFuture(F2_VALUE)
        f3 = f1 % f2

        self.assertEqual(f3.get(), F1_VALUE % F2_VALUE)

    def test_pow(self):
        f1 = NonFuture(F1_VALUE)
        f2 = NonFuture(F2_VALUE)
        f3 = f1 ** f2

        self.assertEqual(f3.get(), F1_VALUE ** F2_VALUE)


class TestUnionFuture(TestCase):

    def test_union_future(self):
        f1 = NonFuture(F1_VALUE)
        f2 = NonFuture(F2_VALUE)
        f3 = UnionFuture([f1, f2])

        self.assertEqual(f3.get(), [F1_VALUE, F2_VALUE])

class TestConditioned(TestCase):

    def test_conditioned(self):
        f1 = ConditionedFuture(lambda a, b: a*b, F1_VALUE, F2_VALUE)
        f2 = ConditionedFuture(lambda a, b: a*b, f1, 2)
        f3 = ConditionedFuture(lambda a, b: a+b, f1, f2)
        f4 = f3 * 4

        expected = 4 * ((F1_VALUE*F2_VALUE) * 2 + (F1_VALUE*F2_VALUE))
        self.assertEqual(f4.get(), expected)
