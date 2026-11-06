"""Write and evaluate the guide's written pages with a headless agent (ADR-003).

`documentor write` works the `status` list: each written page that is missing or stale is written
by one agent call, held to the checks `check-pages` runs, and evaluated by a second call on a
different model; a pass is stamped through `review`. A current page is never touched, and a page
left unreviewed is only evaluated.

The agent is a command: the prompt goes on standard input, the answer comes on standard output,
and `{model}` in the command is replaced by the model. The default is Claude Code headless with
read tools only; `publish.agent.command` in `.helix.yml` or `DOCUMENTOR_AGENT` names another. The
writer's answer is the page without its header: `helix:gap` lines for HELIX artifacts the page had
to do without, `helix:source` lines for what it was written from, then the Markdown. documentor
writes the header and stamps the sources.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

from documentor import check
from documentor.lib import GAP, HEADER, SOURCE, PagePlan, catalog, helix_catalog, helix_root, load_audience, load_yaml, publish_out

COMMAND = "claude -p --model {model} --allowedTools Read,Glob,Grep --output-format text"
WRITER, REVIEWER = "opus", "sonnet"
TIMEOUT = 900  # seconds for one agent call
VERDICT = re.compile(r"^\W*VERDICT:\W*(pass|fail)\b", re.I | re.M)


class AgentError(Exception):
    pass


def settings(config: dict, command: str = "", writer: str = "", reviewer: str = "") -> tuple[str, str, str]:
    """The agent command and the two models: the flags, else `publish.agent`, else the defaults."""
    agent = (config.get("publish") or {}).get("agent") or {}
    return (command or os.environ.get("DOCUMENTOR_AGENT") or agent.get("command") or COMMAND,
            writer or agent.get("writer") or WRITER, reviewer or agent.get("reviewer") or REVIEWER)


def call(command: str, model: str, prompt: str, root: Path) -> str:
    """One agent call from the root: the prompt on stdin, the answer from stdout."""
    argv = shlex.split(command.replace("{model}", model))
    try:
        done = subprocess.run(argv, input=prompt, capture_output=True, text=True, cwd=root, timeout=TIMEOUT)
    except FileNotFoundError:
        raise AgentError(f"agent command not found: {argv[0]} (set publish.agent.command or DOCUMENTOR_AGENT)")
    except subprocess.TimeoutExpired:
        raise AgentError(f"agent call timed out after {TIMEOUT}s")
    if done.returncode != 0:
        raise AgentError(f"agent exited {done.returncode}: {(done.stderr or done.stdout).strip()[:400]}")
    return done.stdout


# --- prompts --------------------------------------------------------------------------------------

def voice_of(page: PagePlan) -> str:
    return page.entry.get("voice") or load_audience(page.audience).get("voice") or "onboarding"


def _voice_rules(profile: str) -> list[str]:
    voice = load_yaml(helix_catalog() / "voice.yml") or {}
    entry = (voice.get("profiles") or {}).get(profile) or {}
    limits = entry.get("limits") or {}
    lines = [f"- Sentences of at most {limits.get('sentence_words')} words; paragraphs and list items of at most "
             f"{limits.get('paragraph_sentences')} sentences; table cells of at most {limits.get('cell_words')} words."]
    lines += [f"- {move}" for move in entry.get("required_moves") or []]
    lines += [f"- Avoid {item}." for item in entry.get("avoid") or []]
    prose = voice.get("prose") or {}
    phrases = {k: v for group in ("avoid_phrases", "information_only", "pronouns") for k, v in (prose.get(group) or {}).items()}
    lines.append("- Never use these words or phrases (the fix follows each): "
                 + "; ".join(f'"{k}" → {v}' for k, v in phrases.items()) + ".")
    return lines


def _hints(page: PagePlan) -> list[str]:
    lines = []
    for hint in page.entry.get("sources") or []:
        if isinstance(hint, str):
            lines.append(f"- {hint}")
            continue
        kind, what = next(iter(hint.items()))
        extra = [f"sections: {', '.join(hint['sections'])}"] if hint.get("sections") else []
        extra += [hint["note"]] if hint.get("note") else []
        lines.append(f"- {kind}: {what}" + (f" ({'; '.join(extra)})" if extra else ""))
    return lines


def _writing_pass() -> list[str]:
    """The writing pass's "Information only" and "What the pass keeps" rules and its rewrite step,
    from HELIX's writing-pass.md, so an agent writes to the same standard a person follows."""
    import re

    path = helix_catalog() / "references" / "writing-pass.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    wanted = []
    for heading in ("Information only", "What the pass keeps"):
        match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if match:
            wanted += ["", f"## {heading} (the writing pass)", match.group(1).strip()]
    rewrite = re.search(r"^5\. \*\*Rewrite what is left\.\*\*\n(.*?)(?=^6\. )", text, re.M | re.S)
    if rewrite:
        wanted += ["", "## Rewriting (the writing pass)", rewrite.group(1).strip()]
    return wanted


def writer_prompt(page: PagePlan, pages: list[PagePlan], config: dict, root: Path,
                  previous: str = "", feedback: list[str] | None = None) -> str:
    entry = page.entry
    here = (root / page.path).parent
    others = [f"- {os.path.relpath(root / p.path, here)}: {p.title} ({p.audience}, {p.kind or 'page'})"
              for p in pages if p is not page and p.work != "delegated"]
    handling = config.get("handling") or {}
    lines = [
        f"You are writing one page of the documentation for the repository in the current directory.",
        f"Read the repository with your tools before you write. Answer with the page only; do not write files.",
        "",
        "## The page",
        f"- Path: {page.path}",
        f"- Title: {page.title}",
        f"- Reader: the {page.audience} audience. {load_audience(page.audience).get('reader', '')}".rstrip(),
        f"- Kind (Diátaxis): {page.kind}",
        f"- The reader's task: {page.task}",
    ]
    if entry.get("outline"):
        lines.append(f"- Sections, as H2 headings in this order: {', '.join(entry['outline'])}")
    if entry.get("budget"):
        lines.append(f"- Budget: at most {entry['budget']} words of prose (code, headings, and tables of commands are not counted).")
    lines += ["", "## Where to look (hints, not paths)"] + (_hints(page) or ["- the code"])
    lines += [f"HELIX artifacts (vision, PRD, architecture, ADRs) live under {helix_root(config)}/."
              " When an applicable hint names a missing artifact, write from available evidence and record the gap. "
              "Omit inapplicable hints without a gap; operational databases need data-design, not an analytics data-architecture."]
    lines += ["", "## Voice"] + _voice_rules(voice_of(page))
    lines += _writing_pass()
    lines += ["", "## Rules the page is checked against",
              "- Every fact comes from a file you read. Do not invent commands, options, files, or behaviour.",
              "- A path in backticks that contains a slash must exist, relative to the repository root.",
              "- A relative Markdown link resolves from the page's own directory. The other pages of the guide, by link:"]
    lines += [f"  {o}" for o in others] or ["  (none)"]
    if handling:
        lines.append(f"- Never publish: {', '.join(handling.get('never_publish') or [])}; nothing matching "
                     f"{', '.join(handling.get('patterns') or [])}.")
    lines.append("- Cite as sources the files whose content the page states, not every file you opened."
                 " A busy file makes the page go stale on every edit; prefer the file or the `path#section` that holds the fact.")
    lines += ["", "## Answer format",
              "Exactly this, and nothing before or after it:",
              "<!-- helix:gap artifact:<name> -->            (one per missing HELIX artifact a hint names; none if none)",
              "<!-- helix:source <path or path#heading-anchor> -->  (one per source, at least one)",
              f"# {page.title}",
              "<the page in Markdown>"]
    if previous:
        lines += ["", "## The current page", "Revise it. Change what the feedback or the moved sources require, and keep the rest.",
                  "", "<<<PAGE", previous.strip(), "PAGE>>>"]
    if feedback:
        lines += ["", "## Feedback to resolve"] + [f"- {f}" for f in feedback]
    return "\n".join(lines) + "\n"


def reviewer_prompt(page: PagePlan, root: Path) -> str:
    entry = page.entry
    return "\n".join([
        "You are evaluating one page of a repository's documentation, written by someone else.",
        f"The repository is {root.resolve()}, the current directory; its paths below are relative to it.",
        f"Read the page at {(root / page.path).resolve()}, the sources its `helix:source` lines name, and whatever else in the repository you need.",
        "",
        f"- Reader: the {page.audience} audience",
        f"- Kind (Diátaxis): {page.kind}",
        f"- The reader's task: {page.task}",
        f"- Sections expected: {', '.join(entry.get('outline') or []) or 'any'}",
        "",
        "Fail the page for any of these: a claim the repository contradicts or does not support; a command, option,"
        " or file that does not exist; a reader who follows the page could not do the task; a section of the"
        " outline missing; content of the wrong kind (a tutorial that only explains, a reference that narrates).",
        "Do not fail it for style alone.",
        "",
        "Answer with one line `VERDICT: pass` or `VERDICT: fail`, then each problem on its own line starting"
        " with `- `, naming the section and what the repository says instead.",
    ]) + "\n"


# --- answers --------------------------------------------------------------------------------------

def parse_answer(text: str) -> tuple[list[str], list[str], str]:
    """The writer's gaps, sources, and body; text around the page (a fence, a preamble) is dropped."""
    text = re.sub(r"^\s*```(?:markdown|md)?\s*\n(.*)\n```\s*$", r"\1", text.strip(), flags=re.S)
    start = re.search(r"^(<!-- helix:|# )", text, re.M)
    text = text[start.start():] if start else text
    gaps = GAP.findall(text)
    sources = [m.group(1) for m in SOURCE.finditer(text)]
    body = HEADER.sub("", SOURCE.sub("", GAP.sub("", text))).strip()
    return gaps, sources, body


def render(page: PagePlan, model: str, gaps: list[str], sources: list[str], body: str) -> str:
    fields = [f"audience={page.audience}", f"page={page.id}", f"kind={page.kind or '-'}", f"voice={voice_of(page)}"]
    fields += [f"budget={page.entry['budget']}"] if page.entry.get("budget") else []
    fields.append(f"written=agent-{model}")
    lines = [f"<!-- helix:publish {' '.join(fields)} -->"]
    lines += [f"<!-- helix:gap {g} -->" for g in dict.fromkeys(gaps)]
    lines += [f"<!-- helix:source {s} -->" for s in dict.fromkeys(sources)]
    return "\n".join(lines) + "\n" + body + "\n"


def findings_for(path: Path, root: Path, planned: set[str]) -> list[str]:
    """The page's own blocking and prose findings, as the writer should read them. A link to a page
    of the guide not yet written is not one: the pages are all written before any is evaluated."""
    found = check.run_check([path], root, False)
    ahead = {os.path.relpath(root / p, path.parent) for p in planned}
    return [f"{f['check']}" + (f" (line {f['line']})" if f["line"] else "") + f": {f['message']}"
            for f in found.items if f["page"] == str(path)
            and (f["severity"] == "blocking" or f["check"].startswith("prose."))
            and not (f["check"] == "broken-link" and f["message"].split("#")[0].split(" ")[0] in ahead)]


# --- the work -----------------------------------------------------------------------------------

def write_page(page: PagePlan, pages: list[PagePlan], config: dict, root: Path, command: str, model: str,
               feedback: list[str] | None = None) -> list[str]:
    """Write (or revise) one page, stamp it, and revise once on findings; the findings left."""
    path = root / page.path
    previous = path.read_text(encoding="utf-8") if path.is_file() else ""
    if previous and not feedback:
        parsed = check.parse_page(path)
        moved = check.Findings()
        if parsed:
            check.check_sources(parsed, root, moved)
        feedback = [f"source moved: {f['message']}" for f in moved.items]
        feedback += findings_for(path, root, {p.path for p in pages if p.work == "written"})
    for attempt in range(2):
        answer = call(command, model, writer_prompt(page, pages, config, root, previous, feedback), root)
        gaps, sources, body = parse_answer(answer)
        missing = [s for s in sources if check.read_source(root, s) is None]
        sources = [s for s in sources if s not in missing]
        problems = [f"source {s} does not exist; cite only files in the repository" for s in missing]
        if not body.startswith("# "):
            problems.append("the answer has no page: it must start with the helix lines, then `# <title>`")
        elif not sources:
            problems.append("the page names no sources: add a helix:source line for each file it states")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render(page, model, gaps, sources, body), encoding="utf-8")
            check.run_stamp([path], root)
            problems += findings_for(path, root, {p.path for p in pages if p.work == "written"})
        if not problems:
            return []
        if attempt == 0:
            previous = path.read_text(encoding="utf-8") if path.is_file() else answer
            feedback = problems
    return problems


def evaluate(page: PagePlan, root: Path, command: str, model: str) -> tuple[bool, list[str]]:
    answer = call(command, model, reviewer_prompt(page, root), root)
    verdict = VERDICT.search(answer)
    notes = [line[2:].strip() for line in answer.splitlines() if line.startswith("- ")]
    if verdict is None:
        return False, ["the evaluator gave no verdict"] + notes
    return verdict.group(1).lower() == "pass", notes


def run(root: Path, config: dict, pages: list[PagePlan], only: str = "", command: str = "",
        writer: str = "", reviewer: str = "", dry_run: bool = False) -> int:
    """Write the missing and stale written pages, evaluate the unreviewed ones; 1 if any is left."""
    from documentor.cli import assess, review

    command, writer, reviewer = settings(config, command, writer, reviewer)
    if writer == reviewer:
        print(f"documentor write: the writer and the evaluator must be different models (both {writer})", file=sys.stderr)
        return 2
    assess(root, config, pages)
    if only:
        chosen = [p for p in pages if only in (p.key, p.path, str(Path(p.path).with_suffix("")))]
        if not chosen or chosen[0].work != "written":
            print(f"documentor write: {only} is not a written page of the guide", file=sys.stderr)
            return 2
        todo = [(chosen[0], "write")]
    else:
        planned = {p.path for p in pages if p.work == "written"}
        # An unreviewed page its checks would block from a stamp goes back to the writer first.
        todo = [(p, "write" if p.entry["state"] in ("missing", "stale") or findings_for(root / p.path, root, planned)
                 else "evaluate")
                for p in pages if p.work == "written" and p.entry["state"] in ("missing", "stale", "unreviewed")]
    if not todo:
        print("every written page is current; nothing to write")
        return 0
    if dry_run:
        for page, step in todo:
            prompt = writer_prompt(page, pages, config, root) if step == "write" else reviewer_prompt(page, root)
            print(f"=== {step} {page.path} ({writer if step == 'write' else reviewer})\n{prompt}")
        return 0
    left = []
    for page, step in todo:  # every page first, so the links between them resolve before any review
        if step != "write":
            continue
        print(f"writing {page.path} ({writer})", flush=True)
        try:
            problems = write_page(page, pages, config, root, command, writer)
        except AgentError as error:
            problems = [str(error)]
        if problems:
            left.append((page, problems))
    for page, step in todo:
        path = root / page.path
        if any(page is p for p, _ in left):
            continue
        try:
            for attempt in range(2):
                print(f"evaluating {page.path} ({reviewer})", flush=True)
                passed, notes = evaluate(page, root, command, reviewer)
                if passed:
                    if review(root, path, f"agent-{reviewer}") != 0:
                        left.append((page, ["passed the evaluation, but its checks block the stamp (above)"]))
                    break
                if attempt == 0:
                    print(f"  failed: {'; '.join(notes) or 'no reasons given'}; revising", flush=True)
                    problems = write_page(page, pages, config, root, command, writer, notes)
                    if problems:
                        left.append((page, problems))
                        break
                else:
                    left.append((page, ["the evaluator failed it twice: " + "; ".join(notes)]))
        except AgentError as error:
            left.append((page, [str(error)]))
    for page, problems in left:
        print(f"LEFT {page.path}:", file=sys.stderr)
        for problem in problems[:8]:
            print(f"  {problem}", file=sys.stderr)
    print(f"\nwrote or evaluated {len(todo) - len(left)} of {len(todo)} pages under {publish_out(config)}")
    return 1 if left else 0
