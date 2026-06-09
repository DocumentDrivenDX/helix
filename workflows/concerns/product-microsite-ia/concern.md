# Concern: Product Microsite IA

## Category
microsite

## Areas
site, docs, frontend

## Components

- **Audience model**: evaluators, first-time users, active users, contributors
- **Information architecture**: top-level sections, section landing pages, sidebar hierarchy, page-local outline
- **Conversion path**: first answer, proof, first action, reference lookup
- **Trust path**: claims, examples, source artifacts, operational proof
- **Navigation state**: current section, current page, sibling context, page-local headings
- **Responsive behavior**: desktop sidebar, mobile drawer, page outline, touch targets

## Constraints

- The homepage must answer what the product is before explaining how it works.
- The first viewport must name the product or category, state the core value,
  and expose a clear next action.
- Navigation must reflect user intent, not internal implementation structure.
- Section landing pages must orient the reader before sending them deeper.
- Sidebars must expose the most important leaf pages without forcing readers
  through abstract categories.
- Page-local navigation must be visibly subordinate to section navigation.
- Reference pages must preserve context: the reader should know what section,
  activity, or category they are in after landing on any leaf page.
- Generated reference pages must have deterministic ordering, stable active
  state, and human-readable titles.
- Supporting material may be grouped or disclosed, but core decision-making
  material must be visible without drilldown.
- Custom layout and CSS are allowed only when the site framework cannot express
  the required hierarchy, state, or responsive behavior.

## Content Guidelines

Product microsites need to serve four reader modes:

| Reader mode | User question | Required path |
|-------------|---------------|---------------|
| Evaluate | What is this, and is it worth my time? | Home, Why, proof, examples |
| Start | How do I try it correctly? | Getting Started, recipes, platform notes |
| Decide | What concept or artifact should I use next? | Concepts, artifact types, workflow |
| Operate | How do I look up exact behavior? | Reference, artifacts, commands, concerns |

Top-level IA should usually separate:

- **Why**: problem, thesis, principles, audience
- **Use**: installation, workflows, recipes, platform guidance
- **Types or Concepts**: reusable flow, artifact types, conceptual model
- **Reference**: exact command, API, concern, and generated catalog material
- **Artifacts or Examples**: worked examples and source-of-truth project docs

These names are not mandatory. The distinction is mandatory: do not mix
persuasion, onboarding, flow, and exact reference into one flat tree.

## Artifact and Reference Navigation

Artifact-type catalogs must help a reader answer "what should I create or read
next?" before they answer "what files exist?"

- Order artifact types by the activity where a user needs them.
- Show core artifacts first for each activity.
- Keep supporting artifacts visibly secondary through lighter treatment,
  disclosure, or a divider.
- Avoid global buckets that hide leaf nodes behind labels users do not already
  understand.
- Keep activity pages, core artifact pages, and supporting artifact pages in
  the same navigation model.
- Left navigation represents site hierarchy and current location.
- Right navigation represents headings inside the current page only.
- The two navs must reinforce each other: selecting a left-nav leaf should not
  make the reader lose sibling or parent context.

## Testing

- Screenshot the homepage, each top-level section, and representative deep
  reference pages on desktop and mobile.
- Verify active left-nav state for every generated reference page type.
- Verify page-local right nav has only headings from the current page.
- Verify core reference pages are reachable without expanding supporting-only
  categories.
- Verify supporting pages remain discoverable through their parent activity.
- Verify mobile navigation reaches the same pages as desktop navigation.

## Quality Gates

- A first-time reader can identify the product, audience, value, and first
  action from the homepage without opening another page.
- A user landing on any generated reference page can identify its parent
  section and nearest sibling pages.
- Core reference pages are visible in the primary section navigation.
- Supporting pages are differentiated without becoming undiscoverable.
- Right-nav styling is subordinate to left-nav styling and has no decorative
  treatment that competes with page content.
- Navigation screenshots show no clipped text, overlapping elements, cramped
  controls, or inconsistent active state.

## When to use

Any project with a public-facing product, flow, platform, or developer
tool microsite. This concern is especially important when the site includes
generated reference content, artifact catalogs, demos, or documentation that
serves both evaluators and active users.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: information-architecture model (reader modes, top-level sections, nav state) for the microsite

## ADR References
