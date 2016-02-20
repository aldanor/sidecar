import { expect } from './helpers';
import renderer from '../renderer';


describe('renderer', () => {
    const Foo = () => <div />;
    const factory = name => ({'Foo': Foo}[name]);
    const render = (obj, env) => renderer(obj, factory)(env);
    const e = obj => ({__element__: obj});

    const consoleError = console.error;
    beforeEach(() => {
        console.error = message => {
            throw new Error(message);
        };
    });
    afterEach(() => {
        console.error = consoleError;
    });

    it('empty builtin tag', () => {
        const elem = render(e({name: 'p', builtin: true}));
        expect(elem.type).to.equal('p');
        expect(elem.props).to.deep.equal({});
    });

    it('empty factory tag', () => {
        const elem = render(e({name: 'Foo'}));
        expect(elem.type).to.equal(Foo);
        expect(elem.props).to.deep.equal({});
    });

    it('invalid factory tag', () => {
        expect(() => render(e({name: 'p'}))).to.throw(Error, 'type should not be null');
    });

    it('non-element', () => {
        expect(render(1)).to.equal(1);
        expect(render(null)).to.equal(null);
        expect(render('foo')).to.equal('foo');
        expect(render({bar: 'baz'})).to.deep.equal({bar: 'baz'});
        expect(render([1, 2])).to.deep.equal([1, 2]);
        expect(render({__expr__: 'env.x + env.y'}, {x: 1, y: 2})).to.equal(3);
        expect(render([{a: {__expr__: 'env.x + env.y'}}], {x: 1, y: 2})).to.deep.equal([{a: 3}]);
    });

    it('builtin tag with props', () => {
        const elem = render(e({name: 'p', builtin: true, props: {x: 1, y: [2, 3], z: 'foo'}}));
        expect(elem.type).to.equal('p');
        expect(elem.props).to.deep.equal({x: 1, y: [2, 3], z: 'foo'});
    });

    it('factory tag with props', () => {
        const elem = render(e({name: 'Foo', props: {x: 1, y: [2, 3], z: 'foo'}}));
        expect(elem.type).to.equal(Foo);
        expect(elem.props).to.deep.equal({x: 1, y: [2, 3], z: 'foo'});
    });

    it('builtin tag with children', () => {
        const elem = render(e({name: 'a', builtin: true, children: ['a', 'b']}));
        expect(elem.type).to.equal('a');
        expect(elem.props).to.deep.equal({children: ['a', 'b']});
    });

    it('factory tag with children', () => {
        const elem = render(e({name: 'Foo', children: ['a', 'b']}));
        expect(elem.type).to.equal(Foo);
        expect(elem.props).to.deep.equal({children: ['a', 'b']});
    });

    it('tag with expr in props', () => {
        const elem = render(e({name: 'Foo', props: {x: {__expr__: 'env.x * 10'}}}), {x: 3});
        expect(elem.type).to.equal(Foo);
        expect(elem.props).to.deep.equal({x: 30});
    });

    it('tag with expr in children', () => {
        const elem = render(e({name: 'Foo', children: [{__expr__: 'env.s + "y"'}]}), {s: 'x'});
        expect(elem.type).to.equal(Foo);
        expect(elem.props).to.deep.equal({children: 'xy'});
    });

    it('tag with tag in props', () => {
        const innerSpec = e({name: 'Foo', children: ['a', 'b']});
        const innerElem = render(innerSpec);
        expect(innerElem.type).to.equal(Foo);
        expect(innerElem.props).to.deep.equal({children: ['a', 'b']});

        const outerElem = render(e({name: 'p', 'builtin': true, props: {foo: innerSpec}}));
        expect(outerElem.type).to.equal('p');
        expect(outerElem.props).to.deep.equal({foo: innerElem});
    });

    it('nested builtin tags', () => {
        const innerSpec = e({name: 'a', builtin: true, props: {href: 'x'}, children: ['bar']});
        const innerElem = render(innerSpec);
        expect(innerElem.type).to.equal('a');
        expect(innerElem.props).to.deep.equal({href: 'x', children: 'bar'});

        const outerElem = render(e({
            name: 'p',
            builtin: true,
            children: ['foo', innerSpec, {__expr__: 'env.s + "bar"'}]
        }), {s: 'foo'});
        expect(outerElem.type).to.equal('p');
        expect(outerElem.props).to.deep.equal({children: ['foo', innerElem, 'foobar']});
    });

    it('nested factory tags', () => {
        const innerSpec = e({name: 'Foo', children: ['foo', {__expr__: 'env.s + "bar"'}]});
        const innerElem = render(innerSpec, {s: 'foo'});
        expect(innerElem.type).to.equal(Foo);
        expect(innerElem.props).to.deep.equal({children: ['foo', 'foobar']});

        const outerElem = render(e({name: 'Foo', children: [innerSpec]}), {s: 'foo'});
        expect(outerElem.type).to.equal(Foo);
        expect(outerElem.props).to.deep.equal({children: innerElem});
    });

    it('className htmlFor style', () => {
        const elem = render(e({name: 'p', builtin: true, props: {
            style: {zIndex: 10}, className: 'foo', htmlFor: 'bar'
        }}));
        expect(elem.type).to.equal('p');
        expect(elem.props).to.deep.equal({style: {zIndex: 10}, className: 'foo', htmlFor: 'bar'});
    });
});
