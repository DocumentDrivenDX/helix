# Contributing to HELIX

Read [AGENTS.md](AGENTS.md) for repository policy and the
[developer guide](docs/helix/04-build/developer-guide.md) for setup, repository
navigation, first contribution, debugging, and verification commands.

Start with the [solution overview](docs/helix/02-design/solution-overview.md)
and [architecture walkthrough](docs/helix/02-design/architecture-walkthrough.md)
if you are new to the codebase. Host installation instructions live in
[docs/install/README.md](docs/install/README.md).

Required checks before submitting changes:

```bash
just test
git diff --check
```

Keep pre-commit hooks enabled. Update canonical source and regenerate derived
outputs as described in the guide. Release work uses the runtime handoff
contract in `workflows/modes/runtime-handoff.md` and repository release
instructions; it requires a separately authorized release scope.
