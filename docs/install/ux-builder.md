# UX Builder companion plugin

UX Builder is a separate plugin in the HELIX marketplace. It provides three
skills for designing an experience, building with the selected SDK, and assessing
journeys. HELIX continues to own governing artifacts and its artifact-type
catalogue. Installing the companion does not adopt a UI library for your project.

## Install

For Claude Code:

```sh
claude plugin marketplace add https://github.com/DocumentDrivenDX/helix
claude plugin install ux-builder@helix
```

For Codex, add `DocumentDrivenDX/helix` as a plugin marketplace and select
UX Builder. The shared `.claude-plugin/marketplace.json` is also supported by
Codex; HELIX keeps one catalogue so the listings cannot drift between hosts.

The plugin requires Node.js 20+ and a local executor. It supplies instructions,
references and a setup checker; npm dependencies are installed in the consumer
project with its own package manager and lockfile. It starts no MCP server and
runs no install hooks. MCP can be configured separately if wanted.

## Start or adopt

Ask the design skill to start or resume the app's UX work. It runs the packaged
setup checker from your project root, reports missing dependencies and installed
versions, and reads guidance for that installed SDK. Run any required installation
within the project's authorized SDK-adoption scope. Assessment also requires the
audit package's documented browser prerequisites; optional video needs ffmpeg.

Record SDK adoption through `packaged-design-system`, naming the actual installed
component/token packages and versions. Resolve competing component owners using
project decisions; plugin installation does not override a Radix/AppKit choice.
UX work lives in `docs/ux-builder/` and `.ux-builder/`; changes to HELIX documents
use the existing UX Builder proposal and approval workflow.

Projects created by the starter use local npm-versioned skills by default. Prefer
those local skills when present. To use the plugin instead, select plugin mode
using `UX_BUILDER_SKILLS=plugin` during creation/initialization, or the durable
`.ux-builder/skills.json` selector in an existing project. Review generated local
skill copies before removal and preserve custom instructions. See the pinned
plugin's README for the selector and exact runner commands.

## Maintaining the listing

UX Builder owns its plugin manifests, source skills, packaging tests and releases.
The listing uses a Git subdirectory source with a full tested commit SHA and its
own plugin version. It does not track HELIX's version or npm package versions.
For an update:

1. Merge and release the upstream UX Builder plugin change and confirm CI.
2. Change this marketplace entry's SHA and plugin version together.
3. Inspect both plugin manifests and the three skill directories at that commit.
4. Run `just test-install-consistency`, `just test`, and `git diff --check`.
5. Smoke-test installation through this marketplace in isolated host settings,
   then exercise setup and one relevant workflow in a consumer project.

Keep the initial listing PR draft until the upstream change is merged/released
and real-source installation is verified. A pin to a PR commit is review evidence,
not a claim that the plugin has been released. Roll back by restoring the prior
listing pin; uninstalling the plugin does not delete UX documents or design state.
