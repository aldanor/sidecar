# -*- coding: utf-8 -*-

import keyword
import pytest

from sidecar import tags
from sidecar.element import Element, expr


@pytest.fixture
def all_tags():
    return [{
        'name': tag,
        'cls': getattr(tags, tag + '_' * keyword.iskeyword(tag)),
        'void': tag in tags._VOID_TAGS
    } for tag in tags._TAGS]


class TestTags(object):
    def test_basic(self, all_tags):
        for tag in all_tags:
            assert issubclass(tag['cls'], Element)
            element = tag['cls'](
                is_='foo', form_enc_type='bar', alt='baz', inputMode='qwe', href=expr('x'),
                style={'line-height': 1, 'align_self': 'no', 'flexFlow': 'yes', 'flex': 0}
            )
            assert element.name == tag['name']
            assert element.is_container == (not tag['void'])
            assert element.inputs == []
            assert element.outputs == []
            assert element.to_dict() == {
                '__element__': {
                    'name': tag['name'],
                    'children': [],
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

    def test_void_tags(self, all_tags):
        for tag in all_tags:
            if tag['void']:
                with pytest.raises_regexp(Exception, 'not a container: {}'.format(tag['name'])):
                    tag['cls']['foo']
                with pytest.raises_regexp(Exception, 'not a container: {}'.format(tag['name'])):
                    tag['cls']()['foo']
            else:
                assert tag['cls']['foo', 'bar'] == tag['cls']()['foo', 'bar']
