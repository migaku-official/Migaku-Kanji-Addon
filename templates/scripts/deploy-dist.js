require('dotenv-flow').config({
	default_node_env: 'development',
});

const { deployToRepoAddonFolder } = require('./_deploy-dist-to-repo-addon');
const { deployToAnkiAddonFolder } = require('./_deploy-dist-to-anki-addon');

const ankiAddonFolder = process.env.ANKI_MIGAKU_ADDON_FOLDER_PATH;
const hasSetAnkiFolder = !!ankiAddonFolder;
const shouldDeployToAnki = process.env.DEPLOY_TO_ANKI && hasSetAnkiFolder;

deployToRepoAddonFolder();

if (shouldDeployToAnki) {
	deployToAnkiAddonFolder();
} else {
	console.log('dont deploy to Anki');
}
