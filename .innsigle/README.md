# Innsigle project state

This directory is owned by the Innsigle CLI. **Do not put private keys here.**

| Path | Purpose |
|------|---------|
| `config.json` | Issuer metadata, key fingerprint, 1Password ref (commit-safe) |
| `public/` | **Public** files to publish at site `/.well-known/innsigle/` |
| `public/keys.json` | Issuer document (public keys only) |
| `public/claims/` | Optional attestations after you sign content |
| `provenance/` | Transcript-derived session data (prompt counts, file paths) — **local only**, gitignored; publish only deliberately after review |
| `AGENTS.md` | Instructions for agents wiring this into a build |

## Custody

- **Private key:** 1Password only (see `config.json` → `onepassword.private_key_ref`)
- **Public key / fingerprint:** `config.json` and `public/keys.json`
- **key_id:** `ed25519:d5a0b2d95482db5ff68fc8318a1ad4de`
- **issuer_id:** `helix-wt-innsigle`
- **Published key_url (after deploy):** `https://documentdrivendx.github.io/helix/.well-known/innsigle/keys.json`

## Publish contract

Innsigle does **not** know Quarto, Hugo, Next, GitHub Pages, etc.

Your build (or an agent) MUST copy:

```text
.innsigle/public/  →  <site-root>/.well-known/innsigle/
```

so that `keys.json` is served at:

```text
https://<your-host>/.well-known/innsigle/keys.json
```

That URL must match `issuer.key_url` in `config.json` (frozen into signed claims).

See **AGENTS.md** for a checklist agents can follow.
