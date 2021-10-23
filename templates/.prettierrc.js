module.exports = {
	// Note tab width purposefully not configured,
	// to allow developer preference in their IDE
	useTabs: true,
	tabWidth: 2,

	// { foo: bar } as opposed to {foo:bar}, for readability
	bracketSpacing: true,

	// Single quotes for strings, except in JSX
	singleQuote: true,
	quoteProps: 'consistent',
	jsxSingleQuote: false,
	jsxBracketSameLine: false,

	// Trailing commas for improved diff
	trailingComma: 'all',

	// Enforce LF for line breaks
	endOfLine: 'lf',
};
