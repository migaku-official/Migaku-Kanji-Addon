// Local files
const {
	CONSTANTS = {},
	ensureDirExists,
	deployTemplatesToDir,
} = require('./_deploy-shared');
const { REPO_ADDON_WEB_DIR } = CONSTANTS;

// Main function
const deployToRepoAddonFolder = () => {
	// Dont continue if the target directory doesn't exist
	if (!ensureDirExists(REPO_ADDON_WEB_DIR)) {
		console.error("Repo addon web dir doesn't exist:", REPO_ADDON_WEB_DIR);
		process.exit(1);
	}

	deployTemplatesToDir(REPO_ADDON_WEB_DIR);
};

module.exports = { deployToRepoAddonFolder };
