# -*- coding: utf-8 -*-

import keyword
import re
import pytest

from sidecar.element import Element, expr
from sidecar import tags


@pytest.fixture(scope='module')
def all_tags():
    return [{
        'name': tag,
        'cls': getattr(tags, tag + '_' * keyword.iskeyword(tag)),
        'void': tag in tags._VOID_TAGS
    } for tag in tags._TAGS]


class TestTags(object):
    def test_tags(self, all_tags):
        for tag in all_tags:
            assert issubclass(tag['cls'], Element)
            assert tag['cls'].allow_children == (not tag['void'])
            assert tag['cls'].__doc__ == '<{}> HTML tag.'.format(tag['name'])
            element = tag['cls'](
                is_='foo', form_enc_type='bar', alt='baz', inputMode='qwe', href=expr('x'),
                style={'line-height': 1, 'align_self': 'no', 'flexFlow': 'yes', 'flex': 0}
            )
            assert element.to_dict() == {
                '__element__': {
                    'name': tag['name'],
                    'props': {
                        'is': 'foo',
                        'formEncType': 'bar',
                        'alt': 'baz',
                        'inputMode': 'qwe',
                        'href': {
                            '__expr__': 'x'
                        },
                        'style': {
                            'lineHeight': 1,
                            'alignSelf': 'no',
                            'flexFlow': 'yes',
                            'flex': 0
                        }
                    }
                }
            }
            assert element.name == tag['name']
            assert element.inputs == []
            assert element.outputs == []
            assert element.children == []
            assert element.props['href'] == expr('x')

    def test_void_tags(self, all_tags):
        for tag in all_tags:
            if tag['void']:
                with pytest.raises_regexp(Exception, 'not a container: {}'.format(tag['name'])):
                    tag['cls']['foo']
                with pytest.raises_regexp(Exception, 'not a container: {}'.format(tag['name'])):
                    tag['cls']()['foo']
            else:
                assert tag['cls']['foo', 'bar'] == tag['cls']()['foo', 'bar']

    def test_attributes(self):
        for attr in tags._ATTRIBUTES:
            if attr == 'style':
                continue
            py_attr = attr + '_' * keyword.iskeyword(attr)
            js_attr = re.sub(r'_([a-z])', lambda s: s.group(1).upper(), attr)
            element = tags.p(**{py_attr: 'foo'})['baz']
            assert element.to_dict() == {
                '__element__': {'name': 'p', 'children': ['baz'], 'props': {js_attr: 'foo'}}
            }
            assert element == tags.p['baz'](**{py_attr: 'foo'})
        assert tags.p(is_=expr('z')).props['is'] == expr('z')

    def test_invalid_attribute(self):
        pytest.raises_str('unknown attribute: bar', tags.p, bar='foo')
        pytest.raises_str('unknown attribute: bar', tags.p['baz'], bar='foo')
        pytest.raises_str('invalid attribute: href=42', tags.p, href=42)

    def test_styles(self):
        for style in tags._STYLES:
            element = tags.p(style={style: 'foo'})
            js_style = re.sub(r'[\-_]([a-z])', lambda s: s.group(1).upper(), style)
            assert element.to_dict() == {
                '__element__': {'name': 'p', 'props': {'style': {js_style: 'foo'}}}
            }
        assert tags.p(style={'z-index': 1.2}).props['style']['zIndex'] == 1.2
        assert tags.p(style={'z_index': 42}).props['style']['zIndex'] == 42
        assert tags.p(style={'zIndex': expr('y')}).props['style']['zIndex'] == expr('y')
        assert tags.p(style={'filter': 'foo'}).props['style']['filter'] == 'foo'

    def test_invalid_style(self):
        pytest.raises_str('invalid style: []', tags.p, style=[])
        pytest.raises_str('unknown style: foo', tags.p, style={'foo': 1})
        pytest.raises_str('invalid style: zIndex=[]', tags.p, style={'z-index': []})
