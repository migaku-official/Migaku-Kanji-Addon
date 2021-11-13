## 1.0.0-beta.1 (unreleased)

- [FIX]: "Show more" button styles on backs of cards no longer have Anki's default button styles interfering.
- [STYLE]: Front of card actions are now more subdued.
- [CHORE]: Added another info message to front of card actions.
- [FIX]: Addon compatibility with opening multiple windows (`util.open_browser(query)`).
- [FIX]: Newly added cards no longer appear in linked vocab.
- [FEATURE]: Linked words now open `jisho.org` search on mobile.
- [STYLE]: Furigana is no longer selectable, to make for cleaner copy/paste of words.
- [STYLE]: Primitive keywords now have a visually distinct style in primitive button hover tooltip.
- [CHORE]: Added title tooltips to all other sections of the card templates.

## 1.0.0-alpha.1 / 1.0.0-alpha.2

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