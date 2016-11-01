# -*- coding: utf-8 -*-
"""This module implements Future base class and other subclasses.

Future objects are the result of executing parallel functions. They doesn't
contain any value, but the application can be stopped waiting the value in case
it is necessary. This objects wrap some data needed to check when the result is
available. A function is given during construction to allow future object
adaptation to different parallel engines.  """

import operator
import threading

from parxe.common import overrides, wait_until_exists

PENDING_STATE = "pending"
RUNNING_STATE = "running"
FINISHED_STATE = "finished"

def _cast(obj):
    if isinstance(obj, Future):
        return obj
    else:
        return NonFuture(obj)

def _thread_run_for_result(future, func, *args):
    """This function executes func(*args) and stores
    its result by means of future.set_result() method."""
    result = func(future, *args)
    future.set_result(result)

class Future(object):
    """Future class for result of parallel functions execution."""

    def __init__(self, do_work, *args):
        """do_work(*args) will be executed in a Python thread.

        This constructor prepares the object and executes the thread.
        It is responsability of do_work function to indicate when the
        future object is in running state (calling to set_as_running()
        method).
        """
        self._result = None
        self._stdout = None
        self._stderr = None
        self._state = PENDING_STATE
        self._err = None
        self._out = None
        self._running_condition = threading.Condition()
        self._do_work_thread = threading.Thread(
            target=_thread_run_for_result,
            args=[self, do_work] + list(args),
        )
        self._do_work_thread.run()

    def set_stdout(self, value):
        self._stdout = value

    def set_stderr(self, value):
        self._stderr = value

    def set_as_running(self):
        """Starts execution of thread job.

        When the result is ready (or an error happened), the thread will
        end indicating to the future object that the result is ready.
        """
        with self._running_condition:
            assert self._state == PENDING_STATE
            self._state = RUNNING_STATE
            self._running_condition.notify()

    def abort(self):
        """Aborts the computation of this future."""
        raise NotImplementedError

    def get(self):
        """Waits until the future is finished and
        returns the result of this execution.

        In case the thread was joined previously, this method just
        returns the result without any waiting.
        """
        if not self.finished():
            self.wait()
        return self._result

    def wait(self, timeout=None):
        """Waits until the given timeout.

        If timeout=None, it will wait forever. This function returns a
        boolean when the result is ready and the future finished.

        When the timeout argument is present and not None, it should be
        a floating point number specifying a timeout for the operation
        in seconds (or fractions thereof).

        Once this method returns True indicating finished state,
        it cannot be called again.
        """
        self._do_work_thread.join(timeout)
        return self.finished()

    def wait_until_running(self, timeout=None):
        """Waits until the future object is in running state.

        When the timeout argument is present and not None, it should be
        a floating point number specifying a timeout for the operation
        in seconds (or fractions thereof).

        This method will return False when finishing because of the timeout.
        """
        if self.pending():
            with self._running_condition:
                self._running_condition.wait(timeout)
        return not self.pending()

    def set_result(self, value):
        """Calling this method stores the result in the future object.

        Besides, this method sets the future state to finished.
        """
        self._result = value
        self._state = FINISHED_STATE

    def finished(self):
        """Indicates if the future is in finished state"""
        return self._state == FINISHED_STATE

    def running(self):
        """Indicates if the future is in running state"""
        return self._state == RUNNING_STATE

    def pending(self):
        """Indicates if the future is in pending state"""
        return self._state == PENDING_STATE

    def get_stderr(self):
        """Reads stderr file content or the error state field."""
        _ = self.get() # force finished wait
        if self._stderr is not None:
            if wait_until_exists(self._stderr):
                with open(self._stderr) as f:
                    self._err = f.read()
        return self._err

    def get_stdout(self):
        """Reads stdout file content or the output state field."""
        _ = self.get() # force finished wait
        if self._stdout is not None:
            if wait_until_exists(self._stdout):
                with open(self._stdout) as f:
                    self._out = f.read()
        return self._out

    def __str__(self):
        return "Future in {} state".format(self._state)

    def after(self, func, *args):
        return ConditionedFuture(func, *args)

    def __add__(self, other):
        return ConditionedFuture(operator.__add__, self, _cast(other))

    def __sub__(self, other):
        return ConditionedFuture(operator.__sub__, self, _cast(other))

    def __mul__(self, other):
        return ConditionedFuture(operator.__mul__, self, _cast(other))

    def __div__(self, other):
        return ConditionedFuture(operator.__div__, self, _cast(other))

    def __pow__(self, other):
        return ConditionedFuture(operator.__pow__, self, _cast(other))

    def __mod__(self, other):
        return ConditionedFuture(operator.__mod__, self, _cast(other))

    def __neg__(self):
        return ConditionedFuture(operator.__neg__, self)

############################
# CONDITIONED FUTURE CLASS #
############################

def _conditioned_do_work(self, func, *args):
    self.set_as_running()
    values = list(args[:])
    for i, val in enumerate(values):
        while isinstance(val, Future):
            val = val.get()
        values[i] = val
    return func(*values)

class ConditionedFuture(Future):
    """A Future object which delays the computation of
    a function which receives Futures as arguments.

    All arguments are not forced to be a Future object.
    """
    def __init__(self, func, *args):
        super(ConditionedFuture, self).__init__(_conditioned_do_work, func,
                                                *args)

    @overrides(Future)
    def abort(self):
        raise NotImplementedError

######################
# UNION FUTURE CLASS #
######################

def _union_do_work(self, args_list):
    self.set_as_running()
    values = list(args_list[:])
    for i, val in enumerate(values):
        values[i] = val.get()
    return values

class UnionFuture(Future):
    """A Future object over a list of Futures."""
    def __init__(self, args_list):
        super(UnionFuture, self).__init__(_union_do_work, args_list)
        self._args_list = args_list

    @overrides(Future)
    def get_stdout(self):
        stdout = [val.get_stdout() for val in self._args_list]
        return '\n'.join(stdout)

    @overrides(Future)
    def get_stderr(self):
        stderr = [val.get_stderr() for val in self._args_list]
        return '\n'.join(stderr)

    @overrides(Future)
    def abort(self):
        raise NotImplementedError


####################
# NON FUTURE CLASS #
####################

def _non_future_do_work(self, value):
    self.set_as_running()
    return value

class NonFuture(Future):
    """A fake Future wrapping a non future object."""
    def __init__(self, value):
        super(NonFuture, self).__init__(_non_future_do_work, value)

    @overrides(Future)
    def abort(self):
        raise NotImplementedError
