<!-- helix:publish audience=developer page=walkthrough kind=explanation voice=onboarding budget=1100 written=codex reviewed=2026-10-29/codex-astra-independent-reader/4a8250a81fa82e57 -->
<!-- helix:gap artifact:architecture -->
<!-- helix:source src/documentor/cli.py sha256:8b7a0be0b2efb9cb -->
<!-- helix:source src/documentor/check.py sha256:784c2473233c0346 -->
<!-- helix:source src/documentor/lib.py sha256:5db149c5af59118b -->
<!-- helix:source src/documentor/generate.py sha256:9ed3906b7fe2bc36 -->
<!-- helix:source src/documentor/report.py sha256:0f48cfca412184a2 -->
<!-- helix:source src/documentor/write.py sha256:208f5a662b7501e4 -->
<!-- helix:source src/documentor/catalog/ci/github-actions.yml sha256:9f8ec1f2b471f001 -->
<!-- helix:source tests/validate-guide.sh sha256:5c416438f8ca7e20 -->
<!-- helix:source tests/validate-publish.sh sha256:fbe3dede8c6f4a24 -->
<!-- helix:source tests/validate-publish-traits.sh sha256:6f8a932174fe2332 -->
<!-- helix:source tests/validate-write.sh sha256:e7fa04c7257f761e -->
<!-- helix:source tests/python/test_report.py sha256:8952e75926f6350b -->
<!-- helix:source tests/python/test_generators_ops.py sha256:7b51edcbc2916d4e -->
<!-- helix:source justfile sha256:33d64f77836eb9e1 -->
<!-- helix:source src/documentor/schemas.py sha256:6db23e6c01b889bc -->
<!-- helix:source src/documentor/site.py sha256:1d8a815021485d27 -->
<!-- helix:source tests/python/test_schemas.py sha256:fed68ae9a073185b -->
# Request walkthrough

## Scenario

The critical request is `documentor check --root .`, which runs on every pull request. It decides whether the pull request leaves the guide behind the repository. The CI template in `src/documentor/catalog/ci/github-actions.yml` runs it:

```sh
uvx --from "$DOCUMENTOR" documentor check --root .
```

Take one pull request that edits a file a written page cites as a source. The check must fail, name the page as stale, and need no agent or network.

These steps follow code and tests; no architecture artifact governs them. [Architecture](architecture.md) describes the parts.

## Sequence

The request reads the configuration, confirms its schema, and plans the pages. It then gives each page a state, checks the architecture views and every page file, and turns the result into an exit code. A `check` writes nothing to disk.

```mermaid
sequenceDiagram
  participant CI as CI job
  participant CLI as cli.main / guide_main
  participant Lib as lib.plan
  participant Assess as cli.assess
  participant Check as check.run_check
  participant Views as cli.views
  CI->>CLI: documentor check --root .
  CLI->>Lib: config_of(root), publish.schema == SCHEMA, audiences, plan(config, root)
  Lib-->>CLI: list of PagePlan
  CLI->>Assess: state of each page
  Assess->>Check: parse_page, check_generated or check_sources
  CLI->>Views: views(root, config, write=False)
  CLI->>CLI: report(root, pages, view_state), with gap_lines
  CLI->>Check: run_check([out], root, False)
  Check-->>CLI: Findings (blocking, warnings)
  CLI-->>CI: exit 0 or 1
```

## Steps and evidence

Tests use fixture repositories.

1. **Dispatch.** `main` in `src/documentor/cli.py` first takes `--catalog DIR`, which sets the HELIX catalog the run reads. It sends tool names such as `check-pages` to their modules. Everything else, `check` included, goes to `guide_main`.
2. **Configuration and plan.** `config_of` reads `.helix.yml`, and `guide_main` refuses a `publish.schema` other than `SCHEMA` in `src/documentor/lib.py`. `plan` then builds one `PagePlan` per page from the audiences, the traits, and the project's own pages. It applies `delegate`, `existing`, and `skip`, selecting operational data pages when configured.
3. **Page state.** `assess` gives each page one state: delegated, empty, missing, unadopted, stale, unreviewed, or current. It regenerates a generated page in memory and compares the result. For a written page, it compares the source digests, then checks the `reviewed=` stamp against the digest of the body.
4. **Gaps.** `assess` adds a page's `helix:gap` lines to its detail as "written without" the missing artifact. The gap does not change the page's state. `report` then calls `gap_lines` in `src/documentor/report.py`, which lists the artifacts that would improve the guide, the one behind the most pages first.
5. **Source digests.** `check_sources` reads each `helix:source` line. It cuts a `path#anchor` source to that heading's section, so edits elsewhere in the file do not stale the page.
6. **Architecture views.** `views` checks the architecture views against the model without rewriting them. With no model, the state is `none`.
7. **Page checks.** `run_check` in `src/documentor/check.py` walks every page under the output directory. It checks sources, kinds, links, backticked paths, cited tests, handling patterns, scope, prose, and unmapped watched files.
8. **Verdict.** `guide_main` prints the report and the counts of blocking findings and warnings. It returns 1 when there is a blocking finding, an unfinished page, or stale views.

The states that `check` reports feed `documentor write` in `src/documentor/write.py`. A missing or stale page goes to the writer. An unreviewed page goes to the evaluator, or back to the writer when its page checks have findings. `reviewer_prompt` gives the evaluator absolute paths to the repository and the page.

| Step | Test | What it asserts |
|---|---|---|
| Plan | `tests/validate-guide.sh` | `build` lists the missing tutorial; a skipped audience page is not planned |
| Schema | `tests/validate-guide.sh` | A `schema: 2` block is refused with "reads schema 1" |
| Page state | `tests/validate-guide.sh` | An unevaluated page shows `REVIEW`; a changed source shows `STALE` and fails `check` |
| Gaps | `tests/validate-write.sh` | `status` reports a page written without the architecture artifact |
| Gap order | `tests/python/test_report.py` | The artifact that would improve most pages comes first; no gaps, no lines |
| Generated pages | `tests/validate-publish-traits.sh` | A new manifest makes the generated page stale and names the regenerate command |
| Source digests | `tests/validate-publish.sh` | An uncited section's change passes; a cited H2 or H3 change blocks |
| Review stamp | `tests/validate-write.sh` | The writer cannot review its own page |
| Evaluation | `tests/validate-write.sh` | The reviewer model evaluates the page the evaluator prompt names |
| Revision | `tests/validate-write.sh` | An unreviewed page with prose findings goes to the writer; a stale page is revised with the moved sources |
| Page checks | `tests/validate-publish.sh` | Broken links, missing paths, handling patterns, and writes outside scope block |
| Verdict | `tests/validate-guide.sh` | A complete, evaluated guide passes `check` |

Run the end-to-end tests:

```sh
uv run just test-guide
# OK: documentor takes a repository from no guide to a checked, evaluated guide and its site, and catches it going stale
uv run just test-publish
# OK: documentor check-pages stamps, pins staleness to sections, blocks broken links, paths and sources, ...
```

<details>
<summary>The assertions behind the scenario</summary>

From `tests/validate-guide.sh`, after the pages are written, stamped, and reviewed:

```sh
$rg check --root "$p" >"$tmpdir/out" 2>&1 || fail "a complete, evaluated guide should pass: $(cat "$tmpdir/out")"

# A changed source makes the written page stale, and a new plug-in the generated one.
printf '# Vision\n\n## Mission\n\nReview and pay claims.\n' >"$p/docs/helix/01-frame/vision.md"
$rg check --root "$p" >"$tmpdir/out" 2>&1 && fail "a changed source should fail the check"
grep -Eq "STALE +about" "$tmpdir/out" || fail "expected the written page stale: $(cat "$tmpdir/out")"
```

From `tests/validate-guide.sh`, a block for another contract version is refused:

```sh
$rg status --root "$p" >"$tmpdir/out" 2>&1 && fail "a schema documentor does not read should be refused"
grep -q "reads schema 1" "$tmpdir/out" || fail "expected the schema refusal: $(cat "$tmpdir/out")"
```

From `tests/validate-write.sh`, the fake evaluator turns the absolute page path back into a relative one before it logs the call:

```sh
grep -q "^sonnet evaluate docs/guide/developer/index.md$" "$FAKE_LOG" || fail "the evaluator should be the reviewer model"
```

From `tests/validate-write.sh`, an unreviewed page with a five-sentence paragraph goes back to the writer:

```sh
printf '\nOne. Two. Three. Four. Five.\n' >>"$project/docs/guide/developer/developer-guide.md"
: >"$FAKE_LOG"
"$rg" write --root "$project" --agent "$agent" >/dev/null 2>&1 || fail "a page blocked by its checks should be revised"
grep -q "^opus write docs/guide/developer/developer-guide.md$" "$FAKE_LOG" || fail "a page with prose findings should go to the writer"
```

</details>

## Schema publication boundary

Schema publication is separate from the guide gate: use `documentor schemas --check` for freshness. Hugo, static, and Hextra assembly publishes schemas; plain Hugo needs `documentor schemas` first. Tests in `tests/python/test_schemas.py` cover references, retained sources, freshness, and site integration.

## Failure paths

Every failure ends in exit 1 with a line naming the page and the next action, except usage errors, which exit 2.

| Condition | Where it is caught | What the reader sees |
|---|---|---|
| `--catalog` without a directory | `main` | `documentor: --catalog needs a directory ...`, exit 2 |
| `publish.schema` is not the one this release reads | `guide_main` | `... this documentor reads schema 1 ...`, exit 2 |
| No audiences in `.helix.yml` | `guide_main` | ``No guide yet: run `documentor init` first.``, exit 2 |
| An unknown trait id | `load_traits`, via `plan` | `documentor: unknown trait(s) ...`, exit 2 |
| A planned page has no file | `assess` | `MISSING`, with "write it (`documentor write`, or HELIX guide mode)" or "run `documentor build`" |
| A cited source changed | `check_sources` | `STALE`, naming the source that changed |
| A cited source was deleted | `check_sources` | Blocking `missing-source` |
| The body changed after review | `assess` | `REVIEW`: "changed after its evaluation; evaluate it again" |
| A generated page differs from regeneration | `check_generated` | Blocking `stale`: "its sources changed" |
| A broken link or backticked path | `check_links` | Blocking `broken-link` or `missing-path` |
| A cited test the file does not define | `check_tests` | Blocking `missing-test` |
| Text matches a `handling` pattern | `check_handling` | Blocking `handling`, also for drawings beside the pages |
| Views drifted from the model | `views` | `architecture views: stale`, with the problems |

Prose breaches are warnings during `check`, because `guide_main` calls `run_check` without strict prose. Only `documentor check-pages --strict-prose` makes them blocking. `documentor write` still sends them back to the writer before the evaluator sees the page.

## Where to change what

Most changes touch one function and one test; extend the matching test before you change the code.

| To change | Edit | Prove it in |
|---|---|---|
| Which pages a repository gets | `plan` in `src/documentor/lib.py`, or a trait in `src/documentor/catalog/traits/` | `tests/validate-guide.sh` |
| The configuration schema version | `SCHEMA` in `src/documentor/lib.py` | `tests/validate-guide.sh` |
| A page state or its message | `assess` in `src/documentor/cli.py` | `tests/validate-guide.sh` |
| How gaps are grouped in the report | `gaps` and `gap_lines` in `src/documentor/report.py` | `tests/python/test_report.py` |
| A new check on page files | `run_check` and its helpers in `src/documentor/check.py` | `tests/validate-publish.sh` |
| How a generated page is built | A `@generator` function in `src/documentor/generate.py` | `tests/validate-publish-generators.sh` |
| A CI, task, schema, or compose generator | `ci_pipelines`, `tasks`, `database_schema`, or `compose_services` in `src/documentor/generate.py` | `tests/python/test_generators_ops.py` |
| Which pages go to the writer or the evaluator | `run` and `write_page` in `src/documentor/write.py` | `tests/validate-write.sh` |
| What the evaluator is told to read | `reviewer_prompt` in `src/documentor/write.py` | `tests/validate-write.sh` |
| When `check` fails | The end of `guide_main` in `src/documentor/cli.py` | `tests/validate-guide.sh` |
| The CI job projects copy | `src/documentor/catalog/ci/github-actions.yml` | No test runs it |
| Voice limits and banned phrases | Synced from HELIX with `just sync-helix`, not edited in `src/documentor/catalog/helix/` | `just test-catalog` |

The Python unit tests run on their own:

```sh
uv run just test-python
```

Run the whole suite before you open a pull request:

```sh
uv run just test
```

The [Developer guide](developer-guide.md) covers setup, and [Command line](cli.md) lists every command and option.
