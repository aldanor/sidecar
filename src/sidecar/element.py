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
            encoded = {'name': obj.name}
            for key in ('children', 'props', 'inputs', 'outputs'):
                if getattr(obj, key):
                    encoded[key] = getattr(obj, key)
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
    allow_children = True

    def __init__(self, name, inputs=None, outputs=None, props=None):
        self.name = name
        self.inputs = list(inputs) if inputs else []
        self.outputs = list(outputs) if outputs else []
        self.props = dict(props) if props else {}
        self.children = []
        self.props = self._convert_props(**(props or {}))

        child_inputs = list(self.inputs)
        self._visit(self.children, lambda e: child_inputs.extend(e.inputs))
        self._visit(self.props, lambda e: child_inputs.extend(e.inputs))
        overlap = [item for item in set(child_inputs) if child_inputs.count(item) > 1]
        if overlap:
            raise RuntimeError('overlapping inputs: {}'.format(sorted(overlap)))

    def _convert_props(self, **props):
        return props

    def _visit(self, obj, callback):
        if isinstance(obj, (list, tuple)):
            [self._visit(item, callback) for item in obj]
        elif isinstance(obj, dict):
            [self._visit(item, callback) for item in obj.values()]
        elif isinstance(obj, type) and issubclass(obj, Element):
            self._visit(obj(), callback)
        elif isinstance(obj, Element):
            callback()
            self._visit(obj.children, callback)
            self._visit(obj.props, callback)

    @property
    def all_inputs(self):
        inputs = list(self.inputs)
        self._visit(self, lambda e: inputs.extend(e.inputs), visit_self=True)
        return sorted(set(inputs))

    @property
    def all_outputs(self):
        outputs = list(self.outputs)
        self._visit(self, lambda e: outputs.extend(e.outputs), visit_self=True)
        return sorted(set(outputs))

    def to_json(self):
        return json.dumps(self, cls=ElementEncoder, indent=4)

    def to_dict(self):
        return json.loads(self.to_json())

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.to_json() == other.to_json()

    def __getitem__(self, key):
        # disallow setting children on non-container elements
        if not self.allow_children:
            raise RuntimeError('not a container: {}'.format(self.name))
        obj = copy.deepcopy(self)
        obj.children = list(key) if isinstance(key, tuple) else [key]
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
        return '<Element: {}>'.format(self.name)
