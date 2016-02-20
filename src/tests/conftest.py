# -*- coding: utf-8 -*-

import re
import pytest


def raises_str(*args, **kwargs):
    args = list(args)
    if not isinstance(args[0], type):
        args = [Exception] + args
    args[1] = re.escape(args[1])
    return pytest.raises_regexp(*args, **kwargs)


def pytest_namespace():
    return {'raises_str': raises_str}
