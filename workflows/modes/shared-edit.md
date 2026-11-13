# Shared Edit

Use when people and an agent should work on a governed document together in a shared editing surface (live editing, comments the agent answers) while the repository stays the record. Engage on: "edit this in a doc", "open it for review", "send it for review", "land the reviewer's edits", "sync the draft back". It needs a runtime that offers such a surface; a runtime that does not says so and edits the repository file directly. Surface-specific steps are in an adapter reference named in step 1.

The document stays `authoring.home: repo`: the surface holds a draft, never the document. Only a merged commit changes it. Which draft a file is bound to lives in `.helix-bindings.yml` (see "Keeping a file bound to its draft"), never in the document's front matter.

The host tool is draftsync (`tools/draftsync/` in the HELIX repository), released with HELIX like documentor. It does the deterministic part (parse, patch, merge, check) offline; the agent does what only the agent can, the calls to the surface. Install it once from the HELIX release the project uses:

```sh
uv tool install "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/draftsync"
```

`draftsync --help` lists its commands. In a HELIX checkout, `uv run --project tools/draftsync draftsync ...` runs it without installing. Without the tool, say so and stop; do not patch the file by hand.

## 1. Open

1. Choose the document and confirm it has no uncommitted changes.
2. Create one draft in the surface from the body only. The front matter stays in git and is never offered for editing. Note the draft's address and the revision it was created at.
3. Bind the file: `draftsync bind FILE --tool claude-docs --origin <the draft's address> --synced-rev <that revision>`. It writes the entry in `.helix-bindings.yml` and the `<tool>-bind` line in `.gitattributes`; commit both. Anyone with access to the draft can now sync the file.
4. Offer the local-edit hook (below). A repository with bound files adds it once.
5. Read the adapter for the runtime's surface (`workflows/references/shared-edit-claude-docs.md` for the Claude Docs connector). No adapter, or no surface in this runtime: stop and say so.

Git is untouched while people and the agent edit and comment in the draft.

## 2. Land

1. Ask the surface for what changed since the recorded revision, never for a full export, and translate it into `EDITS.json` (operations addressed by block index; `draftsync blocks FILE` prints the index at the base). For the Claude Docs surface the adapter names the two reads and `draftsync edits` does the translation and checks that the old draft and the file line up. The format is in the script's header.
2. Run `draftsync apply FILE --edits EDITS.json --base-commit BASE`. It applies only the changed words, so untouched text stays byte-identical, merges into the current file when the file changed since the base, and prints the diff and the file's hash before and after. Review the diff, then run it again with `--write`.
3. Handle a refusal, never route around it:
   - a generated table (an assessment's Criteria and Comparison tables, a position paper's Recommendations table) was edited: make the change in the `assessment:` or `recommendations:` block by hand, then run `skills/helix/scripts/assessment-tables.py --write`; never write the table to match the draft;
   - the file moved and an edit conflicts: ask the reviewer which text wins;
   - code, a quote, HTML, or a numbered item that would need renumbering: edit it in the repository.
4. Run `skills/helix/scripts/validate-instance.py` on the result. Open the pull request with the resolved comment threads as the review record, and list each document whose file hash changed: anything keyed to the hash (a seal, a recorded review) is stale and is the project's to refresh.

## Never

Overwrite the file with an export, edit front matter as text, apply an edit the tool refused by hand-editing around it, or treat resolved comments as an approval.

## Handoff

Name the draft, the base, what landed, what was refused and why, and the documents whose hashes changed.

## Keeping a file bound to its draft

A file bound to a draft (ADR-020) is synced in both directions. The binding is one entry in `.helix-bindings.yml` plus a `<tool>-bind` line in `.gitattributes` (`draftsync bind FILE --tool claude-docs --origin URL --synced-rev N` writes both); `draftsync status FILE` shows it and says whether the file changed since the base. The system of record is the document's `ddx.authoring.home`: `repo` or absent means git wins a conflict, `external-tool` means the draft does.

1. **Draft to git.** Read the draft as in step 2 above, but pass `--from-binding` to `edits` and `apply`: the base is the file body the binding names, found in git history, and a conflict resolves toward the record. The report on stderr lists what lost. Open the pull request as before.
2. **Git to draft, after the merge.** Read the draft at the bound revision (`OLD.xml`) and now in full (`NOW.xml`), then run `draftsync doc-ops FILE --old OLD.xml --now NOW.xml --from-binding`. It prints `ops` and a `report`. Send `ops` as the `payload.ops` of one `update` on the draft's body. Edits replace only changed words and are guarded by the draft's revision; if a guard refuses, someone edited meanwhile, so read again and rerun. The `report` lists conflicts and the changes it left to a person (formatting, a new list or table, a block the draft deleted).
3. **Rebind** when later reads get long: once the draft equals a committed file body, `draftsync rebind FILE --synced-rev N --old OLD.xml` (the draft at N) moves the binding, after checking the draft against the file.

A Claude Code hook can tell the agent when a bound file is edited locally. A repository with bound files registers it in `.claude/settings.json`; it does nothing for unbound files, and it needs `draftsync` on the PATH (the uv tool install above):

```json
{"hooks": {"PostToolUse": [{"matcher": "Edit|Write|MultiEdit",
  "hooks": [{"type": "command", "command": "draftsync hook"}]}]}}
```

Under `repo` the agent syncs after the commit or merge, not on each edit; under `external-tool` it warns that the draft wins. Edits made through a shell command do not trigger the hook, so check `draftsync status` when a sync starts.
