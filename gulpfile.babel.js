import gulp from 'gulp';
import googleWebfonts from 'gulp-google-webfonts';
import gulpUtil from 'gulp-util';
import path from 'path';
import webpack from 'webpack';
import webpackConfig from './gulp/webpack.config.babel';

function pathTo(relpath) {
    return path.join(__dirname, relpath);
}

gulp.task('fonts', () =>
    gulp.src('gulp/fonts.list')
        .pipe(googleWebfonts({}))
        .pipe(gulp.dest(pathTo('src/sidecar/static/fonts')))
);

gulp.task('webpack', callback => {
    function onError(error, stats) {
        if (error) {
            return callback(new gulpUtil.PluginError('webpack', error));
        } else {
            gulpUtil.log('[webpack]', stats.toString());
            return callback();
        }
    }
    webpack(webpackConfig, onError);
});

gulp.task('build', ['fonts', 'webpack']);

gulp.task('watch', ['webpack'], () => {
    gulp.watch(['js/**/*.js'], ['webpack'])
});

gulp.task('default', ['build']);
