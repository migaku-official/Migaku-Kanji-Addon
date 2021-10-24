module.exports = {
	extends: ['stylelint-config-standard', 'stylelint-config-prettier'],
	plugins: ['stylelint-order', 'stylelint-scss', 'stylelint-prettier'],
	rules: {
		// Mark formatting issues as errors
		'prettier/prettier': true,

		// Enforce alphabetical ordering of CSS properties
		// This for both consistency and predictability
		'order/properties-alphabetical-order': true,

		// Clearer spacing between blocks
		'rule-empty-line-before': ['always', { except: ['first-nested'] }],
		'at-rule-empty-line-before': [
			'always',
			{
				ignore: ['after-comment', 'blockless-after-blockless', 'first-nested'],
				ignoreAtRules: ['else'],
			},
		],

		// Kanji fonts will be reliably present
		// (fallback generic fonts unnecessary and wouldn't work anyway)
		'font-family-no-missing-generic-family-keyword': null,

		// SCSS ruleset switch-out
		// Ref: https://github.com/kristerkari/stylelint-scss#installation-and-usage
		'at-rule-no-unknown': null,
		'scss/at-rule-no-unknown': true,

		// Necessary to disable for SCSS support
		// Ref: https://github.com/stylelint/stylelint/issues/5322#issuecomment-847712546
		'no-invalid-position-at-import-rule': null,
	},
};
