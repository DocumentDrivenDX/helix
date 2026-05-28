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
  <a class="helix-hero-action-secondary" href="artifacts">Inspect the proof</a>
</div>

</div>
<figure class="helix-hero-loop" role="img" aria-label="HELIX lifecycle loop from artifacts through alignment review, implementation plan, runtime execution, and evidence or drift back into artifacts">
  <div class="helix-loop-center">Shared memory loop</div>
  <div class="helix-loop-node helix-loop-artifacts">
    <span>01</span>
    <strong>Artifacts</strong>
    <em>Intent, requirements, principles, and designs</em>
  </div>
  <div class="helix-loop-node helix-loop-review">
    <span>02</span>
    <strong>Alignment review</strong>
    <em>Find stale assumptions before execution</em>
  </div>
  <div class="helix-loop-node helix-loop-plan">
    <span>03</span>
    <strong>Implementation plan</strong>
    <em>Bound the change and the verification gate</em>
  </div>
  <div class="helix-loop-node helix-loop-runtime">
    <span>04</span>
    <strong>Runtime execution</strong>
    <em>Human, agent, or queued delivery surface</em>
  </div>
  <div class="helix-loop-node helix-loop-evidence">
    <span>05</span>
    <strong>Evidence / drift</strong>
    <em>Results update the documents or expose gaps</em>
  </div>
  <div class="helix-loop-role helix-loop-human">Human judgment</div>
  <div class="helix-loop-role helix-loop-agent">Agent work</div>
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
    <span>User-global or per-repo. Supports every HELIX route including build and run.</span>
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
  agent the context it needs to create, execute, and refine quality plans.
</p>

<div class="helix-home-grid helix-loop-steps">
  <a class="helix-home-card" href="artifact-types">
    <span class="helix-card-label">1 · Write the brief</span>
    <span>Say what the agent should know. Capture the goal, requirements, constraints, and decisions before the agent starts changing files.</span>
  </a>
  <a class="helix-home-card" href="artifacts">
    <span class="helix-card-label">2 · Check alignment</span>
    <span>Find what no longer matches. Use HELIX to catch stale assumptions, missing context, and contradictions across the document graph.</span>
  </a>
  <a class="helix-home-card" href="skills">
    <span class="helix-card-label">3 · Create the work plan</span>
    <span>Turn the documents into bounded work. Define what to change, what not to change, how success will be checked, and what evidence to collect.</span>
  </a>
  <a class="helix-home-card" href="platforms">
    <span class="helix-card-label">4 · Run it in the factory</span>
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
  <a href="artifacts/product-vision/"><span>01</span><strong>Product Vision</strong><em>Intent</em></a>
  <a href="artifacts/prd/"><span>02</span><strong>PRD</strong><em>Requirements</em></a>
  <a href="artifacts/principles/"><span>03</span><strong>Principles</strong><em>Judgment</em></a>
  <a href="artifacts/features/"><span>04</span><strong>Feature Specs</strong><em>Scope</em></a>
  <a href="artifacts/architecture/"><span>05</span><strong>Architecture</strong><em>Structure</em></a>
  <a href="artifacts/test-plans/"><span>06</span><strong>Test Plans</strong><em>Proof</em></a>
  <a href="artifacts/implementation-plan/"><span>07</span><strong>Implementation Plans</strong><em>Execution</em></a>
</div>

</section>

<div class="hx-mt-16"></div>

<section class="helix-home-section">

## Worked example: HELIX governs itself

<p class="helix-example-subhead">
  The graph below shows HELIX's own governing artifacts on the same spine.
  Hover each document to see what changed and the kind of prompt used in the
  public screencasts.
</p>

<div class="helix-authority-graph helix-annotated-graph" aria-label="HELIX governing artifact relationship graph">
  <div class="helix-strand-label helix-human-label">
    <strong>Human judgment</strong>
    <span>Manual edits + prompts</span>
  </div>
  <div class="helix-strand-label helix-ai-label">
    <strong>AI execution</strong>
    <span>Alignment reviews + updates</span>
  </div>
  <div class="helix-graph-visual" aria-hidden="true">
    {{< helix-hero >}}
  </div>
  <a class="helix-graph-node helix-node-left helix-node-vision" href="artifacts/product-vision/">
    <b class="helix-step">01</b>
    <span>Intent</span>
    <strong>Product Vision</strong>
    <em>Why HELIX exists.</em>
    <span class="helix-node-hover">
      <span>The frame prompt created the first intent document before requirements or code.</span>
      <code>Create the HELIX product vision.</code>
    </span>
  </a>
  <a class="helix-graph-node helix-node-right helix-node-prd" href="artifacts/prd/">
    <b class="helix-step">02</b>
    <span>Requirements</span>
    <strong>PRD</strong>
    <em>What HELIX provides and refuses.</em>
    <span class="helix-node-hover">
      <span>The same frame prompt turned intent into concrete product requirements.</span>
      <code>Create the HELIX PRD.</code>
    </span>
  </a>
  <a class="helix-graph-node helix-node-left helix-node-features" href="artifacts/features/">
    <b class="helix-step">04</b>
    <span>Scope</span>
    <strong>Feature Specs</strong>
    <em>Capabilities derived from requirements.</em>
    <span class="helix-node-hover">
      <span>The frame prompt decomposed the PRD into acceptance-backed feature work.</span>
      <code>Create feature specs from the HELIX PRD.</code>
    </span>
  </a>
  <a class="helix-graph-node helix-node-right helix-node-principles" href="artifacts/principles/">
    <b class="helix-step">03</b>
    <span>Constraint</span>
    <strong>Principles</strong>
    <em>Values for design and review.</em>
    <span class="helix-node-hover">
      <span>Review prompts use the governing documents to catch omissions and drift.</span>
      <code>Review HELIX against its governing principles.</code>
    </span>
  </a>
  <a class="helix-graph-node helix-node-left helix-node-architecture" href="artifacts/architecture/">
    <b class="helix-step">05</b>
    <span>Structure</span>
    <strong>Architecture</strong>
    <em>Boundaries and system shape.</em>
    <span class="helix-node-hover">
      <span>The design prompt translated scoped requirements into a technical shape.</span>
      <code>Create the HELIX architecture.</code>
    </span>
  </a>
  <a class="helix-graph-node helix-node-right helix-node-tests" href="artifacts/test-plans/">
    <b class="helix-step">06</b>
    <span>Proof</span>
    <strong>Test Plans</strong>
    <em>Executable expectations.</em>
    <span class="helix-node-hover">
      <span>The test prompt asked for red tests before implementation touched the code.</span>
      <code>Create test plans for the HELIX feature specs.</code>
    </span>
  </a>
  <a class="helix-graph-node helix-node-left helix-node-implementation" href="artifacts/implementation-plan/">
    <b class="helix-step">07</b>
    <span>Execution handoff</span>
    <strong>Implementation Plans</strong>
    <em>Scoped runtime work.</em>
    <span class="helix-node-hover">
      <span>The implementation prompt sent bounded work to the runtime with a test gate.</span>
      <code>Create a HELIX implementation plan.</code>
    </span>
  </a>
  <div class="helix-collaboration-note">
    Humans provide judgement and quality, steering with edits and prompts.
    Agents review, propose updates to keep the artifact stack coherent,
    create implementation plans and execute them.
  </div>
  <div class="helix-diagram-popover" aria-hidden="true">
    <span class="helix-diagram-popover-copy"></span>
    <code class="helix-diagram-popover-prompt"></code>
  </div>
</div>

<script>
(() => {
  const graph = document.querySelector(".helix-annotated-graph");
  if (!graph) return;

  const popover = graph.querySelector(".helix-diagram-popover");
  const copy = popover?.querySelector(".helix-diagram-popover-copy");
  const prompt = popover?.querySelector(".helix-diagram-popover-prompt");
  if (!popover || !copy || !prompt) return;

  const clamp = (value, min, max) => Math.max(min, Math.min(value, max));

  const show = (node) => {
    const source = node.querySelector(".helix-node-hover");
    const sourceCopy = source?.querySelector("span");
    const sourcePrompt = source?.querySelector("code");
    if (!sourceCopy || !sourcePrompt) return;

    copy.textContent = sourceCopy.textContent.trim();
    prompt.textContent = sourcePrompt.textContent.trim();
    popover.classList.add("is-visible");
    popover.setAttribute("aria-hidden", "false");

    requestAnimationFrame(() => {
      const graphRect = graph.getBoundingClientRect();
      const nodeRect = node.getBoundingClientRect();
      const popRect = popover.getBoundingClientRect();
      const nodeCenterY = nodeRect.top - graphRect.top + nodeRect.height / 2;
      const leftNode = nodeRect.left + nodeRect.width / 2 < graphRect.left + graphRect.width / 2;
      const centerX = graphRect.width / 2;
      const x = leftNode
        ? centerX - popRect.width - 28
        : centerX + 28;
      const y = clamp(nodeCenterY - popRect.height / 2, 84, graphRect.height - popRect.height - 24);

      popover.style.left = `${x}px`;
      popover.style.top = `${y}px`;
    });
  };

  const hide = () => {
    popover.classList.remove("is-visible");
    popover.setAttribute("aria-hidden", "true");
  };

  graph.querySelectorAll(".helix-graph-node").forEach((node) => {
    node.addEventListener("mouseenter", () => show(node));
    node.addEventListener("focus", () => show(node));
    node.addEventListener("mouseleave", hide);
    node.addEventListener("blur", hide);
  });
})();
</script>

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
    <span>Use Markdown, reviews, and explicit prompts before adding queue automation.</span>
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

The method is public: the catalog, HELIX's own governing artifacts, and the
research foundation are all inspectable.

<div class="helix-home-grid helix-proof-grid">
  <a class="helix-home-card helix-card-human" href="artifacts">
    <span class="helix-card-label">Worked artifacts</span>
    <strong>HELIX governs itself in public</strong>
    <span>Read the actual vision, PRD, principles, contracts, designs, and alignment reviews behind the project.</span>
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
