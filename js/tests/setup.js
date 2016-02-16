import jsdom from 'node-jsdom';

const document = jsdom.jsdom('<!doctype html><html><body></body></html>');
const window = document.defaultView;

global.document = document;
global.window = window;

for (const key in window) {
    if (window.hasOwnProperty(key) && !(key in global)) {
        global[key] = window[key];
    }
}
