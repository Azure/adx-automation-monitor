// requirements

var gulp = require('gulp');
var gulpBrowser = require("gulp-browser");
var reactify = require('reactify');
var del = require('del');
var size = require('gulp-size');


gulp.task('transform', function () {
    var stream = gulp.src('./src/javascripts/jsx/*.js')
        .pipe(gulpBrowser.browserify({ transform: ['reactify'] }))
        .pipe(gulp.dest('./app/app/static/js/'))
        .pipe(size());
    return stream;
});


gulp.task('del', function () {
    return del(['./app/app/static/js']);
});

gulp.task('default', ['del'], function () {
    gulp.start('transform');
    gulp.watch('./app/app/static/jsx/*.js', ['transform']);
});