<!-- helix:publish audience=data page=cli kind=reference voice=onboarding generated=cli-commands -->
<!-- helix:source pyproject.toml sha256:74a08b4781a32616 -->
<!-- helix:source src/documentor/cli.py sha256:0707cd738e9b6418 -->
# Cli

Every command line the project installs: 1 in all, from `[project.scripts]` in its pyproject files, with each command's purpose from its docstring. Options and arguments are on each command's `--help`.

## documentor

`documentor` is `documentor.cli:main` (pyproject.toml); 8 commands.

| Command | What it does |
|---|---|
| `documentor init` | detect what the repository is; propose (or write) the guide |
| `documentor status` | every page of the guide, and what each needs next |
| `documentor build` | regenerate what is generated, check everything, build the site; |
| `documentor write` | write the missing and stale pages with an agent, and evaluate |
| `documentor check` | the CI gate: regenerate in memory, fail on anything behind |
| `documentor review` | Record an evaluation, only of a page that passes every check, never by the page's writer; it
lapses when the page changes. |
| `documentor adopt` | Give a hand-written page the header that brings it under the guide; its text is untouched. |
| `documentor prompt` | the brief a writer (or an evaluator) of a written page gets |
