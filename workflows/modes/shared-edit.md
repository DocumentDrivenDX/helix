# Shared Edit

Use when people and an agent should work on a governed document together in a shared editing surface (live editing, comments the agent answers) while the repository stays the record. Engage on: "edit this in a doc", "open it for review", "send it for review", "land the reviewer's edits", "sync the draft back". It needs a runtime that offers such a surface and the sync companion for it; without both, say so and edit the repository file directly only if the user asks.

A document that is `authoring.home: repo` stays that way: the surface holds a draft, never the document, and only a merged commit changes it. Which draft a file is bound to lives in the companion's binding file, never in the document's front matter.

## The companion: docsync

The sync is done by docsync, a separate plugin ([DocumentDrivenDX/docsync](https://github.com/DocumentDrivenDX/docsync)). It is optional: nothing else in HELIX needs it. Its skill owns the surface: opening a draft, reading what changed, landing edits as a word-level patch, writing the file's changes back, comments, suggestions, and the binding (`.docsync.json` and a `docsync` line in `.gitattributes`). Follow that skill for every step. Its surface today is Claude Docs.

Check that the docsync skill is available. If it is not, stop, say so, and give the install commands for the host. Do not install it unasked, and do not sync or patch the file by hand.

```sh
claude plugin marketplace add DocumentDrivenDX/plugins
claude plugin install docsync@documentdrivendx
```

```sh
codex plugin marketplace add DocumentDrivenDX/plugins
codex plugin add docsync@documentdrivendx
```

Installing it does not give a host the surface. docsync needs the Claude Docs tools and a git repository, and stops without them.

## What HELIX adds

Apply these to the docsync steps.

1. **Binding: say which side wins.** Read the document's `ddx.authoring.home` and pass it when binding: `repo` or absent is `--record git`; `external-tool` is `--record doc`. This is the project's instruction, so it needs no separate question. If `home` and an existing binding disagree, stop and ask.
2. **Applying edits: guard the generated tables.** Run every `apply` with `HELIX_GUARD_DOC=<FILE>` set in its environment, the same file it patches, and pass `--guard <plugin-root>/skills/helix/scripts/assessment-tables-guard`. The guard checks docsync's copy from beside that file, where the flow's `criteria.yml` and `keys.yml` are found. With the two set, docsync refuses an edit to a generated table (an assessment's Criteria and Comparison tables, a position paper's Recommendations and Decision Criteria tables). Make that change in the `assessment:`, `recommendations:`, or `weights:` block, then run `skills/helix/scripts/assessment-tables.py --write`; never write the table to match the draft. The guard needs PyYAML; if it cannot run, docsync refuses, and the guard stays.
3. **After landing.** Run `skills/helix/scripts/validate-instance.py` on the result. Open the pull request with the resolved comment threads as the review record.
4. **Changed hashes.** List each document whose file hash changed: anything keyed to the hash (a seal, a recorded review) is stale and is the project's to refresh.
5. **Local edits.** docsync has no edit hook. Run `docsync status` on a bound file when a sync starts, and after committing changes to one. Under `repo`, write the changes into the draft after the commit or merge, not on each edit. Under `external-tool`, warn that the draft wins before editing the file.

## Moving a binding made by draftsync

HELIX releases through v0.25.0 shipped their own tool, draftsync, which kept bindings in `.helix-bindings.yml`. docsync does not read that file. When one exists, move each binding before syncing:

1. With the draftsync from the release that made the binding, land the draft's edits, merge them, and write the file's changes back, until the draft equals the committed file.
2. With docsync, read the whole draft, `bind` the file to the same draft at the revision read, then `rebind` it with that read. `rebind` succeeds only if the draft and the file line up; if it refuses, remove the new entry, report why, and keep the old binding.
3. Once every file is moved, delete `.helix-bindings.yml`, the `*-bind` lines in `.gitattributes`, and any `draftsync hook` entry in `.claude/settings.json`; commit these with `.docsync.json`.

## Never

Overwrite the file with an export, edit front matter as text, get around a refusal by editing the file or the draft by hand, or treat resolved comments as an approval.

## Handoff

Name the draft, the base, what landed, what was refused and why, and the documents whose hashes changed.
