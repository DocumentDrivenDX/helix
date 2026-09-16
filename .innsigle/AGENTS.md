# Agent instructions: Innsigle publish + seal

You are wiring Innsigle into this repository. Innsigle stores all project state
under `.innsigle/` and does **not** detect or modify framework-specific publish
trees (`static/`, `public/`, `docs/`, `_site/`, etc.).

## Layout (source of truth)

```text
.innsigle/
  config.json          # issuer id, key_id, key_url, op:// private key ref
  public/
    keys.json          # public issuer document
    claims/            # put *.attestation.json here when sealing pages
  provenance/          # transcript-derived L2 session data — stays local (gitignored)
  README.md
  AGENTS.md            # this file
```

Private keys are **never** in the repo. Credentials come from 1Password via
`config.json` → `onepassword.private_key_ref`.

## Required build step

Before or as part of deploy, copy the public staging tree to the **site root**
well-known path (adjust only the left side if your tool needs a different
source path — the **destination path is fixed**):

```bash
# Generic: after your site is rendered into SITE_ROOT
mkdir -p "$SITE_ROOT/.well-known/innsigle"
cp -a .innsigle/public/. "$SITE_ROOT/.well-known/innsigle/"
```

Examples (illustrative only — pick what this repo uses):

| Tool | Typical SITE_ROOT / hook |
|------|---------------------------|
| Quarto | Copy into `static/.well-known/innsigle/` so render includes it, **or** post-copy into `_site/.well-known/innsigle/` |
| Hugo | `static/.well-known/innsigle/` |
| plain static | project `public/` or deploy rsync source |
| GitHub Pages (Actions) | step after build: copy into artifact root |

**Do not** invent alternate URL paths. Signed claims use:

- `key_url`: `https://documentdrivendx.github.io/helix/.well-known/innsigle/keys.json`
- site path: `/.well-known/innsigle/keys.json`

If the public host differs, update `.innsigle/config.json` `issuer.key_url`
**before** signing new claims (old seals keep their frozen URL).

## Seal a content file

Finalize the **exact bytes** you will publish, then:

```bash
innsigle seal path/to/page.html
# optional: --kind model-primary|human-authored|mixed
# or commit a default colophon at .innsigle/colo.json

innsigle verify path/to/page.html
# finds attestation + keys under .innsigle/ (or public/.well-known/)
```

Colophons MAY carry the optional `human_input` measure (integer percent,
method hi1, declared from the operator's session journal — proposed
automatically by `innsigle seal <file> --auto`). NEVER edit its component
counts to reach a target percent: the CLI recomputes the headline from the
counts and refuses mismatches (exit 5). No journal evidence → omit the object
entirely. Shape reference: `innsigle colo example --kind model-primary --human-input`.

Issuer metadata and the private key ref come from `.innsigle/config.json` +
1Password. Attestation lands in `.innsigle/public/claims/` — include that tree
in the publish copy step.

## 1Password bridging (env)

- `INNSIGLE_OP_BIN` may contain arguments, e.g. `INNSIGLE_OP_BIN="mac op"`
  to bridge to the host CLI from a VM (OrbStack).
- `OP_ACCOUNT=<account>` (or `innsigle seal --op-account <account>`) selects
  the 1Password account; it is passed as `--account` to `op read`.

## Identity (this repo)

- issuer_id: `helix-wt-innsigle`
- key_id: `ed25519:d5a0b2d95482db5ff68fc8318a1ad4de`
- key_url: `https://documentdrivendx.github.io/helix/.well-known/innsigle/keys.json`

## Non-goals for agents

- Do not commit PEM private keys or `op` session tokens.
- Do not re-run `innsigle init` unless the operator asked (creates a new key).
- Do not rewrite Innsigle crypto or move keys outside `.innsigle/` + 1Password.
