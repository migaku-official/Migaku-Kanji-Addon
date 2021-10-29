// ----------------------------
// Imports

// Necessary to make `process.env` accessible
require('dotenv-flow').config({
	default_node_env: 'development',
});

// Local dependencies; modular scripts
// (The two main deployment tasks)
const { deployToRepoAddonFolder } = require('./_deploy-dist-to-repo-addon');
const { deployToAnkiAddonFolder } = require('./_deploy-dist-to-anki-addon');
const { CONSTANTS, ensureDirExists } = require('./_deploy-shared');

// ----------------------------

if (!ensureDirExists(CONSTANTS.TEMPLATES_DIST)) {
	console.error("Templates dist dir doesn't exist:", CONSTANTS.TEMPLATES_DIST);
	process.exit(1);
}

deployToRepoAddonFolder();
deployToAnkiAddonFolder();
