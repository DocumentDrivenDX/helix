# Claude Notes

See [AGENTS.md](AGENTS.md) for the main repository instructions.

Claude-specific notes:

- prefer `ddx agent run --harness claude` for non-interactive reproducible runs
- for interactive work, use Claude Code sessions with the unified HELIX skill
  via `/helix <mode>` (e.g. `/helix input`, `/helix align`, `/helix frame`,
  `/helix design`, `/helix evolve`, `/helix review`)
- `ddx agent run` is the dispatch surface — avoid calling `claude -p` directly
  in examples or docs
- to deploy HELIX to a Databricks workspace (Genie), follow the runbook at
  [docs/install/databricks-genie.md](docs/install/databricks-genie.md); the
  `just genie-build` / `just genie-install` / `just genie-verify` recipes wrap
  it (needs `DATABRICKS_HOST`+`DATABRICKS_TOKEN`, or a `DATABRICKS_PROFILE`)
- site content lives under `docs/website/content/` (Hugo machinery stays in
  `website/`); hand-authored prose is governed by `docs/website/CLAUDE.md` and
  linted with `just lint-prose` (Vale)
- when changing surfaces that touch the runtime boundary (queue, beads,
  agent dispatch), check:
  - `docs/helix/00-discover/product-vision.md` and `docs/helix/01-frame/prd.md`
    for the target shape (content + one skill; DDx owns the runtime)
  - `workflows/principles.md` and `workflows/ratchets.md` for methodology
    invariants (in flux — verify before relying on)
  - `tests/validate-skills.sh` for skill packaging behaviour the current
    skill preserves

<!-- DDX-META-PROMPT:START -->
<!-- Source: claude/system-prompts/focused.md -->
# System Instructions

**Execute ONLY what is requested:**

- **YAGNI** (You Aren't Gonna Need It): Implement only specified features. No "useful additions" or "while we're here" features.
- **KISS** (Keep It Simple, Stupid): Choose the simplest solution that meets requirements. Avoid clever code or premature optimization.
- **DOWITYTD** (Do Only What I Told You To Do): Stop when the task is complete. No extra refactoring, documentation, or improvements unless explicitly requested.

**Response Style:**
- Be concise and direct
- Skip preamble and postamble
- Provide complete information without unnecessary elaboration
- Stop immediately when the task is done

**When coding:**
- Write only code needed to pass tests
- No gold-plating or speculative features
- Follow existing patterns and conventions
- Add only requested functionality

<!-- DDX-META-PROMPT:END -->
