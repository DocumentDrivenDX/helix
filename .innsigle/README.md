# Innsigle project state

This directory is owned by the Innsigle CLI (pinned to v0.5.0 by
`scripts/innsigle-cli.sh`). **Do not put private keys here.**

| Path | Purpose |
|------|---------|
| `config.json` | Issuer metadata, key ids and roles, content globs, 1Password ref (commit-safe, committed) |
| `public/` | **Public** files published at site `/.well-known/innsigle/` |
| `public/keys.json` | Issuer document: both public keys, their roles, and the human → build endorsement |
| `public/claims/` | Attestations for **curated** pages, signed by the human key (committed) |
| `public/endorsements/` | The human key's endorsement of the build key (committed) |
| `keys/` | Local private PEMs (the build key after `just innsigle-build-key`) — **gitignored** |
| `provenance/` | Transcript-derived session data — **local only**, gitignored |
| `AGENTS.md` | Instructions for agents wiring this into a build |

## Two keys, one issuer (Innsigle ADR-004)

| Role | Custody | Seals | Claims live |
|------|---------|-------|-------------|
| **human** | 1Password only (`config.json` → `onepassword.private_key_ref`); never in CI | curated pages (no `generated: true`) as `mixed` | committed under `public/claims/` |
| **build** | GitHub secret `INNSIGLE_BUILD_KEY` (PEM from `just innsigle-build-key`, local copy under `keys/build/`) | generated pages (`generated: true`) as `model-primary` | minted by CI at every build, never committed |

The human key endorses the build key (`just innsigle-endorse`); the build key
never endorses anything. Rendered HTML quotes the source attestation — the
signature covers the markdown source, not the HTML bytes.

- **issuer_id:** `helix`
- **human key_id:** `ed25519:d5a0b2d95482db5ff68fc8318a1ad4de`
- **build key_id:** see `keys.build.key_id` in `config.json`
- **Published key_url:** `https://documentdrivendx.github.io/helix/.well-known/innsigle/keys.json`

## Everyday

```bash
just innsigle-seal            # curated pages with the human key (op signed in); commit .innsigle/public/
just test-innsigle            # gate: verifies every claim and the rendered seals
```

CI seals generated pages with the build key before building the site and
runs the same gate with every page required.

## Publish contract

Hugo mounts `.innsigle/public` at `static/.well-known/innsigle` (see
`website/hugo.yaml`), so `keys.json` is served at the `key_url` above. That
URL is frozen into signed claims; change it in `config.json` **before** signing.

See **AGENTS.md** for the checklist agents follow.
