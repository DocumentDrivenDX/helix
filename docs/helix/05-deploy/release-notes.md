---
ddx:
  id: release-notes
  authoring:
    home: repo
  depends_on:
    - deployment-checklist
  review:
    self_hash: 99574883788300395089b39ca0b1918d4a23f359269390fa4717bc0fc0c41f51
    deps:
      deployment-checklist: 78c9688645de24f33182dca537e13d0fb180abb4773ab85b48468e495a92bad1
    reviewed_at: "2026-09-17T19:23:17Z"
---

# Release Notes — HELIX v0.13.1

## Release Scope

- Release identifier or version: `v0.13.1`
- Release date: 2026-09-17 (operator-driven; tagged at the merge commit)
- Rollout window or environment: the public website at
  `https://documentdrivendx.github.io/helix/` and its build pipeline; the
  plugin packages carry only the version bump
- Release owner: HELIX maintainer cutting the tag
- Source commit or build: the tag's merge commit (tag `v0.13.1`); previous release
  `v0.13.0` at `91eb74d2` (2026-09-15)

## Audience and Channels

| Audience | Why they care | Delivery channel |
|----------|---------------|------------------|
| Website readers | Every page carries an Innsigle seal that says who signed the page's source and whether a model drafted it | GitHub Pages rebuild |
| HELIX maintainers | Curated pages are sealed with the house key before merge; generated pages are sealed by CI with a second key | This file and `.innsigle/README.md` |
| HELIX plugin users | No change beyond the version number | Plugin repo tag; marketplace update |

## Highlights

- **Content seals on every page.** Each website page quotes an Innsigle
  attestation for its markdown source: the source digest, the declared
  composition (`mixed` for curated prose, `model-primary` for generator
  output), the signing key and its role, and the signature. A page whose
  source changed after sealing renders no seal and fails the build instead
  of showing a seal that would not verify.
- **Two keys, one issuer (Innsigle ADR-004).** The house key stays in
  1Password and seals curated pages, whose claims are committed. A build key
  held as a repository secret seals the generated pages at every site build.
  The house key endorses the build key, so a verifier who pins the house key
  recognizes CI seals, and the build key can never mint a curated seal.
- **Seal gate.** `tests/validate-innsigle.sh` verifies every claim with the
  pinned Innsigle CLI, enforces the key policy, and checks the built site
  serves the issuer document, the endorsement, and a seal on every page.

## Required Actions Summary

- Plugin users: none.
- Maintainers: after editing a page under `docs/website/content/` that is
  not generated, run `just innsigle-seal` (1Password CLI signed in) and
  commit `.innsigle/public/claims/`; the website workflow fails until the
  claim matches the source. Generated pages need nothing.
- Maintainers: the build key is the `INNSIGLE_BUILD_KEY` repository secret;
  `just innsigle-build-key --rotate` followed by `just innsigle-endorse`
  rotates it.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Site | The colophon partial renders a seal from the committed or CI-minted claim, embeds the attestation as `application/innsigle+json`, and states that the signature covers the markdown source, not the HTML; `.innsigle/public/` is served at `/.well-known/innsigle/` | Website readers |
| Scripts | `scripts/innsigle-cli.sh` pins Innsigle v0.5.0 for every caller; `scripts/innsigle-seal.sh` wraps `innsigle seal --all`; `scripts/innsigle-build-key.sh` mints or rotates the build key | Maintainers |
| Config | `.innsigle/config.json` is committed with the content globs, frontmatter-driven composition, and key roles; the issuer document lists both keys and the endorsement | Maintainers and verifiers |
| CI | The website and Pages workflows seal generated pages with the build key before Hugo runs; the gate runs with every page required | Maintainers |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| The first build key's private half was committed to the pull request branch | The key is marked revoked in the issuer document and a replacement was minted, stored as the secret, and endorsed; the ignore rule now covers `.innsigle/keys/` | Seals from the revoked key never verify; the live site carries only replacement-key seals |
| The claude-code recipe page was edited after sealing | Resealed with the house key | The page renders its seal again |

## Breaking Changes and Required Actions

- None. The plugin packages differ from `v0.13.0` only in the version field.

## Migration or Rollback Guidance

- Migration: pull the tag; nothing to regenerate for plugin consumers.
- Rollback: install the `v0.13.0` tag. The website keeps its seals because
  they are produced at build time from `main`.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| One-pager, brief, and HTML render targets are not built | Teams wanting a document rather than a deck | Backlog item with the precise gap; write the brief as a deck script for now |
| The eval's investor-deck brief fails the shape gate on a reversal the skill wrote, and the survey brief needs an 1,800-second budget | Maintainers reading the eval | Recorded in `evals/results/`; the mode text names the coverage vocabulary and the shape rules |
| Claim subject URIs for section index pages follow the source path shape (`…/_index/`) rather than the published URL | Verifiers reading the URI field | Informational only; the digest and the `Signed source` line identify the page; reported upstream |
| Georgia and Trebuchet are absent on stock Linux LibreOffice, so the raster substitutes them there | Hosts rasterizing decks on Linux | `deck-qa.py` notes the missing typeface; use the `technical` or `classic` look |

Support: open an issue at `https://github.com/DocumentDrivenDX/helix`.

## References

- Deployment checklist: [`deployment-checklist.md`](deployment-checklist.md)
- Seal operations: `.innsigle/README.md`, `.innsigle/AGENTS.md`
- Innsigle decision record: ADR-004 in `DocumentDrivenDX/innsigle` (v0.5.0)
- Commit range: `git log v0.13.0..v0.13.1`
