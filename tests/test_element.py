# -*- coding: utf-8 -*-

from pytest import raises_regexp

from sidecar.element import expr


class TestElement(object):
    def test_expr(self):
        raises_regexp(Exception, 'invalid expr: 1', expr, 1)
        raises_regexp(Exception, "invalid expr: ''", expr, '')
        assert expr(expr('foo')) == expr('foo')
        assert str(expr('bar')) == 'bar'
        assert repr(expr('bar')) == "expr('bar')"
        assert expr('baz').code == 'baz'
