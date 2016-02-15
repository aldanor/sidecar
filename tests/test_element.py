# -*- coding: utf-8 -*-

from pytest import raises_str

from sidecar.element import Element, expr
from sidecar import tags


class Tag(Element):
    allow_children = False

    def __init__(self, id, a, b, c=None):
        super(Tag, self).__init__('Tag', inputs=[id], props={'a': a, 'b': b, 'c': c})

    def _convert_props(self, a, b, c=None):
        props = {'_a': a, '_b': b}
        if c is not None:
            props['_c'] = c
        return props


class Container(Element):
    def __init__(self, inputs=None, outputs=None, **props):
        super(Container, self).__init__('Container', inputs, outputs, props)


class TestElement(object):
    def test_expr(self):
        raises_str('invalid expr: 1', expr, 1)
        raises_str("invalid expr: ''", expr, '')
        assert expr(expr('foo')) == expr('foo')
        assert str(expr('bar')) == 'bar'
        assert repr(expr('bar')) == "expr('bar')"
        assert expr('baz').code == 'baz'

    def test_repr(self):
        assert repr(tags.del_()) == '<Element: del>'
        assert repr(Container(['a'])['foo']) == '<Element: Container>'

    def test_basic(self):
        assert not Tag.allow_children
        tag = Tag('id', 'a', 'b')
        assert tag.name == 'Tag'
        assert tag.inputs == ['id']
        assert tag.outputs == []
        assert tag.children == []
        assert tag.props == {'_a': 'a', '_b': 'b'}

        container = Container(outputs=['b'], foo=1)[tags.p(href='foo'), Container(['a'])]
        assert Container.allow_children
        assert container.name == 'Container'
        assert container.inputs == []
        assert container.outputs == ['b']
        assert container.props == {'foo': 1}
        assert container.children == [tags.p(href='foo'), Container(['a'])]
