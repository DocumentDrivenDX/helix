# Install HELIX

HELIX is a methodology, an artifact-type catalog, and a single routing
skill. It is not a CLI, a tracker, or a runtime. To use HELIX you make
its content discoverable from the runtime you already use. This index
points at the per-runtime install guides and states the minimal runtime
contract HELIX assumes.

The source content is the same across every runtime. Per-runtime guides
describe **discovery and invocation only**. They do not fork the skill
or the catalog. See [No-fork policy](#no-fork-policy) below.

## Minimal runtime contract

A HELIX-compliant runtime can:

1. **Read markdown files** from the project's filesystem.
2. **Write markdown files** to the project's filesystem.
3. **Search files** by path or pattern across the project.
4. **Optionally execute a shell command** for verification or build/run modes.

That is the full contract. HELIX assumes nothing else — no tracker, no
queue, no execution loop, no IDE integration, no language toolchain.
This contract is the binding form of PRD R-4 (runtime-neutral content)
and the Constraints section. Items 1–3 are required; item 4 is optional
and only some routes (`build`, `run`, `commit`, `release`) make use of it.

If your runtime satisfies items 1–3, HELIX's alignment, framing,
design, evolve, validate, and review routes all work. If it also
satisfies item 4, the execution-oriented routes become available.

## Source of truth

The runtime install guides are packaging notes. The normative HELIX
content lives in two places in this repo:

- [`skills/helix/SKILL.md`](../../skills/helix/SKILL.md) — the single
  routing skill. One public entry point (`helix`), one routing table,
  one set of per-mode workflow contracts. There are no separate public
  `helix-*` skills.
- [`workflows/`](../../workflows/) — the artifact-type catalog and
  methodology specification. `workflows/activities/00-discover` through
  `workflows/activities/06-iterate` carry the artifact templates,
  prompts, quality criteria, and examples.
  `workflows/principles.md`, `workflows/ratchets.md`, and
  `workflows/artifact-schema.md` carry the methodology invariants.

When a per-runtime guide and the skill or catalog disagree, the skill
and catalog win. The guides are about how a particular runtime finds
and invokes this content, not about what the content says.

## Per-runtime install guides

Five supported runtimes. Each guide is self-contained: file layout,
install steps, invocation, and verification. Pick the one that matches
your environment; install more than one if you use more than one.

### [DDx](https://github.com/DocumentDrivenDX/ddx)

```bash
ddx install helix
```

DDx is the reference runtime. `ddx install helix` clones HELIX into
`~/.ddx/plugins/helix/` (uses the Claude Code plugin format, so the
same content serves both runtimes).

**Best fit for:** the full HELIX-plus-runtime experience. DDx provides
the bead queue, execution loop, evidence capture, and worker process
that drives HELIX modes against a tracked work plan.

### [Claude Code](claude-code.md)

```bash
claude plugin marketplace add https://github.com/DocumentDrivenDX/helix
claude plugin install helix@helix --scope user -y
```

Install via the Claude Code plugin marketplace. The HELIX repo ships
both the plugin manifest and the marketplace listing.

**Best fit for:** local development with full read/write/search and
shell access. Supports every HELIX route, including `build` and `run`.

### [OpenAI Codex CLI](codex.md)

```bash
npx skills add DocumentDrivenDX/helix -a codex
```

Install via the Vercel Labs Skills CLI (the cross-runtime install
helper from agentskills.io). Drops HELIX into `~/.codex/skills/helix/`
for filesystem-scan auto-discovery. A direct filesystem-copy fallback
is available for Dockerfile/no-Node environments.

**Best fit for:** terminal-native Codex sessions with full agentskills
spec compliance.

### [GitHub Copilot](copilot.md)

```bash
# adopter repo: copy .github/copilot-instructions.md from the HELIX repo
cp helix/.github/copilot-instructions.md .github/
git add .github/copilot-instructions.md && git commit
```

Auto-discovered across VS Code/JetBrains/Xcode/Eclipse Copilot Chat,
github.com Copilot Chat, code review, cloud agent, and Copilot CLI.
No install command beyond committing the file.

**Best fit for:** Copilot-using teams adopting HELIX as a repo-scoped
methodology. The legacy GitHub App Extensions path is retired (Nov
2025); MCP servers remain an option for future tool-using extensions.

### [Databricks Genie Code](databricks-genie.md)

```bash
bash scripts/build-genie-bundle.sh
python scripts/install-genie.py
python scripts/verify-genie.py
```

Build the bundle locally, upload via the Databricks Python SDK to
`/Workspace/.assistant/skills/helix/`, then verify offline. End-to-end
verification of skill activation requires manual browser interaction
with Genie Code (no public chat API).

**Best fit for:** Databricks-resident teams who want HELIX governance
to live alongside their data and notebook work. Methodology-only —
execution-oriented routes typically land in Databricks jobs/notebooks
or CI pipelines rather than inline.

## Refresh: keeping your HELIX tree current

Refresh is a first-class HELIX mode that brings every artifact instance
under a project HELIX tree up to date with the current canonical
templates and prompts. Each runtime supports Refresh with different
fan-out mechanisms: DDx via `ddx agent run --harness <activity>` per
activity directory (parallel), Claude Code via the Agent tool per activity
(parallel), and Codex CLI via `codex agent` sub-runs per activity (parallel).
Databricks Genie Code and GitHub Copilot do not have sub-agent dispatch,
so Refresh runs sequentially through each activity directory in order.
All runtimes use the same underlying HELIX methodology for validation
and artifact updates.

## Convergence point: agentskills.io

Claude Code, Codex CLI, Cursor, VS Code/Copilot, Gemini CLI, and
Databricks Genie Code all adopt the open
[Agent Skills specification](https://agentskills.io/specification).
HELIX's `skills/helix/SKILL.md` is agentskills-compliant: required
`name` and `description` frontmatter, parent directory name equal to
`name:`, progressive-disclosure layout with heavy content in
`references/` (or, in HELIX's case, `workflows/`).

The cross-runtime install helper `npx skills add` (from Vercel Labs)
works for runtimes that load skills from local filesystem paths
(Claude Code, Codex CLI). It does NOT install to Genie's
`/Workspace/.assistant/skills/` (use `scripts/install-genie.py`
instead) and is not the canonical path for Copilot
(`.github/copilot-instructions.md` commit) or DDx (`ddx install
helix`).

## No-fork policy

The per-runtime guides exist so adopters can install HELIX. They do
not exist to localize, dialect, or rewrite the methodology.

- The normative skill body lives in `skills/helix/SKILL.md` and
  nowhere else. Per-runtime guides may quote it for orientation but
  must not paste a divergent copy.
- The artifact catalog lives in `workflows/` and nowhere else.
  Per-runtime guides may describe the directory layout (so users know
  what they are vendoring) but must not redefine artifact types,
  templates, or quality criteria.
- If a runtime genuinely requires content adaptation — for example, a
  manifest file, a wrapper instruction file, or a packaging metadata
  document — that adaptation lives **inside the per-runtime install
  guide**, clearly marked as a runtime-specific shim. It does not get
  pushed back into `skills/` or `workflows/`.
- A per-runtime guide that introduces normative HELIX behavior the
  other guides do not share is a bug against PRD R-4 and R-7. File it
  as a HELIX alignment finding.

This policy is what makes "the source content is the same across every
runtime" enforceable. Five install paths, one HELIX.

## Engineer-facing mechanism research

The user-facing per-runtime guides keep packaging notes minimal. For
mechanism details — what commands exist, manifest schemas, headless
testing surfaces — see the research notes:

- [docs/resources/agents/agentskills-spec.md](../resources/agents/agentskills-spec.md)
- [docs/resources/agents/claude-code-plugins.md](../resources/agents/claude-code-plugins.md)
- [docs/resources/agents/openai-codex-cli-skills.md](../resources/agents/openai-codex-cli-skills.md)
- [docs/resources/agents/github-copilot-instructions.md](../resources/agents/github-copilot-instructions.md)
- [docs/resources/agents/databricks-genie-code-skills.md](../resources/agents/databricks-genie-code-skills.md)
- [docs/resources/agents/ddx-plugins.md](../resources/agents/ddx-plugins.md)

## Homepage linking

The HELIX website homepage links to `website/content/install/_index.md`,
which mirrors this index as an in-site Hugo page. The homepage carries
a dedicated "Install HELIX in your runtime" section with per-runtime
CTA cards and a "Read the full install index" link.

## See also

- [`skills/helix/SKILL.md`](../../skills/helix/SKILL.md) — routing
  skill and per-mode workflow contracts.
- [`workflows/README.md`](../../workflows/README.md) — methodology
  overview.
- [`workflows/principles.md`](../../workflows/principles.md) and
  [`workflows/ratchets.md`](../../workflows/ratchets.md) — methodology
  invariants.
- [`docs/helix/01-frame/prd.md`](../helix/01-frame/prd.md) — PRD,
  including R-4 (runtime-neutral content), R-7 (per-runtime packages),
  and the Constraints section that defines the minimal runtime
  contract.
- [FEAT-013](../helix/01-frame/features/FEAT-013-runtime-install-coverage.md)
  and [TD-013](../helix/02-design/technical-designs/TD-013-multi-runtime-install.md)
  — the feature spec and technical design driving this install matrix.
