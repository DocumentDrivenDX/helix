<!-- helix:publish audience=user page=index kind=tutorial voice=public-site budget=700 written=agent-opus reviewed=2026-10-20/agent-sonnet/019d97a8b1e40ed4 -->
<!-- helix:gap artifact:user-stories -->
<!-- helix:source README.md#install sha256:11003d4123be1f55 -->
<!-- helix:source README.md#use sha256:1668b6192a52a5d5 -->
<!-- helix:source src/documentor/cli.py sha256:4181ca3d7fc04669 -->
<!-- helix:source src/documentor/detect.py sha256:ff655eeda6b4701f -->
<!-- helix:source src/documentor/lib.py sha256:093a891d0f8bcf48 -->
# Getting started

documentor is a command-line tool. It works out what kind of project a repository is. It then generates, checks, and assembles that repository's documentation, which documentor calls its *guide*. In one session, you point documentor at your own repository and read the list of documentation pages it needs.

## Before you start

You need:

- Python 3.11 or later.
- [uv](https://docs.astral.sh/uv/), which installs and runs documentor.
- A repository to document, checked out on your machine. Use a scratch branch; documentor writes files into it.

The first session needs no Hugo, Go, or agent. Those come later, to build a site and write pages.

## Open it and sign in

documentor has no account and no sign-in. You install it once and run it from a terminal. Replace `<tag>` with the HELIX release that contains documentor (v0.19.0 or later).

```sh
uv tool install "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor"
```

To try it without installing:

```sh
uvx --from "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor" documentor --version
```

Check that it runs:

```sh
documentor --version          # after uv tool install; with uvx, run uvx --from "..." documentor --version
```

The output names the documentor version and the HELIX catalog version it carries. [HELIX](https://github.com/DocumentDrivenDX/helix) is the method that defines what a guide contains. documentor is the tool that builds one.

## Your first task: one worked session, step by step

In this task, documentor describes your repository and lists every page its readers need.

**1. Go to the repository.**

```sh
cd path/to/your-repository
```

Or pass `--root DIR` to any command.

**2. Ask documentor what the repository is.**

```sh
documentor init
```

The screen starts with `Traits detected in <name>:`. A *trait* is something the repository is, such as a plugin or a data app. Each trait adds pages to the guide.

Each trait line shows a confidence score and its evidence files. `PROPOSE` marks a trait that scored 0.5 or higher. Below that, `Proposed for .helix.yml:` shows the configuration block documentor suggests. Lines starting `Page added:` and `Page delegated:` show what each trait contributes.

The report ends by listing significant files that no proposed trait claims, or with `Every significant file is claimed.`

**3. Record the proposal.**

If the repository has no `.helix.yml` yet, `init` already wrote one in step 2. It also created the HELIX folders under `docs/helix/`. The screen confirms both.

If `.helix.yml` exists but has no `publish:` block, `init` prints `Add to .helix.yml (or rerun with --write):`. Record the proposal now:

```sh
documentor init --write
```

The screen ends with `wrote the proposal to <path>/.helix.yml`, naming the repository's folder. The `audiences` list in that block names who reads the guide: developer, operator, user, or data. If `.helix.yml` already records traits, `init` changes nothing and asks you to compare them with the proposal.

**4. List the guide.**

```sh
documentor status
```

The screen starts with `Guide for <name>: N pages`, then lists the pages under each audience. Each row gives the page's state, id, kind, and how it is produced. The last column says what the page needs next.

| Mark | Meaning |
|---|---|
| `ok` | The page is current. |
| `MISSING` | The page does not exist yet. |
| `STALE` | A source the page cites has changed since it was written. |
| `REVIEW` | A second reader has not yet evaluated the page. |
| `ADOPT` | A hand-written page needs a header to join the guide. |
| `->` | Another tool already publishes the page; the guide links it. |
| `EMPTY` | The repository has nothing to generate the page from. |

On a new guide, most rows read `MISSING`. The list ends with `For the agent`, an ordered list of the pages that still need writing.

If the screen reads `No guide yet: run documentor init first.`, `.helix.yml` has no audiences yet. Go back to step 3.

**5. Generate what can be generated.**

```sh
documentor build --no-site
```

The command regenerates every page whose facts come from a structured source, and prints `regenerated <path>` for each. It then shows the same page list, followed by a count of blocking findings and warnings. `--no-site` skips building the website.

## What you have done

You installed documentor, let it detect your repository's traits, and recorded its proposal in `.helix.yml`. You then read every page your readers need, with each page's state.

The generated pages are now files in a folder named `guide` beside the HELIX root. With the default HELIX root `docs/helix/`, that folder is `docs/guide/`. Add an `out` key under `publish:` in `.helix.yml` to move the folder.

## Where to go next

- [Using the product](using.md): write the remaining pages, build the site, and gate pull requests with `documentor check`.
- [What it is and is not](about.md): what documentor does for a repository, and what it leaves to you.
- [Command line](../developer/cli.md): every command and option.
