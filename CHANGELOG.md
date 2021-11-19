## (Unreleased)

- [FEATURE]: "Show more" buttons enhanced in "Vocab" and "Primitive of" sections - can now "show less".
- [FEATURE]: A bundled parser is now included in the addon, so Migaku Japanese is no longer strictly required to be installed as a dependency.
- [FEATURE]: A pop-up notice is now show to the user when attempting to edit the card templates, warning them that changes would be overwritten. An option is provided to take them to the directory containing the compiled files, if they would still like to make any changes.
- [FIX]: Fixed an issue that can happen when creating kanji cards by selection.

## 1.0.0-beta.4

- [FIX]: Furigana is no longer hidden when "hide readings of known words until hovered" is unselected.

## 1.0.0-beta.3

- [FEATURE]: Linked word furigana on mobile is now revealed on first tap, and jisho search on second tap (if setting enabled).
- [FIX]: Selecting vocab text without also selecting furigana now more consistent, especially for words with okurigana or kanji/hiragana combo words.

## 1.0.0-beta.2

- [FIX]: Successive card reviews on several platforms work again
- [FIX]: Added defaults to several config requests, preventing some errors
- [FIX]: Typos in settings window removed

## 1.0.0-beta.1

This is a "partially open" beta, announced for supporters on Patreon, but with the GitHub repo being made available to the public for the first time.

### New features

- [FEATURE]: Linked words now open `jisho.org` search on mobile.
- [FEATURE]: A character's primitive alternatives are now displayed within the "Primitive in" section, if applicable.
- [STYLE]: Primitive keywords now have a visually distinct style in the primitive button hover tooltip.
- [FEATURE]: Primitives with alternatives now display an asterisk when appearing as primitive buttons in other cards.
- [FEATURE]: Kanji diagram now starts fully drawn, with settings available for card animation preference (play from start, all strokes at once, fully drawn).
- [FEATURE]: You can now also add kanji cards via manual selection, i.e. via text box content (non-kanji, duplicates, known kanji ignored).

### Notable fixes and improvements

- [FIX]: Automatic card creation when adding new cards is now working again.
- [FIX]: Look-ahead card creation should now occur more reliably (but more testing required).
- [CHORE]: Suspended cards that are not new can now display in linked words (e.g. retired cards).
- [CHORE]: Dictionary radicals are now hidden by default, and can be shown via a new setting.
- [FIX]: "Show more" button styles on backs of cards no longer have Anki's default button styles interfering.
- [STYLE]: Front of card actions are now more subdued, and have an additional info message.
- [FIX]: Compatibility with addons that open multiple windows (`util.open_browser(query)`).
- [FIX]: Newly added cards no longer appear in linked vocab.
- [STYLE]: Furigana is no longer selectable, to make for cleaner copy/paste of words.
- [CHORE]: Added more tooltips to the main card templates.
- [FIX]: Adding user data to cards on AnkiDroid no longer breaks the entire card, but just breaks the kanji diagram for that card. User data still shows. Card can be fixed via "Refresh Kanji Cards" on desktop. (Best we can do for now).
- [FIX]: "Found new kanji" dialog will no longer open duplicate windows (e.g. during "Export 1T").

## 1.0.0-alpha.1 / 1.0.0-alpha.2

This is a closed alpha for Patreon "Backers".

First candidate for a public release. Note that the alpha and beta history prior to 1.0.0 are not recorded here, and otherwise exist in Patreon and Discord post history.

### New features

- [FEATURE]: Added a new "primitive in" section, which displays more complex kanji that the kanji you're learning appears within.
- [FEATURE]: Added "new" cards to linked vocab with separate styles, so you can see upcoming vocab.
- [FEATURE]: Added "show more" buttons for linked vocab and primitive section, to truncate long results.
- [CHORE]: Added tooltips to some sections to explain what they are.
- [CHORE]: Added "mark known and delete" button to front for convenience.
- [CHORE]: Added "suggest change" button to back of cards to encourage improvemenets to the kanji database.

### Notable fixes and improvements

- [FIX]: AnkiDroid now working fully (icons and stroke order diagram).
- [FEATURE]: UserData now appears in the lookup browser (from any of both recognition/production cards).
- [FEATURE]: When setting a custom keyword, you can now specify that it's a primitive name.
- [FEATURE]: Clicking the greyed-out example words in linked vocab now opens the dictionary (shift + click still works too).
- [FEATURE]: Furigana is now displayed in a distributed way above kanji only, instead of full-kana.
- [FEATURE]: The base kanji font is now consistent across all platforms, rather than relying on system font.
- [FIX]: Stroke order diagram hotkeys now working more consistently.
- [STYLE]: Improvement of the card layout styles across mobile/desktop.
- [CHORE]: Numerous other small fixes and tweaks.
- [CHORE]: Added "About" page in settings with licencing, links, credits.