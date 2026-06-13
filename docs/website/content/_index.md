---
title: HELIX
layout: hextra-home
---

<div class="helix-hero-layout">
<div class="helix-hero-copy">

{{< hextra/hero-badge link="why/the-thesis" >}}
  <span>See the details</span>
  {{< icon name="arrow-circle-right" attributes="height=14" >}}
{{< /hextra/hero-badge >}}

{{< hextra/hero-headline >}}
Product lifecycle for AI.
{{< /hextra/hero-headline >}}

{{< hextra/hero-subtitle >}}
Agents do better work with context they can trust. HELIX is a document discipline for teams building software with agents. It turns project intent and evidence into shared memory, then keeps that memory current as the work changes.
{{< /hextra/hero-subtitle >}}

<div class="helix-hero-actions" aria-label="Homepage actions">
  <a class="helix-hero-action-primary" href="use/getting-started">Start with HELIX</a>
  <a class="helix-hero-action-secondary" href="artifact-types">Browse the catalog</a>
</div>

</div>
<figure class="helix-hero-image-panel" aria-label="Document spine double helix">
  <img class="helix-hero-image helix-hero-image-light" src="hero/concepts/document-spine-helix-light-2026-05-12.png" alt="A document spine double helix connecting human intent, AI execution, and governed artifacts." />
  <img class="helix-hero-image helix-hero-image-dark" src="hero/concepts/document-spine-helix-dark-2026-05-12.png" alt="" aria-hidden="true" />
</figure>
</div>

<div class="hx-mt-16"></div>

<section class="helix-home-section">

<div class="helix-section-kicker">Get started</div>

## Install HELIX in your runtime

HELIX works with Claude Code, Codex CLI, GitHub Copilot, and Databricks Code Genie.
Pick the guide for your environment and you're up in minutes.

<div class="helix-home-grid helix-platform-grid">
  <a class="helix-home-card" href="install">
    <span class="helix-card-label">Claude Code</span>
    <strong>Install as a Claude Code skill</strong>
    <span>User-global or per-repo. Installs the single <code>helix</code> routing skill.</span>
  </a>
  <a class="helix-home-card" href="install">
    <span class="helix-card-label">Codex CLI + Copilot</span>
    <strong>Discover via AGENTS.md or editor instructions</strong>
    <span>Full flow on the Codex CLI; read-mostly HELIX work on Copilot surfaces.</span>
  </a>
  <a class="helix-home-card" href="install">
    <span class="helix-card-label">Databricks Code Genie</span>
    <strong>Skill bundle in workspace storage</strong>
    <span>Shared across the workspace, next to your data and notebook work.</span>
  </a>
</div>

<p class="helix-section-footer">
  <a href="install">Read the full install index <span aria-hidden="true">→</span></a>
</p>

</section>

<div class="hx-mt-16"></div>

<section class="helix-home-section">

## How it works

<p class="helix-section-intro">
  Getting started with HELIX is simple: install it into your agent, then work
  through prompts as you normally would. The HELIX skill helps the agent read
  and update the document graph while you stay in control. That graph gives the
  agent the context it needs to create, check, and hand off quality plans.
</p>

<div class="helix-home-grid helix-loop-steps">
  <a class="helix-home-card" href="artifact-types">
    <span class="helix-card-label">1 · Write the brief</span>
    <span>Say what the agent should know. Capture the goal, requirements, constraints, and decisions before the agent starts changing files.</span>
  </a>
  <a class="helix-home-card" href="artifacts">
    <span class="helix-card-label">2 · Check alignment</span>
    <span>Find stale assumptions, missing context, and contradictions across the document graph.</span>
  </a>
  <a class="helix-home-card" href="skills">
    <span class="helix-card-label">3 · Create the work plan</span>
    <span>Turn the documents into bounded work. Define what to change, what not to change, how to check success, and what evidence to collect.</span>
  </a>
  <a class="helix-home-card" href="platforms">
    <span class="helix-card-label">4 · Hand off to a runtime</span>
    <span>Send the plan to the place work gets done. Use DDx, Claude, Codex, Databricks, or a manual workflow. Capture the result and feed it back into the documents.</span>
  </a>
</div>

<p class="helix-section-footer">
  <a href="reference/demos/">See it in action <span aria-hidden="true">→</span></a>
</p>

</section>

<div class="hx-mt-16"></div>

<section class="helix-home-section">

## Artifact spine

HELIX includes many artifact types, but to get started you only need a few.
Begin with the spine, then add supporting artifacts as the work demands them.

<div class="helix-spine-flow" aria-label="Core HELIX artifact spine">
  <a href="artifact-types/discover/product-vision/"><span>01</span><strong>Product Vision</strong><em>Intent</em></a>
  <a href="artifact-types/frame/prd/"><span>02</span><strong>PRD</strong><em>Requirements</em></a>
  <a href="artifact-types/frame/principles/"><span>03</span><strong>Principles</strong><em>Judgment</em></a>
  <a href="artifact-types/frame/feature-specification/"><span>04</span><strong>Feature Specs</strong><em>Scope</em></a>
  <a href="artifact-types/design/architecture/"><span>05</span><strong>Architecture</strong><em>Structure</em></a>
  <a href="artifact-types/test/test-plan/"><span>06</span><strong>Test Plans</strong><em>Proof</em></a>
  <a href="artifact-types/build/implementation-plan/"><span>07</span><strong>Implementation Plans</strong><em>Execution</em></a>
</div>

</section>

<div class="hx-mt-16"></div>

<section class="helix-home-section">

## Use more than one flow scope

<p class="helix-section-intro">
  A product and its documentation site can both use HELIX without becoming two
  public skills. Declare separate flow scopes, keep each artifact stack in its
  own root, and let the same <code>helix</code> routing skill choose the right
  workflow mode for the scope.
</p>

<div class="helix-home-grid helix-proof-grid">
  <a class="helix-home-card helix-card-human" href="use/multiple-flows">
    <span class="helix-card-label">Multiple flows</span>
    <strong>Product docs and microsite docs can live side by side</strong>
    <span>Learn the marker shape, scope rules, and microsite-docs template pattern.</span>
  </a>
  <a class="helix-home-card helix-card-connect" href="artifacts">
    <span class="helix-card-label">Dogfood example</span>
    <strong>HELIX renders its own docs as a separate example corpus</strong>
    <span>This generated area is proof and source traceability, not adopter doctrine.</span>
  </a>
</div>

</section>

<div class="hx-mt-16"></div>

<section class="helix-home-section">

<div class="helix-section-kicker">Runtime paths</div>

## Use HELIX where your team already works

HELIX is Markdown and methodology. The runtime supplies file editing, review,
execution, and evidence capture.

<div class="helix-home-grid helix-platform-grid">
  <a class="helix-home-card" href="use/manual-recipe">
    <span class="helix-card-label">Manual</span>
    <strong>Small teams adopting the method first</strong>
    <span>Start with Markdown, reviews, and explicit prompts before adding queue automation.</span>
  </a>
  <a class="helix-home-card" href="use/claude-code-recipe">
    <span class="helix-card-label">Claude Code</span>
    <strong>Interactive artifact review and editing</strong>
    <span>Ask an agent to reconcile documents, propose patches, and explain open questions.</span>
  </a>
  <a class="helix-home-card" href="use/codex-recipe">
    <span class="helix-card-label">Codex</span>
    <strong>Codebase-aware planning and implementation</strong>
    <span>Use the artifact spine to guide bounded code changes and implementation plans.</span>
  </a>
  <a class="helix-home-card" href="use/ddx-runtime">
    <span class="helix-card-label">DDx</span>
    <strong>Reference runtime for queued execution</strong>
    <span>Map HELIX plans to beads when queue control and execution evidence matter.</span>
  </a>
  <a class="helix-home-card" href="use/databricks-recipe">
    <span class="helix-card-label">Databricks</span>
    <strong>Data and governance workflows</strong>
    <span>Apply HELIX artifacts to analytical systems, platform work, and managed evidence.</span>
  </a>
</div>

</section>

<div class="hx-mt-16"></div>

<section class="helix-home-section">

<div class="helix-section-kicker">Proof</div>

## Inspect the foundations

The method is public: the catalog, research foundation, and HELIX dogfood corpus
are all inspectable. The dogfood corpus shows how this repository applies
HELIX to itself; the reusable doctrine lives in the catalog and use guides.

<div class="helix-home-grid helix-proof-grid">
  <a class="helix-home-card helix-card-human" href="artifacts">
    <span class="helix-card-label">Dogfood corpus</span>
    <strong>HELIX governs itself in public</strong>
    <span>Read the generated self-docs with source links and historical context labels.</span>
  </a>
  <a class="helix-home-card helix-card-ai" href="artifact-types">
    <span class="helix-card-label">Artifact catalog</span>
    <strong>Reusable prompts, templates, and quality guidance</strong>
    <span>Browse the document types and learn which ones are core versus supporting.</span>
  </a>
  <a class="helix-home-card helix-card-connect" href="research">
    <span class="helix-card-label">Research foundations</span>
    <strong>Why document-driven AI work needs governance</strong>
    <span>Trace the methodology back to the research and operating assumptions that shaped it.</span>
  </a>
</div>

</section>
