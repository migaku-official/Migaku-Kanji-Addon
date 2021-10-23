// ---------------------------------------
// Imports

const gulp = require('gulp');
const rimraf = require('rimraf');
const nunjucksRender = require('gulp-nunjucks-render');
const prettier = require('gulp-prettier');
const sass = require('gulp-sass')(require('sass'));
const autoprefixer = require('gulp-autoprefixer');
const stylelint = require('gulp-stylelint');
const stripCssComments = require('gulp-strip-css-comments');
const rename = require('gulp-rename');
const browserSync = require('browser-sync').create();
const plumber = require('gulp-plumber');
const zip = require('gulp-zip');

// ---------------------------------------
// Constants

const OUTPUT_DIR = 'dist';
const DEMO_DIR = `${OUTPUT_DIR}/demo`;
const SERVE_DIR = `${OUTPUT_DIR}/demo/html`;
const TEMPLATES_DIR = 'src/templates/';
const STYLES_DIR = 'src/styles/';
const ASSETS_DIR = 'src/collection-media/';

const TEMPLATES_GLOB = `${TEMPLATES_DIR}**/*.njk`;
const TEMPLATES_GLOB_EXCLUDE = '!**/partials/**/*';
const STYLES_GLOB = `**/*.scss`;
const ASSETS_GLOB = `${ASSETS_DIR}**/*`;
const DEMO_ASSETS_GLOB = `${TEMPLATES_DIR}/demo/**/*`;
const DEMO_ASSETS_GLOB_EXCLUDE = `!${TEMPLATES_DIR}/demo/**/*.njk`;
const SCSS_SRC = `${STYLES_DIR}styles.scss`;
const CSS_DIST = 'styles.css';
const ZIP_DIST = 'collection.media.zip';

const TASKS = {
	DEFAULT: 'default',
	SERVE: 'serve',
	WATCH: 'watch',

	BUILD: {
		CLEAN: 'clean',
		TEMPLATES: 'nunjucks',
		STYLES: 'scss',
		ASSETS_ZIP: 'assets-zip',
		DEMO_ASSETS: 'demo-assets',
	},
};

// ---------------------------------------
// Build tasks

gulp.task(TASKS.BUILD.CLEAN, (cb) => {
	rimraf(OUTPUT_DIR, cb);
});

// HTML templating
gulp.task(TASKS.BUILD.TEMPLATES, () =>
	gulp
		.src([TEMPLATES_GLOB, TEMPLATES_GLOB_EXCLUDE])
		.pipe(plumber())
		.pipe(
			nunjucksRender({
				path: [TEMPLATES_DIR],
			}),
		)
		.pipe(prettier())
		.pipe(gulp.dest(OUTPUT_DIR)),
);

// SCSS compilation
gulp.task(TASKS.BUILD.STYLES, () =>
	gulp
		.src(SCSS_SRC)
		.pipe(plumber())
		.pipe(
			sass({
				outputStyle: 'expanded',
				includePaths: ['node_modules'],
			}),
		)
		.pipe(autoprefixer())
		.pipe(
			stripCssComments({
				preserve: true,
			}),
		)
		.pipe(
			stylelint({
				failAfterError: false,
				fix: true,
			}),
		)
		.pipe(rename(CSS_DIST))
		.pipe(gulp.dest(OUTPUT_DIR))
		.pipe(browserSync.stream()),
);

// Zip assets destined for Anki `collection.media` folder
gulp.task(TASKS.BUILD.ASSETS_ZIP, () =>
	gulp
		.src(ASSETS_GLOB)
		.pipe(plumber())
		.pipe(zip(ZIP_DIST))
		.pipe(gulp.dest(OUTPUT_DIR)),
);

// Assets necessary for demo directory
gulp.task(TASKS.BUILD.DEMO_ASSETS, () =>
	gulp
		.src([
			ASSETS_GLOB,
			DEMO_ASSETS_GLOB,
			DEMO_ASSETS_GLOB_EXCLUDE,
			`${OUTPUT_DIR}/${CSS_DIST}`,
		])
		.pipe(plumber())
		.pipe(gulp.dest(DEMO_DIR)),
);

// ---------------------------------------
// Serve

gulp.task(TASKS.SERVE, () => {
	browserSync.init({
		server: {
			baseDir: [
				// Open this dir in the browser
				SERVE_DIR,
				// But also resolve assets from this dir
				DEMO_DIR,
			],
			directory: true,
		},
	});

	gulp.watch(TEMPLATES_GLOB, gulp.series(TASKS.BUILD.TEMPLATES));
	gulp.watch(
		[ASSETS_GLOB, STYLES_GLOB],
		gulp.series([TASKS.BUILD.STYLES, TASKS.BUILD.DEMO_ASSETS]),
	);

	gulp.watch([TEMPLATES_GLOB, ASSETS_GLOB]).on('change', browserSync.reload);
});

// ---------------------------------------

gulp.task(TASKS.DEFAULT, gulp.series(Object.values(TASKS.BUILD)));
