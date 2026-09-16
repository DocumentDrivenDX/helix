# Slide renderer icon set

Monochrome line icons used by `render-deck.js` for slide callouts, section markers, and card headers; one SVG per icon, named `<name>.svg`.
Style contract: `viewBox="0 0 24 24"`, `fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"` on the root `<svg>`, every shape inside the 2..22 box.
No `width`/`height` attributes, no XML prolog, no `<style>`; each file stays under 600 bytes.
The renderer inlines each SVG and substitutes `currentColor` with the slide theme's accent (or lets it inherit the surrounding CSS `color`), so icons carry no colour of their own and work on light and dark backgrounds.
Icons are drawn to read at roughly 0.4 inch on a slide; avoid fine detail that only works larger.
These icons are original work authored in this repository from basic primitives (circle, rect, line, polyline, polygon, path).
They are not copied from Lucide, Feather, or any other icon library, and carry the repository licence.
To check the set: parse each file with `xml.dom.minidom`, rasterize with `rsvg-convert` after replacing `currentColor`, and eyeball a `montage` contact sheet.
