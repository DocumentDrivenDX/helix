# Agent instructions: Innsigle seals in this repository

Innsigle stores all project state under `.innsigle/` and does **not** detect
or modify framework-specific publish trees. Everything here is already wired;
this file says what not to break.

## Layout (source of truth)

```text
.innsigle/
  config.json          # issuer id, key ids + roles, content globs, op:// ref for the human key
  public/
    keys.json          # public issuer document (human + build keys, endorsement index)
    claims/            # human-key attestations for curated pages (committed)
    endorsements/      # human key's endorsement of the build key (committed)
  keys/                # local private PEMs (build key) — gitignored
  provenance/          # transcript-derived L2 session data — gitignored
  README.md
  AGENTS.md            # this file
```

Private keys are **never** in the repo. The human key lives in 1Password
(`config.json` → `onepassword.private_key_ref`); the build key is the
`INNSIGLE_BUILD_KEY` repository secret.

## Key policy (Innsigle ADR-004)

| Page | Frontmatter | Composition | Key | Who seals |
|------|-------------|-------------|-----|-----------|
| curated | no `generated: true` | `mixed` | human | the operator: `just innsigle-seal`, then commit `.innsigle/public/` |
| generated | `generated: true` (stamped by `scripts/generate-reference.py`, `publish-artifacts.py`, `publish-resources.py`) | `model-primary` | build | CI, at every website build; never committed |

Frontmatter decides, not path. `innsigle seal --all` (v0.5.0) applies the
policy from `content_globs` + `kind_from_frontmatter` in `config.json` and
skips a file whose key is absent instead of failing.

## Build wiring (already in place)

- `website/hugo.yaml` mounts `.innsigle/public` at `static/.well-known/innsigle`
  and `assets/innsigle`, and the content root at `assets/content-src`.
- `website/layouts/_partials/components/comments.html` renders the colophon
  only when the claim digest matches the current source bytes, and embeds the
  attestation as `application/innsigle+json`.
- `.github/workflows/website.yml` and `pages.yml` run
  `scripts/innsigle-seal.sh --role build` with the secret before Hugo.
- `tests/validate-innsigle.sh` is the gate (`just test-innsigle`).

**Do not** invent alternate URL paths. Signed claims use
`key_url` = `https://documentdrivendx.github.io/helix/.well-known/innsigle/keys.json`.

## Commands

```bash
scripts/innsigle-cli.sh <args>   # the pinned CLI; every script goes through it
just innsigle-seal               # seal --all: curated via 1Password, generated if INNSIGLE_BUILD_KEY is set
just innsigle-seal --role human  # curated only; fails without the human key
just innsigle-build-key          # one-time: mint the build key (then store the PEM as the GitHub secret)
just innsigle-endorse            # one-time (and after rotation): human key endorses the build key
just test-innsigle               # gate
```

Colophons MAY carry the optional `human_input` measure (method hi1). NEVER
edit its component counts to reach a target percent; the CLI recomputes the
headline and refuses mismatches (exit 5).

## 1Password bridging (env)

- `INNSIGLE_OP_BIN` may contain arguments, e.g. `INNSIGLE_OP_BIN="mac op"`
  to bridge to the host CLI from a VM (OrbStack).
- `OP_ACCOUNT=<account>` (or `--op-account <account>`) selects the
  1Password account; it is passed as `--account` to `op read`.

## Non-goals for agents

- Do not commit PEM private keys, `op` session tokens, or build-key claims.
- Do not re-run `innsigle init` or `just innsigle-build-key` unless the
  operator asked (each creates a new key).
- Do not let the build key endorse the human key, and do not seal curated
  pages with the build key.
- Do not rewrite Innsigle crypto or move keys outside `.innsigle/` + 1Password.
