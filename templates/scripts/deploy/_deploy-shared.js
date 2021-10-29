// Node builtins
const path = require('path');
const fs = require('fs');

// Constants
const CONSTANTS = {
	REPO_ADDON_WEB_DIR: path.resolve(__dirname, '../../../addon/web'),
	ANKI_ADDON_WEB_DIR: 'web',
	TEMPLATES_DIST: path.resolve(__dirname, '../../dist'),
};

/**
 * Ensure the provided directory exits.
 */
const ensureDirExists = (dirPath) => {
	try {
		const dirExists = fs.existsSync(dirPath);

		if (!dirExists) {
			console.error(`\nError: '${dirPath}' directory does not exist.\n`);
			process.exit(1);
		}

		return dirExists;
	} catch (err) {
		console.error(
			`An error occurred while checking for the '${dirPath}' directory.`,
			err,
		);
	}
};

/**
 * Copy files from templates source dir to target dir.
 */
const deployTemplatesToDir = (targetDir) => {
	// Loop through templates build folder
	fs.readdir(CONSTANTS.TEMPLATES_DIST, (readErr, files) => {
		if (readErr) {
			console.error(`Error reading directory '${CONSTANTS.TEMPLATES_DIST}'.`);
			console.error(readErr);
			process.exit(1);
		}

		console.log(`\nCopying template build files to target dir:\n${targetDir}`);

		files.forEach((fileName) => {
			const extension = fileName.split('.').pop();
			const fullFilePath = path.resolve(CONSTANTS.TEMPLATES_DIST, fileName);
			const fullDestinationPath = `${targetDir}/${fileName}`;

			// Dont copy directories or zips (only files)
			if (
				(fs.existsSync(fullFilePath) &&
					fs.lstatSync(fullFilePath).isDirectory()) ||
				extension === 'zip'
			) {
				return;
			}

			fs.copyFile(fullFilePath, fullDestinationPath, (copyErr) => {
				if (copyErr) {
					console.error(`Error copying file '${fileName}'.`);
					console.error(copyErr);
					process.exit(1);
				}
			});
		});
	});
};

module.exports = { CONSTANTS, ensureDirExists, deployTemplatesToDir };
