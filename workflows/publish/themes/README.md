# Themes

One set of color roles that every renderer maps to its own format: the Mermaid views
(`themeVariables`), the deployment SVG, the presentation renderer (Eraser), and the site (Hextra's
`--primary-hue`, the self-contained layout's CSS variables). A model picks one with
`[theme] name = "<id>"` and may override any role; a role a model sets wins over the theme's.

| Role | Used for |
|---|---|
| `ground` | the page and diagram background |
| `sunken` | a zone or group's fill |
| `surface` | a box's fill |
| `border`, `recessed` | box outlines; zone outlines and the background grid |
| `strong`, `text`, `muted` | titles; body text; details, labels, and lines |
| `accent` | the outline on the project's own code |
| `focus` | what a walkthrough step highlights |
| `ok` | a governing or return path |
| `limited`, `purchasing`, `evaluation` | a stand-in; decided, not built; unknown |
