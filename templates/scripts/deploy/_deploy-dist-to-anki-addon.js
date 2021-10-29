// Node builtins
const path = require('path');

// Local files
const {
	CONSTANTS = {},
	ensureDirExists,
	deployTemplatesToDir,
} = require('./_deploy-shared');
const { ANKI_ADDON_WEB_DIR } = CONSTANTS;

// Variables pulled from .env.development
const ankiAddonFolder = process.env.ANKI_MIGAKU_ADDON_FOLDER_PATH;
const shouldDeployToAnki = process.env.DEPLOY_TO_ANKI;

// Main function
const deployToAnkiAddonFolder = () => {
	if (!shouldDeployToAnki) {
		console.error(
			"`.env.development` variable `DEPLOY_TO_ANKI` set to 'false' (or didn't exist).",
		);
		process.exit(1);
	}

	const ankiWebDir = path.resolve(ankiAddonFolder, ANKI_ADDON_WEB_DIR);

	// Don't continue if the specified Anki addon directory doesn't exist
	if (!ensureDirExists(ankiAddonFolder)) {
		console.error("Anki addon dir doesn't exist:", ankiAddonFolder);
		process.exit(1);
	}

	// Don't continue if Anki's addon `web` directory doesn't exist
	if (!ensureDirExists(ankiWebDir)) {
		console.error(
			"The Anki folder `web` within the Anki addon dir doesn't exist:",
			ankiWebDir,
		);
		process.exit(1);
	}

	deployTemplatesToDir(ankiWebDir);
};

module.exports = { deployToAnkiAddonFolder };
