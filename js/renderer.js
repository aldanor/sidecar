import React from 'react';
import _ from 'lodash';

// this could be optimized in theory by storing function objects and
// components that don't have nested expressions in a precached tree
function renderer(ui, factory) {
    function render(env) {
        function renderSingle(obj) {
            if (!_.isObject(obj)) {
                return obj;
            } else if (_.isArray(obj)) {
                return _.map(obj, renderSingle);
            } else if (_.has(obj, '__expr__')) {
                return Function('env', `return (${obj.__expr__})`)(env);
            } else if (_.has(obj, '__element__')) {
                const element = obj.__element__;
                const type = element.builtin ? element.name : factory(element.name);
                const props = element.props ? renderSingle(element.props) : null;
                const children = element.children ? renderSingle(element.children) : [];
                return React.createElement(type, props, ...children);
            } else {
                return _.mapValues(obj, renderSingle);
            }
        }
        return renderSingle(ui);
    }
    return render;
}

export default renderer;
