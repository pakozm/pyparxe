# -*- coding: utf-8 -*-
import sys

sys.modules['nanomsg'] = __import__(
    'tests.nanomsg_mock',
    globals(),
    locals(),
    ['Socket'],
    -1
)
