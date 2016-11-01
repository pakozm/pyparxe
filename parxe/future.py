# -*- coding: utf-8 -*-
"""This module implements Future base class and its subclasses.

Future objects are the result of asynchronous functions execution. Their
value is unknown at construction, so they offer an interface for gathering
this value when it is computed, or wait until it is available."""

import operator
import threading

from parxe.common import overrides, wait_until_exists

PENDING_STATE = "pending"
RUNNING_STATE = "running"
FINISHED_STATE = "finished"

def _cast(obj):
    """Casts non Future objects to NonFuture."""
    if isinstance(obj, Future):
        return obj
    else:
        return NonFuture(obj)

def _thread_run_for_result(future, func, *args):
    """This function executes func(*args) and stores
    its result by means of future.set_result() method."""
    result = func(future, *args)
    future._set_result(result)

class Future(object):
    """Future class for result of parallel functions execution.

    Instances of this class execute do_work function given in the
    constructor using a dedicated Python thread (from threading
    library). The do_work function has the responsability of
    indicating the running state of the object by calling
    set_as_running() method. This do_work function receives
    as arguments the future object and a variable list of arguments
    given to __init__ constructor.
    
    Example:

    >>> def square(self, x):
    ...     self.set_as_running()
    ...     return x**2
    >>> fut = Future(square, 4)
    >>> fut.get()
    16
    """

    def __init__(self, do_work, *args):
        """do_work(self, *args) will be executed in a Python thread."""
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
        """Changes the state of the object from pending to running.
        
        This method should be called by do_work function."""
        with self._running_condition:
            assert self._state == PENDING_STATE
            self._state = RUNNING_STATE
            self._running_condition.notify()

    def abort(self):
        """Aborts the computation of this future."""
        raise NotImplementedError

    def get(self):
        """Waits until the future is finished and returns the result
        of this execution.

        If the object is in finished state, this method returns the
        result without any waiting.
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

    def _set_result(self, value):
        """Calling this method stores the result in the future object.

        Besides, this method sets the future state to finished. This
        method is called by the thread target function and should not
        be called by anyone else out of this module.
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
        """Represents a future with a string as:
        Future in RUNNING state
        """
        return "Future in {} state".format(self._state.upper())

    def after(self, func):
        """Appends the execution of a function over the output of this Future.
        
        The function will be called as func(self.get()) when the result of this
        Future is ready.
        """
        return ConditionedFuture(func, self)

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
    """A Future class intended to execution of delayed functions.

    The function computation is delayed until all the arguments
    given in the constructor are finished. It allow to mix together
    Future and non Future objects.
    """
    def __init__(self, func, *args):
        super(ConditionedFuture, self)\
        .__init__(
            _conditioned_do_work,
            func,
            *args
        )

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
        values[i] = _cast(val).get()
    return values

class UnionFuture(Future):
    """A Future over a list of Futures.

    The result of this Future is a list of values.
    """
    def __init__(self, args_list):
        super(UnionFuture, self).__init__(_union_do_work, args_list)
        self._args_list = args_list

    @overrides(Future)
    def get_stdout(self):
        """The stdout is the concatenation of every Future in the list."""
        stdout = [val.get_stdout() for val in self._args_list]
        return '\n'.join(stdout)

    @overrides(Future)
    def get_stderr(self):
        """The stderr is the concatenation of every Future in the list."""
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
    """A fake one wrapping a non future object.

    This class is useful to mix together Future and NonFuture objects."""
    def __init__(self, value):
        super(NonFuture, self).__init__(_non_future_do_work, value)

    @overrides(Future)
    def abort(self):
        raise NotImplementedError
