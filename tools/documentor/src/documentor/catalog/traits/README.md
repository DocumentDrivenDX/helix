# Repository traits

A trait is something a repository is or has: a Databricks app, a tablespec pipeline, a Python
library. Each trait declares the signals that detect it and what it adds to the repository's
documentation: flows, pages (written, or generated from the repository's own structured sources),
views, the files a new instance of which should be documented, and what pages must never contain.

`skills/helix/scripts/publish_detect.py` scores every trait against a repository and proposes a
`publish:` block. The confirmed list is recorded in `.helix.yml` as `publish.traits`, so the
documentation never changes shape because a file appeared. When a repository has a significant
file that no trait claims (`significant.yml`), detection reports it: that is the cue to add a
trait. The format is `workflows/references/publishing.md`, Repository traits.
