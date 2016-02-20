import ExtractTextPlugin from 'extract-text-webpack-plugin';
import path from 'path';
import webpack from 'webpack';

function pathTo(relpath) {
    return path.join(__dirname, '..', relpath);
}

let config = {
    entry: {
        'app': pathTo('js/app'),
        vendor: [
            'react', 'sockjs-client', 'underscore', 'debug', 'alt', 'immutable',
            'whatwg-fetch', 'material-ui', 'react-tap-event-plugin', 'rc-slider',
            'react-flexbox-grid'
        ]
    },
    output: {
        path: pathTo('src/sidecar/static'),
        publicPath: '/static/',
        filename: '[name].bundle.js',
        chunkFilename: '[name].bundle.js'
    },
    module: {
        loaders: [
            {
                test: /\.(css|scss)$/,
                loader: ExtractTextPlugin.extract('style', 'css?sourceMap&modules&importLoaders=1&localIdentName=[name]__[local]___[hash:base64:5]!postcss!sass?sourceMap')
            },
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                query: {
                    presets: [
                        'es2015-webpack',
                        'react'
                    ],
                    plugins: [
                        'transform-decorators-legacy',
                        'transform-class-properties',
                        'transform-object-rest-spread'
                    ],
                    cacheDirectory: true
                }
            }
        ]
    },
    resolve: {
        extensions: ['', '.js', '.jsx', '.json', '.scss'],
        modulesDirectories: ['node_modules'],
        root: [pathTo('js'), pathTo('node_modules')]
    },
    node: {
        fs: 'empty',
        net: 'empty',
        tls: 'empty',
        process: 'empty'
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery',
            'root.jQuery': 'jquery',
            React: 'react',
            _: 'underscore',
            'es6-promise': 'es6-promise',
            'fetch': 'imports?this=>global!exports?global.fetch!whatwg-fetch'
        }),
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: JSON.stringify('production')
            }
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'vendor',
            filename: 'vendor.bundle.js'
        }),
        new ExtractTextPlugin('vendor.css', { allChunks: true })
    ],
    stats: {
        colors: true
    }
};

if (process.env.NODE_ENV === 'production') {
    config.plugins.push(
        new webpack.optimize.UglifyJsPlugin({
            sourceMaps: false,
            minimize: true,
            compress: {
                warnings: false
            },
            output: {
                comments: false,
                semicolons: true
            }
        })
    );
} else {
    config.devtool = 'eval-cheap-module-source-map';
}

export default config;
