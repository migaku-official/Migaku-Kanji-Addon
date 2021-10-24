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
- `yarn serve`: Launches the dev demo server, and watches for changes - rebuilding when necessary.
- `yarn start`: Runs `build` then `serve`.
- `yarn lint`: Runs stylelint.

## Active development

Run `yarn start` and navigate to `http://localhost:3000/` to view the demo template outputs. Note that re-compiling the HTML templates can take up to 30s-1m on change, but SCSS changes recompile almost instantly.

If you are adding more features or covering more use-cases/edge-cases, consider adding another demo template or derivative in the `templates/demo` directory.
