# -*- coding: utf-8

import abc
import copy
import json
import six


class expr(object):
    def __init__(self, code):
        if not isinstance(code, (six.string_types, expr)) or not code:
            raise RuntimeError('invalid expr: {!r}'.format(code))
        self.code = str(code)

    def __repr__(self):
        return 'expr({!r})'.format(self.code)

    def __str__(self):
        return self.code

    def __hash__(self):
        # need this, otherwise JSON encoder trips in Python 3
        return hash(('__expr__', self.code))

    def __eq__(self, other):
        return isinstance(other, type(self)) and str(self) == str(other)


class ElementEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Element):
            encoded = {
                'name': obj.name,
                'children': obj.children or [],
                'props': obj.props or None
            }
            if obj.inputs:
                encoded['inputs'] = obj.inputs
            if obj.outputs:
                encoded['outputs'] = obj.outputs
            return {'__element__': encoded}
        elif issubclass(obj, Element):
            return obj()
        elif isinstance(obj, expr):
            return {'__expr__': str(obj)}
        return super(ElementEncoder, self).default(obj)


class ElementMeta(abc.ABCMeta):
    # allow using [] operator on the class object
    def __getitem__(cls, key):
        return cls()[key]


@six.add_metaclass(ElementMeta)
class Element(object):
    def __init__(self, name, is_container=False, inputs=None, outputs=None, props=None):
        self.name = name
        self.is_container = bool(is_container)
        self.inputs = list(inputs) if inputs else []
        self.outputs = list(outputs) if outputs else []
        self.props = dict(props) if props else {}
        self.children = []
        self.props = self._convert_props(**(props or {}))

    def _convert_props(self, **props):
        return props

    def to_json(self):
        return json.dumps(self, cls=ElementEncoder, indent=4)

    def to_dict(self):
        return json.loads(self.to_json())

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.to_json() == other.to_json()

    def __getitem__(self, key):
        # disallow settings children on non-container elements
        if not self.is_container:
            raise RuntimeError('not a container: {}'.format(self.name))
        obj = copy.deepcopy(self)
        obj.children = key if isinstance(key, tuple) else (key,)
        for item in obj.children:
            # allow using element class objects for empty elements
            if isinstance(item, type) and issubclass(item, Element):
                continue
            # child elements can be strings, expressions or elements
            if not isinstance(item, (six.string_types, expr, Element)):
                raise RuntimeError('unexpected child element: {}'.format(item))
        return obj

    def __call__(self, **props):
        obj = copy.deepcopy(self)
        new_props = obj.props
        new_props.update(props)
        obj.props = obj._convert_props(**new_props)
        return obj

    def __repr__(self):
        props = (' ' + ' '.join('{}={!r}'.format(*i) for i in self.props.items())).rstrip()
        return '<{0}{1}>{2}</{0}>'.format(self.name, props, '...' * bool(self.children))
