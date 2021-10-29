# Template development

Please ensure you have already read both the contribution guidelines ([CONTRIBUTING.md](../.github/CONTRIBUTING.md)) and development documentation ([DEVELOPMENT.md](../.github/DEVELOPMENT.md)) before diving in.

## Getting started

First you ought to ensure your node environment is suitable. We recommend you use `nvm` [Node Version Manager](https://github.com/nvm-sh/nvm#installing-and-updating) to manage and install node versions.

So, first run `nvm use` to auto-install and use a known-compatible version of node as per the directory `.nvmrc`.

Then, run `yarn` to install `node_modules` dependencies.

You'll need to [install Yarn globally](https://yarnpkg.com/getting-started/install) if you don't already have it installed (you can do so with `npm`).

## Quickstart

In other words, run `nvm use && yarn` to set up your dev environment and install the requisite dependencies.

Then you'll probably want to run `yarn serve`.

## Scripts

- `yarn build`: Compile the templates into the adjacent `dist` folder.
- `yarn deploy`: Deploy the compiled templates into the repo addon folder, and even your system's Anki addon folder (if configured).
- `yarn serve`: Launches the dev demo server, and watches for changes - rebuilding when necessary.
- `yarn start`: Runs `build` then `serve`.
- `yarn lint`: Runs stylelint.

## Active development

Run `yarn start` and navigate to `http://localhost:3000/` to view the demo template outputs. Note that re-compiling the HTML templates can take up to 30s-1m on change, but SCSS changes recompile almost instantly.

If you are adding more features or covering more use-cases/edge-cases, consider adding another demo template or derivative in the `templates/demo` directory.

## Build and deployment

The build directory (`./dist`) is kept up to date if you're watching changes with `yarn start`. Otherwise, to compile the templates, simply run `yarn build`.

To deploy these changes, run `yarn deploy`. This will updated the contents of the root folder `addons` which forms the source code for the Anki addon folder itself.

If you're developing locally, you can also deploy directly to the Migaku Kanji addon folder in your own Anki. This requires some small configuration first.

### ⚠️ But first, a warning

Deploying into Anki only replaces the template files in the `web` folder. It will not affect your user data. However, making modifications directly to your addon folder obviously comes with the risk that you might change something you want to revert.

**For this reason, it is highly recommended that you first make a back-up of your Migaku Kanji addon folder.** Just .zip a copy of it, for the sake of being cautious. We will not be liable if you make any changes and lose any data. So proceed with caution! This is a development feature intended for developers who know what they're doing.

Note that this deployment also only updates the template content of the addon (and also the `collection.media` data), and **not any of the python scripts**. If you want to update those, you'll need to manually copy and paste them.

### Configuring Anki deployment

In this directory, there is a file `.env.development.example`. Duplicate this file, and rename it to just `.env.development`. **Never commit this file**. You shouldn't be able to, anyway (it's in the `.gitignore`).

Within this dotenv file, you'll need to change the value of the `ANKI_MIGAKU_ADDON_FOLDER_PATH` variable to equal the absolute pathname to the `Migaku Kanji` folder in your Anki `addons21` folder. The end of your path will probably look like `.../Anki2/addons21/Migaku Kanji`. For example, mine is (on Mac) `/Users/$USER/Library/Application Support/Anki2/addons21/Migaku Kanji`.

Once you have configured this, you can re-run the regular `yarn deploy` and it will also deploy to your Anki folder in addition to the repo `addon` folder.

**You'll need to restart Anki to see your deployed changes.**

## Manually "deploy"

An easier but slower method to the above, is simply to build the repo with `yarn build`, and then copy the contents of the `dist` folder into the `web` folder of the Migaku Kanji addon folder in Anki.
