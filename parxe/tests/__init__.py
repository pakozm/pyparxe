# -*- coding: utf-8 -*-
import sys

sys.modules['nanomsg'] = __import__(
    'parxe.tests.nanomsg_mock',
    globals(),
    locals(),
    ['Socket'],
    -1,
)
