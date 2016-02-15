# -*- coding: utf-8 -*-

import json
import pytest

from sidecar.element import Element, expr
from sidecar import tags


class Tag(Element):
    allow_children = False

    def __init__(self, id, a, b=None):
        super(Tag, self).__init__('Tag', inputs=[id], props={'a': a, 'b': b})

    def _convert_props(self, a, b=None):
        props = {'_a': a}
        if b is not None:
            props['_b'] = b
        return props


class Container(Element):
    def __init__(self, x, inputs=None, outputs=None, **props):
        props['x'] = x
        super(Container, self).__init__('Container', inputs, outputs, props)


class IO(Element):
    allow_children = False

    def __init__(self):
        super(IO, self).__init__('IO', inputs=['i'], outputs=['o'])


class TestElement(object):
    def test_expr(self):
        pytest.raises_str('invalid expr: 1', expr, 1)
        pytest.raises_str("invalid expr: ''", expr, '')
        assert expr(expr('foo')) == expr('foo')
        assert str(expr('bar')) == 'bar'
        assert repr(expr('bar')) == "expr('bar')"
        assert expr('baz').code == 'baz'

    def test_repr(self):
        assert repr(tags.del_()) == '<Element: del>'
        assert repr(Container(['a'])['foo']) == '<Element: Container>'

    def test_basic(self):
        assert not Tag.allow_children
        tag = Tag('id', 'a')
        assert tag.name == 'Tag'
        assert tag.inputs == ['id']
        assert tag.outputs == []
        assert tag.children == []
        assert tag.props == {'_a': 'a'}

        container = Container('x', outputs=['b'], foo=1)[tags.p(href='foo'), Container('y')]
        assert Container.allow_children
        assert container.name == 'Container'
        assert container.inputs == []
        assert container.outputs == ['b']
        assert container.props == {'foo': 1, 'x': 'x'}
        assert container.children == [tags.p(href='foo'), Container('y')]

    def test_allow_children(self):
        pytest.raises_str('not a container: Tag', lambda: Tag('i', 'a')['foo'])
        pytest.raises_str('not a container: hr', lambda: tags.hr['foo'])
        pytest.raises_str('not a container: hr', lambda: tags.hr(href='bar')['foo'])

    def test_getitem(self):
        assert Container('x')['foo', 'bar', 'baz'].children == ['foo', 'bar', 'baz']
        pytest.raises_str(TypeError, 'argument', lambda: Container['foo'])
        assert tags.p['foo'].children == ['foo']
        assert tags.p[('foo', 'bar')] == tags.p['foo', 'bar']
        assert tags.p['x', expr('y'), tags.hr, IO()].children == ['x', expr('y'), tags.hr, IO()]
        pytest.raises_str('unexpected child element: []', lambda: tags.p[[]])

    def test_input_overlap(self):
        with pytest.raises_str("overlapping inputs: ['j']"):
            tags.p[
                Container('x', inputs=['a'])[
                    Tag('i', 'a', b={'foo': Tag('j', 'b')}),
                    'foo'
                ],
                Container('y', inputs=['j'])
            ]
        with pytest.raises_str("overlapping inputs: ['i']"):
            tags.p[IO, IO()]

    def test_all_inputs(self):
        element = Container('x', inputs=['a', 'b'])[
            IO,
            Tag('j', a={'x': [1, Tag('k', 'foo')]})
        ]
        assert element.all_inputs == ['a', 'b', 'i', 'j', 'k']

    def test_all_outputs(self):
        element = Container('x', outputs=['a', 'b'])[
            Tag('j', a={'x': [1, IO]}),
            Container('y', outputs=['a', 'b', 'c'])['foo']
        ]
        assert element.all_outputs == ['a', 'b', 'c', 'o']

    @pytest.mark.parametrize('element, expected', [
        (
            tags.p(),
            {'name': 'p'}
        ),
        (
            tags.p[tags.hr, tags.br()],
            {
                'name': 'p',
                'children': [
                    {'__element__': {'name': 'hr'}},
                    {'__element__': {'name': 'br'}}
                ]
            }
        ),
        (
            Container('x', inputs=['a'], outputs=['b'], foo='bar')[
                IO,
                Tag('j', 'a', b='b'),
                tags.p(style={'z-index': 1}, class_='baz')[expr('x'), 'y']
            ],
            {
                'name': 'Container',
                'inputs': ['a'],
                'outputs': ['b'],
                'props': {'x': 'x', 'foo': 'bar'},
                'children': [
                    {'__element__': {
                        'name': 'IO',
                        'inputs': ['i'],
                        'outputs': ['o']
                    }},
                    {'__element__': {
                        'name': 'Tag',
                        'inputs': ['j'],
                        'props': {'_a': 'a', '_b': 'b'}
                    }},
                    {'__element__': {
                        'name': 'p',
                        'props': {'style': {'zIndex': 1}, 'className': 'baz'},
                        'children': [{'__expr__': 'x'}, 'y']
                    }}
                ]
            }
        )
    ], ids=list(map(str, range(3))))
    def test_to_json_or_dict(self, element, expected):
        assert element.to_dict()['__element__'] == expected
        assert element.to_json() == json.dumps({'__element__': expected}, indent=4, sort_keys=True)

    def test_encode_invalid(self):
        pytest.raises_str('not JSON serializable', Container(object()).to_json)
        pytest.raises_str('not JSON serializable', Container(object()).to_dict)
