## 0.12.4

- [STYLE]: Layout aside has a fixed width now instead of min/max size range.
- [CHORE]: Radicals/linked words that return "(no results)" now also hide their contained info messages to reduce irrelevant visual clutter.

## 0.12.3

- [FIX]: Stroke order slider now working in lookup browser after subsequent lookups.
- [FEATURE]: Added "Suggest Change" action button.

## 0.12.2

- [FIX]: Added `delete_mark` functions to front templates for recognition/production, so front delete action works.

## 0.12.1

- [FIX]: Actually hide front-of-card actions on mobile.

## 0.12.0

- [FEATURE]: Added front-of-card actions (mark known/delete).

## 0.11.0

- [STYLE]: Furigana is now displayed above kanji only, instead of full kana.

## 0.10.1

- [FIX]: Open tooltips in the lookup browser are now closed on subsequent lookups.

## 0.10.0

- [STYLE]: Added new linked word derivative for new cards.

## 0.9.10

- [STYLE]: Readings use space more effectively on mobile.
- [CHORE]: Content tweaks.
- [STYLE]: Primitive-of tooltips now are left-positioned to avoid being cut-off on smaller screens.

## 0.9.9

- [FIX]: Clicking example words now opens the dictionary on click (shift modifier not necessary, but still works too).

## 0.9.8

- [CHORE]: Added '(no results)' span to each of the card sub-sections if there are no results.

## 0.9.7

- [FIX]: Stroke diagram hotkeys prevent duplicate bindings and are therefore no longer buggy.

## 0.9.6

- [STYLE]: Right-padding on primitives of container removed, since it's unnecessary.

## 0.9.5

- [CHORE]: Title/tooltip content tweak.

## 0.9.4

- [FIX]: Stroke diagram border partially occluded on Windows.
- [STYLE]: Thinned the stroke diagram border in light mode.
- [STYLE]: Increased contrast of faded info messages in light mode (mobile info, tooltips).

## 0.9.3

- [STYLE]: Base kanji font applied to tags, padding adjusted accordingly.
- [CHORE]: Fixed content typo.

## 0.9.2

- [REFACTOR]: "Hide furigana on linked words" setting now enabled on mobile, changed message from "(hover)" to "(tap)" for mobile devices.

## 0.9.1

- [STYLE]: Primitive/radical buttons have been artificially centered, necessary due to a quirk in the font-family line-height.

## 0.9.0

- [REFACTOR]: Switched radicals/primitives-of containers around.
- [STYLE]: Another iteration of layout style tweaks.
- [CHORE]: Content revisions.
- [STYLE]: User data vertical padding tweaks.

## 0.8.7

- [STYLE]: Min-width on primitives/radicals container, for the medium breakpoint which can squish severely when tooltips are toggled.

## 0.8.6

- [STYLE]: Another iteration of responsive layout style tweaks, tightening and loosening at the various breakpoints.

## 0.8.5

- [STYLE]: Hid title tooltip separators on mobile.
- [STYLE]: Title tooltip on mobile now have center alignment offsets to account for the tooltip button.
- [CHORE]: Tooltip content revisions.
- [STYLE]: Tightening of responsive layout styles.

## 0.8.4

- [FIX]: Included missing title tooltip script binds in lookup template.

## 0.8.3

- [FIX]: Aside container now has a responsive `min-width`, which unbreaks some especially squishy/narrow layouts.

## 0.8.2

- [FIX]: Lookup templates didn't have access to the new content variables.
- [FIX]: Tooltip button style resets for Anki.
- [CHORE]: Toggle script only on the backs of cards now.
- [STYLE]: Stroke diagram now has a responsive width system that's more conducive to being squished a little.

## 0.8.1

- [FIX]: Tooltip toggles no longer rely on their own (broken) individual inline scripts, and are now orchestrated by a single script.

## 0.8.0

- [FEATURE]: Added tooltips and explanatory messaging to main card sub-sections.

## 0.7.2

- [FIX]: "(hover)" text was (mistakenly) active on mobile.
- [FIX]: Furigana alignment and centering (especially on mobile) now displays more consistently.
- [FIX]: Front of card example words can again wrap to multiple lines.

## 0.7.1

- [FIX]: Example words without furigana now line up with example words that do have furigana.
- [STYLE]: Fallback fonts for front-of-card characters.
- [FIX]: Front characters no longer wrap to multiple lines.
- [STYLE]: Tweaks to responsive layout padding.

## 0.7.0

- [FEATURE]: Added dedicated font for kanji characters.
- [FIX]: Asset imports now work in AnkiDroid.

## 0.6.1

- [FIX]: Production back template now respects the option "hide keyword for advanced users" toggle.
- [REFACTOR]: Repo dist folder now gives complete template file outputs rather than piecemeal, to make Anki deployment simpler.

## 0.6.0

- [FEATURE]: Overhaul of stroke order diagram, including slider, and all strokes drawn at the start, rather than one-by-one.
- [STYLE]: Padding of linked words on larger viewports reduced to match medium viewports (bit roomy).

## 0.5.1

- [FIX]: Focus styles on stroke order diagram controls are no longer partially obscured by the above character container.

## 0.5.0

- [STYLE]: Min-height applied to stroke order diagram, so it's not squashed when no stroke order data is present. "(no data)" message displayed when stroke diagram isn't present.
- [STYLE]: Stroke diagram axes are now manually rendered for greater flexibility, e.g. to also be present on completed default diagram.
- [STYLE]: More tweaks to "Primitive" keyword badge (moved down a little) so there's less overlap with above keywords when wrapped on mobile.
- [STYLE]: Dark mode button hover color reduced in intensity.
- [REFACTOR]: Replaced stroke order controls "stop" icon with "restart" icon, since it makes better sense.

## 0.4.1

- [STYLE]: Tweaks to stroke order diagram responsive button/image sizes.
- [STYLE]: Moved "Primitive" keyword badge in a little.

## 0.4.0

- [STYLE]: Actions and lookup actions now display a message on mobile communicating their inoperability.
- [STYLE]: Linked word padding slightly reduced on mid-level breakpoints.
- [STYLE]: Tweaked primitive keyword style opacity/font-size.
- [FEATURE]: Show messages on mobile RE: clickable functionality.

## 0.3.0

- [STYLE]: Added dedicated and separate styles for primitive keywords; added associated demo derivative templates.

## 0.2.0

- [STYLE]: Explicit styles for "Welcome" and "No Results" lookup window templates.
- [STYLE]: Revised approprirate colors for stroke order diagram axes.

## 0.1.4

- [REFACTOR]: Moved user data field up, so it sits just below keyword/meanings.
- [FIX]: Keyword now displays in lookup markup (ID is different than the card templates).
- [FIX]: Removed user data field from lookup.
- [FIX]: Dark mode in lookup browser now works.
- [STYLE]: Tightened padding/margins on tags.

## 0.1.3

- [FIX]: Fixed front/back content alignment being slightly off due to scroll bar presence on the back template
- [STYLE]: Tweaked diagram title responsive font size/weight/padding.

## 0.1.2

- [STYLE]: Tweaked responsive layout aside and stroke order diagram width and padding.
- [STYLE]: Tweaked reading responsive widths for better alignment, especially with shorter readings.

## 0.1.1

- [FIX]: Show keyword on the lookup templates.

## 0.1.0

Initial release for alpha testing.
