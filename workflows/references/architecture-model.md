# The architecture model

A project's architecture views are generated from one model file, `docs/helix/02-design/architecture-model.toml`, in which every element and relation cites the code that shows it. The views in `architecture.md` and the guide's generated pages are renderings of the model; nothing is drawn by hand. `documentor views` renders them, and `documentor check` fails when a view is stale, when a cited file no longer contains its string, or when the configuration declares an external system the model does not claim. The `design` mode keeps the model beside the architecture document. The diagram standard the views follow is `workflows/references/diagram-design.md`.

## The file

```toml
[system]
id = "atlas"                        # the model's own system; one element has this id and kind "system"
repo = "example-org/atlas"          # where the code the model cites lives
facts = "scripts/architecture_facts.py"   # optional: its declared_facts(root) lists declared systems
regenerate = "just architecture"    # optional: the command the generated text tells a reader to run

[theme]                             # optional: the project's colors over its `publish.theme` (a ux-builder theme), or `name = "<theme>"`; a neutral palette otherwise
accent = "#D12800"                  # the outline on the project's own code
accent_name = "red"                 # the legend's word for it
ground = "#F0EEE6"                  # the fill of everything outside the project
ground_name = "beige"

[[element]]
id = "gateway"
name = "Unity AI Gateway"
detail = "model calls as the user"  # optional, drawn under the name
kind = "external"                   # person | system | container | store | external
status = "built"                    # built | placeholder (a stand-in) | decided (not built) | unknown
facts = ["hosted-mcp:genie-ask"]    # optional: declared systems the project's facts script finds
evidence = [{ path = "config/tools.toml", contains = 'name = "genie-ask"' }]

[[element]]
id = "hohfeld"
name = "Hohfeld"
kind = "container"
status = "built"
system = "hohfeld"                  # optional: this element is another repository's system (see The estate)
evidence = [{ path = "pyproject.toml", contains = "hohfeld>=" }]

[[relation]]
from = "backend"
to = "gateway"
label = "model calls as the user"
status = "built"
step = 2                            # optional: its place in the view's numbered reading order
note = "The gateway signs the call with the person's identity."
evidence = [{ path = "atlas/model_gateway.py", contains = "class ModelGateway" }]

[[view]]
id = "context"
title = "atlas in its workspace"
takeaway = "One sentence a reader keeps."
direction = "LR"
elements = ["analyst", "proxy", "atlas", "gateway"]
document = "architecture.md"        # the file that holds the view's markers (default)
```

Rules:

- **Evidence is a file and a string the file must contain.** Cite the narrowest string that names the thing (a class, a setting name, a dependency line), so a rename fails the check and a reflow does not. An element or relation with no evidence fails.
- **Owner decides the color.** An element is the project's own (`owner` = the `[system]` id: the accent outline), a `person`, or `platform` (everything the project uses but does not build). Systems and containers default to the project's own; stores and externals default to `platform`. A data project whose tables are its product sets `owner` on its own stores.
- **Status is drawn.** `built` is solid; a `placeholder` (a stand-in such as static entitlements) and a `decided` element take the project's lifecycle colors; `unknown` is dashed.
- **A view holds at most 15 elements.** Split a denser view, as one pilot split its container view into the process and the services it calls. A relation is drawn in every view that holds both ends.
- **Only the text between markers is generated.** A view sits between `<!-- architecture-view: <id> -->` and `<!-- /architecture-view -->` in its document. The project's generator writes it; the project's check fails when it is stale.
- **Declared systems are claimed.** When `[system] facts` names a script, its `declared_facts(root)` returns short keys for what the configuration declares (an MCP server, an app resource, a private package: whatever the project's configuration can name). Each key must appear in an element's `facts`, and each claim must still be declared, so a system added to the configuration without a place in the views fails the check. The script is the project's own; HELIX defines only the contract.
- **No host, credential, or identifier belongs in the model.** Names of workspace objects are fine; connection strings and tokens are not.

## View types

A flowchart answers "where does this piece sit?" only as well as its layout allows, and it answers "what does it do?" and "how do the pieces work together?" badly at any size. A view's `type` picks the form that suits its one question. Every type is generated between the same markers and checked by the same `--check`.

| `type` | Answers | Draws from | Renders as |
|---|---|---|---|
| `flowchart` (default) | what connects to what, at one level | elements, relations, `step` | Mermaid flowchart |
| `stack` | where each piece sits, read top to bottom; no arrows | each element's `layer` | Markdown table |
| `cast` | what each piece does, one line each | each element's `job` | Markdown table |
| `deployment` | where everything runs and what travels between | each element's `tier` (1 at the top) and `zone`; each relation's `label` and `why` | SVG beside the document, `architecture-views/<id>.svg` |
| `journey` | how the pieces work together, one request at a time | a `[[journey]]` and its steps | Mermaid sequence |
| `dag` | how data moves from source to consumer, stage by stage | relations marked `data = true` | Mermaid flowchart, left to right, unlabeled |
| `field-guide` | a developer's first map: one request across responsibility lanes, with the notes beside it | the view's groups (one per lane, left to right), each element's `owner` (the lane the system owns is shaded), each relation's `step`, `throughout`, `why`, and `note` | a whole page, self-contained HTML at the view's `document` |

```toml
[[element]]
id = "gateway"
# ...
layer = "Databricks platform"       # stack
job = "Carries every model call, as the person, metered."   # cast
tier = 4                            # deployment: the row, counted from the top
zone = "Unity AI Gateway"           # deployment: the box that hosts it

[[relation]]
from = "atlas"
to = "gateway"
label = "model calls as the user"
why = "one governed, metered path"  # deployment: shown beside the label

[[zone]]                            # optional: a zone's caption
name = "Data"
caption = "Provisioned by the infrastructure repository"

[[journey]]
id = "nda-review"
title = "An analyst reviews a contract"
takeaway = "Every step runs as the person."

[[journey.step]]
from = "analyst"
to = "proxy"
label = "opens the app, and SSO signs them in"

[[view]]
id = "nda-review"
type = "journey"
journey = "nda-review"
elements = []
```

**The field guide is the diagram standard's "architecture field guide" (HELIX's `workflows/references/diagram-design.md`), generated.** Its composition is the standard's: a takeaway headline, a plate with responsibility lanes and a named ownership region, numbered reading order, a legend, the walkthrough, and the sources and limits. Here every part is the model's: the lanes are the view's groups in order; a lane whose elements the system owns is shaded; the numbered steps are the relations with a `step`, in order, each note led by the relation's `why`; the call marked `throughout` gets its pill; the omissions are the elements the view leaves out, by layer, and the elements not yet built; the links are the other documents the model draws. Boxes stack in their lane on one shared axis; a line into the next lane takes its own corridor when it climbs or drops, the outermost target on the innermost corridor so none cross; a line that skips a lane runs over the top and one that returns runs under the bottom. Keep the view to five to seven elements, as the standard says, and put internals in another view. Every numbered step must be on the plate, or `--check` says which is off it.

**Architecture views and data views stay apart.** A relation is either a call (a job reads a volume, the app calls the gateway) or data flowing between stages (bronze feeds silver). Mark the second kind `data = true`. A `dag` view draws only data relations, and checks they form a DAG. A `deployment` view leaves them out, so it answers where things run and what they call, not what feeds what. For a data pipeline, the lineage DAG reads the way the platform's own job graph does: each stage one column after what feeds it. In a deployment view, put what people open in the tier just below them, or every "opens" line crosses the drawing.

A journey's step must walk a relation the model holds, in either direction, or stay on one element (an internal step). So a journey inherits its relations' evidence: remove a relation and every journey that walks it fails the check, and a journey cannot claim a call the code does not make. A step against a relation's direction is drawn as a reply.

The deployment layout is arithmetic, not a layout engine: a tier's zones share the width by how many boxes they hold, and the lines are routed rather than placed. A line between adjacent tiers takes its own lane in the gap between them, lanes ordered so their runs cross as few lines as swaps allow, and each box's exits ordered by where each line goes. A line that skips a tier takes a lane in the gap it leaves by and one in the gap it enters by, joined down the left corridor. Two neighbors on one tier too close for a label loop through the gap below them (above, on the bottom tier). Labels sit where the fewest lines pass behind them, and zone headers slide clear of the lines entering their zone.

## Presentations

A deployment view can also be drawn for a room: measured boxes, routed connectors, a theme, and a walkthrough that highlights one step at a time. This is the diagram review's example 6, but generated from the model.

```bash
documentor tour --root . --view deployment --journey nda-review --theme synaptiq --out out/
ERASER_MODULES=... CHROMIUM_PATH=... node src/documentor/architecture/js/render.mjs out/    # writes out/present.html
```

| Comes from | Becomes |
|---|---|
| each zone and tier | an Eraser group, with its boxes inside it |
| each element | a box, outlined in the accent for the system's own code and dashed when not built |
| the deployment router's routes and label spots | each connector's ports, waypoints, and label position |
| the journey's steps, and each relation's `why` | the walkthrough's highlighted step and caption; without a journey, the view's relations in order |
| `--theme`, a ux-builder theme, or the project's `publish.theme` | the colors and font, under the model's own `[theme]` |

The presentation plays on one screen, never scrolled (`js/stage.mjs`). The overview frames the whole diagram; each step's camera glides to that step's boxes and line and zooms in as far as they allow, above the caption. A jump to a shot off screen pulls back to frame both, then flies in. Play advances on its own; drag pans, the wheel zooms, and `#step-N` in the address opens a step.

Eraser grows a box to fit its text, so the render runs twice: the first pass measures, and the second snaps each line's ends onto the measured edges. The presentation is output, like the SVG: never edited, regenerated when the model changes. The Python step needs only PyYAML; the render needs Node, `@eraserlabs/diagrams`, and a Chromium, so `check` never depends on it.

## The estate

Systems in different repositories describe each other from their own side. A model marks an element that is another repository's system with `system = "<id>"`, where the id is that repository's `[system].id`. An estate config lists the systems and where their models are:

```toml
title = "The program estate"
takeaway = "What is built, what calls what, and which repository to open."
host = "github.example.com"           # for --fetch; omit for github.com

[[system]]
id = "atlas"
repo = "the client/atlas-harness"
path = "../atlas-harness"          # a local checkout; with --fetch the model is read from the repository instead

[[system]]
id = "hohfeld"
repo = "the client/hohfeld"
```

`documentor estate check --config estate.toml` composes the models and fails when a connection is **one-sided**: A's model has a relation to an element marked `system = "B"`, and B's model has no relation in the same direction to an element marked `system = "A"`. Each repository keeps its own model checked against its own code; the estate checks that the repositories agree about each other. A model that names a system the estate does not include is a warning: the list of those is the estate's backlog.

`architecture_estate.py render --out <page>` writes the landscape: one node per system with its repository, one edge per agreed connection (dashed when either side is not `built`), a table of the models with the commit each was read at, and each connection as both sides state it. The page lives where the estate is governed (for the client, the engagement hub's architecture workstream) and is regenerated when any model moves; its first line names every model and commit it was built from.
