const path = require('path');
const fs = require('fs');

const ROOT_DIR = path.resolve(__dirname, '../');
const TEMPLATES_DIR = path.resolve(ROOT_DIR, 'src/templates');
const STYLE_DIR = path.resolve(ROOT_DIR, 'src/styles');

const STYLE_FILE = path.resolve(STYLE_DIR, 'styles.scss');
const CARD_HTML = path.resolve(
	TEMPLATES_DIR,
	'partials/layout/layout-card-structure.njk',
);
const LOOKUP_HTML = path.resolve(
	TEMPLATES_DIR,
	'partials/layout/layout-lookup-structure.njk',
);
const DMAK_JS = path.resolve(
	TEMPLATES_DIR,
	'partials/structure/migaku/_dmak.njk',
);

const pkgJson = require(path.resolve(ROOT_DIR, 'package.json'));
const version = pkgJson.version;

// The LOC contents to search-for/append semver to
const TARGET_PHRASE = '- @version';
const TARGET_REGEX = new RegExp(`^${TARGET_PHRASE}`);

console.log(`Writing version "v${version}" to output files:`);

[STYLE_FILE, CARD_HTML, LOOKUP_HTML, DMAK_JS].forEach((file) => {
	fs.readFile(file, 'utf8', (err, data) => {
		if (err) {
			console.error(err);
			return;
		}

		const lines = data.split('\n').map((line) => {
			const isVersionLine = TARGET_REGEX.test(line);
			return isVersionLine ? `${TARGET_PHRASE} v${version}` : line;
		});

		fs.writeFile(file, lines.join('\n'), 'utf8', (err) => {
			if (err) {
				console.error(err);
			}

			console.log(`- Successfully wrote to "${file.split('/').pop()}"`);
		});
	});
});
