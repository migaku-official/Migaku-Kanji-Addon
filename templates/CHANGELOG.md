## 0.7.2 (unreleased)

- [FIX]: "(hover)" text was (mistakenly) active on mobile.

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
