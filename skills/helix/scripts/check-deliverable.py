#!/usr/bin/env python3
"""check-deliverable — deterministic gate for a HELIX deliverable script.

Checks a deck / one-pager / brief script (the `deliverable` artifact type)
for the things a person would otherwise catch on the first read: label
titles, HELIX vocabulary in bodies, unsourced numbers, placeholders, missing
or generic visuals, pattern limits and density rules from
deliverables/slide-patterns.yml, deck ordering, and an inspected render.

Usage:
    check-deliverable.py <script.md> [--catalog DIR] [--format text|json]

Exit 0 when no blocking findings; 1 when there are; 2 on usage errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("check-deliverable.py needs PyYAML (python3 -m pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

LABEL_TITLES = {
    "overview", "background", "results", "agenda", "summary", "introduction",
    "next steps", "risks", "timeline", "recommendation", "conclusion",
    "questions", "thank you", "appendix", "sources", "context", "problem",
    "solution", "status", "update", "roadmap", "team", "about us",
}
HELIX_VOCAB = re.compile(
    r"\b(?:FR|US|FEAT|ADR|TD|SD|TP|PRD|DEL|CONTRACT|WS)-\d+"
    r"|\bbeads?\b|\bratchets?\b|\bwork items?\b|\bacceptance criteri(?:a|on)\b"
    r"|\bAC\d+\b|\bartifact graph\b|\b(?:discover|frame|build|deploy|iterate) activity\b"
    r"|\bddx\b|\bstoryboard beats?\b|\bflow beats?\b|\bcandidate-briefing\b"
    r"|\bkeep_when_short\b",
    re.I,
)
PLACEHOLDER = re.compile(r"\[NEEDS CLARIFICATION|\[TODO\]|\bTBD\b|\[Fill in\]|<placeholder>|\[\.\.\.\]")
# A bracketed Capitalized phrase is usually a template slot left behind; markdown links `[text](url)` and ids like
# `[ADR-003]` do not match (same rule as validate-instance.py, warning severity)
BRACKET_TOKEN = re.compile(r"(?<!\[)\[(?:[A-Z][a-z]+)(?:[ /][A-Za-z]+)*\](?!\()")
NUMBER = re.compile(r"(?<![\w.])(?:\$?\d[\d,]*(?:\.\d+)?\s?(?:%|k|K|M|B|x)?)(?![\w.])")
# Methodology terms an audience outside the project would need defined; a warning, since some are plain English elsewhere
JARGON = re.compile(r"\b(?:concerns?|stop triggers?|autonomy levels?|quality floors?|ratchets?|framing|[\w-]+ modes?|the record|the profile|spikes?|project artifacts?|sibling profiles?)\b", re.I)
GENERIC_VISUALS = {"chart", "diagram", "image", "table", "graph", "picture", "photo", "screenshot", "none", "n/a"}

# title.slop: headline shapes that read as generated. A title is one sentence
# with a subject, a verb, and one concrete noun; these are the ways it fails
# that the human-facing voice profile names (reversals, rule-of-three padding,
# flattery, generalizations). Ported from sloptimizer's headline rules so the
# gate holds without that skill installed.
_APOS = r"(?:'|’)"
_LISTICLE_NOUNS = (r"(?:things|reasons|ways|lessons|mistakes|signs|secrets|tips|takeaways|truths|myths|"
                   r"ideas|insights|principles|habits|rules|questions|shifts|changes|factors|points|patterns|steps|keys|pillars|traps)")
_GROUP_NOUNS = (r"(?:teams?|people|leaders|engineers|developers|companies|organi[sz]ations|customers|users|"
                r"buyers|founders|executives|managers|businesses|enterprises|startups)")
_GROUP_VERBS = (r"(?:switch|win|lose|choose|prefer|want|need|trust|buy|adopt|leave|stay|succeed|fail|care|love|"
                r"hate|ignore|struggle|expect|demand|know|forget|resist|deserve)")
_IMPERATIVES = {
    "add", "adopt", "align", "ask", "audit", "build", "buy", "call", "check", "choose", "close", "commit",
    "configure", "count", "cut", "decide", "define", "deploy", "design", "document", "draft", "drive", "edit",
    "find", "fix", "follow", "frame", "get", "give", "go", "grow", "hire", "hold", "install", "join", "keep",
    "launch", "lead", "learn", "let", "list", "make", "map", "measure", "merge", "move", "name", "open", "own",
    "pick", "plan", "publish", "push", "put", "read", "release", "remove", "review", "run", "scale", "see",
    "sell", "send", "set", "share", "ship", "show", "sign", "start", "stop", "take", "tell", "test", "track",
    "train", "try", "turn", "use", "validate", "verify", "watch", "write",
}
_REVERSAL = [re.compile(p, re.I) for p in (
    rf"\b(?:(?:is|are|was|were|do|does|did|has|have|had|will|can|could|should)\s+not|(?:isn|aren|wasn|weren|doesn|don|hasn|haven){_APOS}t)\s*[.!]?$",
    r",\s*not\s+(?:a|an|the|your|our|their|just|only|merely|simply|because)\b",
    r"^not\s+(?:a|an|the|just|only|because)\b",
    r"\bnot\s+[^,;.]{1,40}?,?\s+but\s+\w",
    rf"\b(?:isn{_APOS}t|aren{_APOS}t|is not|are not|doesn{_APOS}t|don{_APOS}t)\b[^,;.]{{1,60}}[,;.]\s*(?:it{_APOS}s|it is|they{_APOS}re|they are|but)\b",
    r"^(?:less|fewer|more)\b[^,]{1,40},\s*(?:less|fewer|more)\b",
)]
_FLATTERY = [re.compile(p, re.I) for p in (
    r"\byour best (?:teams?|people|engineers?|work|days?)\b", r"\b(?:teams|people|leaders|companies) like yours?\b",
    r"\bhold(?:s|ing)? (?:ourselves|yourself|yourselves|themselves) to\b", r"\byou deserve\b",
    r"\bthe (?:smartest|best|brightest) (?:teams|people|minds|engineers)\b", r"\byou already (?:know|use|have|do|trust)\b",
    r"\bworld[- ]class\b", r"\bbest[- ]in[- ]class\b", r"\bindustry[- ]leading\b", r"\bthe (?:bar|standard) we (?:set|hold|keep)\b",
)]
_APHORISM = [re.compile(p, re.I) for p in (
    r"\bis the new\b", r"\bthe only \w+ that matters\b", r"\bis everything\b", r"\bmore than ever\b", r"\bdone right\b",
    r"\bis (?:a|the) (?:feature|superpower|multiplier|moat|journey|mindset)\b", r"\bis (?:a|an) (?:nice-to-have|luxury)\b",
    r"\b(?:wins|matters|counts)\s*[.!]?$", r"\bat scale\s*[.!]?$", r"\bthe hard way\b", r"\bchanges everything\b",
    r"\bhere to stay\b", r"\bthe future of\b", r"\bwelcome to\b",
    r"^that(?:'|’)?s what makes\b", r"^that is what makes\b",
    r"^(?:this|that) is (?:what|how|why) \w+ (?:works|matters|wins|scales|holds)\b",
    r"\beverything else is (?:detail|plumbing|noise|downstream)\b",
)]
_COUNT = (
    r"(?:\d[\d,]*|a dozen|dozens|hundreds|thousands|"
    r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:-(?:one|two|three|four|five|six|seven|eight|nine))?|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    r"two|three|four|five|six|seven|eight|nine|ten)"
)
_INVENTORY_VERBS = (
    r"(?:with|has|have|had|offers?|ships?|includes?|provides?|contains?|routes?|spans?|across|covers?|"
    r"supports?|brings?|delivers?|packs?|features?|comes with|made (?:up )?of|consists? of|bundles?|"
    r"holds?|carries|carry|adds?|lists?|boasts?|totals?|comprises?)"
)
_HEDGES = re.compile(
    r"\b(?:also|(?<!not )just|simply|really|actually|basically|essentially|arguably|perhaps|maybe|somewhat|"
    r"quite|very|truly|genuinely|literally|surprisingly|frankly|honestly|fairly|rather|pretty)\b", re.I)
_TITLE_MAX_WORDS, _TITLE_TARGET_WORDS = 10, 8
_MANNERED = (  # vendored from sloptimizer assets/vale/styles/Sloptimizer/ManneredProse.yml; tests/validate-headline-sync.sh keeps it equal
    '\\bearns? (?:its|their) keep\\b',
    '\\b(?:a|the|one) (?:dial|knob|lever) worth (?:turning|pulling)\\b',
    '\\b(?:dials|knobs|levers) (?:to|worth) (?:turn|pull|turning|pulling)\\b',
    '\\bpulls? (?:its|their|his|her) (?:own )?weight\\b',
    '\\bpunch(?:es)? above (?:its|their) weight\\b',
    '\\b(?:do|does|did|doing) (?:the|all the|most of the) heavy lifting\\b',
    '\\b(?:is|are|was|were) doing (?:a lot of|most of the|the real|all the) work\\b',
    '\\bmoves? the needle\\b',
    '\\blow-hanging fruit\\b',
    '\\btable stakes\\b',
    '\\bnorth star\\b',
    '\\bsilver bullet\\b',
    '\\bsecret sauce\\b',
    '\\bunder the hood\\b',
    '\\bdouble-edged sword\\b',
    '\\bcuts both ways\\b',
    '\\ba tale of two\\b',
    "\\bthe lion(?:'|’)s share\\b",
    '\\bboils? down to\\b',
    '\\bthe elephant in the room\\b',
    '\\bthe beating heart of\\b',
    '\\ba breath of fresh air\\b',
    '\\bthrough the lens of\\b',
    '\\bat the intersection of\\b',
    '\\bfirst-class citizen\\b',
    '\\bin lockstep\\b',
    '\\bwears? (?:two|many|several|multiple) hats\\b',
    '\\bpaints? a (?:clear |vivid |fuller |complete )?picture\\b',
    '\\bthe wheels (?:come|came|fall|fell) off\\b',
    '\\bload-bearing (?:assumption|claim|idea|sentence|word|phrase|question|decision|detail|premise|distinction)\\b',
    '\\bthe connective tissue (?:of|between)\\b',
    '\\bthe glue that holds\\b',
    '\\bthe plumbing (?:of|behind|underneath)\\b',
    '\\bthe scaffolding (?:of|for|around)\\b',
    '\\bthe engine (?:of|behind|driving)\\b',
    '\\bshine[sd]? a light on\\b',
    '\\bpeel(?:s|ing)? back the (?:layers|curtain|onion)\\b',
    '\\bthe tip of the iceberg\\b',
    '\\bthe missing piece of the puzzle\\b',
    '\\ba (?:seat|place) at the table\\b',
    '\\bat a crossroads\\b',
    '\\bthe (?:road|path) ahead\\b',
    '\\bfull circle\\b',
)
_STATUS_JARGON = (  # vendored from sloptimizer assets/vale/styles/SloptimizerExternal/StatusJargon.yml (ignorecase); the sync test keeps it equal
    '\\bportability reference\\b',
    '\\brepresentative workload\\b',
    '\\bworking hypothesis\\b',
    '\\bproposed contract\\b',
    '\\bcandidate,? (?:scope open|tbd|pending)\\b',
    '\\bscope (?:open|tbd|to be (?:defined|determined))\\b',
    '\\bfit (?:unproven|tbd|unclear)\\b',
    '\\bnot (?:yet )?committed\\b',
    '\\bdirectionally (?:correct|right|aligned)\\b',
    '\\bunder (?:exploration|consideration|evaluation|investigation)\\b',
    '\\bin flight\\b',
    '\\bto be validated\\b',
    '\\bsubject to (?:validation|confirmation|alignment)\\b',
    '\\bpending (?:alignment|validation|confirmation|decision)\\b',
    '\\baspirational\\b',
    '\\bnascent\\b',
    '\\blighthouse (?:project|use case|customer|initiative)\\b',
    '\\bpathfinder\\b',
    '\\bexemplar\\b',
    '\\bstraw ?man\\b',
    '\\bnaming tbd\\b',
    '\\btbd\\b',
    '\\bwip\\b',
)
_TAXONOMY = (  # vendored from SloptimizerExternal/InternalTaxonomy.yml (case-sensitive, inline (?i:) groups)
    '\\b(?i:zone|plane|pillar|horizon|wave|workstream|swimlane|quadrant|lane|epic|theme)s? \\d{1,2}\\b',
    '\\bP\\d{1,2}(?:[ ,/]+P\\d{1,2})+\\b',
    '\\b(?i:principle|pillar)s? P?\\d{1,2}\\b',
)
_MARKETING = (  # vendored from SloptimizerExternal/MarketingRegister.yml (ignorecase)
    '\\bleverag(?:e|es|ed|ing)\\b',
    '\\bdifferentiat(?:ed|ing|or|ors)\\b',
    '\\bcommoditi[sz](?:e|es|ed|ing|ation)\\b',
    '\\bbest[- ]of[- ]breed\\b',
    '\\benterprise[- ]grade\\b',
    '\\bfuture[- ]proof(?:ed|ing)?\\b',
    '\\bturnkey\\b',
    '\\bholistic(?:ally)?\\b',
    '\\bfrictionless\\b',
    '\\bnext[- ]gen(?:eration)?\\b',
    '\\bsynerg(?:y|ies|istic)\\b',
    '\\bvalue[- ]add(?:ed)?\\b',
    '\\bmission[- ]critical\\b',
    '\\bstate[- ]of[- ]the[- ]art\\b',
    '\\b(?:universal|unified|seamless|delightful) experience\\b',
    '\\bsingle (?:pane|source) of (?:glass|truth)\\b',
    '\\bgoverned (?:conversational|data|ai) access\\b',
)
# HELIX-owned, not vendored from sloptimizer (tests/validate-headline-sync.sh does not touch this
# list): the human-facing voice profile's three named bland-prose smells the mechanical rules above
# cannot see — a title or body can pass every rule above and still read like a policy memo. See
# voice.yml's human-facing `avoid` list, which this ports as a mechanical backstop, not a substitute
# for the editorial "would a person actually say this" pass in the deliverable prompt.
_BUREAUCRATIC_EUPHEMISM = (
    '\\bbefore the (?:decision|review|evaluation|assessment) (?:closes|concludes|finalizes|lands)\\b',
    '\\bthe (?:decision|review|evaluation|assessment) (?:closes|concludes|finalizes|lands)\\b',
    '\\bcloses? the (?:decision|review|evaluation|assessment) on\\b',
    '\\bpending (?:finalization|closure)\\b',
    '\\bconduct(?:s|ed|ing)? an? (?:evaluation|assessment|investigation)\\b',
    '\\bprovide(?:s|d)? (?:clarification|guidance)\\b',
    '\\bactionable insights?\\b',
    '\\brobust (?:framework|solution|process)\\b',
)
# HELIX-owned, not vendored: the negative-parallelism shapes the upstream title rules leave alone because a
# headline may legitimately say "instead of". In a body bullet they are the guidance's own register echoed
# back ("not one it makes", "a guess instead of a record", "never a recommendation"), so they run on shapes
# only. voice.yml's human-facing avoid list names them under negative parallelism and slogan closers.
_BODY_REVERSAL = [re.compile(p, re.I) for p in (
    r"\bnot one (?:it|we|they|this|that) \w+",
    r"\brather than\b",
    r"\b(?:a|an|the) [\w-]+ instead of (?:a|an|the) [\w-]+\s*[.!]?$",
    r",\s*not\s+[a-z][\w-]*(?:\s+[a-z][\w-]*){0,3}\s*(?:[.;]|$)",   # "..., not published for the software" (bare noun or participle)
    r"\bnever (?:a|an|the|to|as)\b",
    r"^(?:skip|ignore|delay|postpone|wait on|do nothing about) [^,]{1,40}, and (?:the|this|that|your|our) \w+",
)]
_EM_DASH = re.compile(r"\u2014|\s\u2013\s|\s--\s")   # an unspaced en dash is a range (2016–2017) and stays
# HELIX-owned: the copula-avoidance and borrowed-authority shapes voice.yml names; bodies and cells only
_COPULA_AVOIDANCE = re.compile(r"\b(?:serves?|stands?|acts?|functions?) as\b|\bboasts?\b", re.I)
_BORROWED_AUTHORITY = re.compile(
    r"\b(?:experts?|analysts?|observers?|many|some|critics?|practitioners?) (?:say|agree|argue|note|believe|consider|suggest)\b"
    r"|\bstudies (?:show|suggest|indicate)\b|\bit is (?:widely|generally|well) (?:known|accepted|regarded|understood)\b"
    r"|\bwidely (?:regarded|considered|seen) as\b", re.I)
_BOLD_LABEL_BULLET = re.compile(r"^\*\*[^*]{1,40}\*\*\s*[:.]")
_COUNT_OF = r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten) of (?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b"
_TITLE_CASE = r"(?:[A-Z][\w'’-]*|[a-z]{1,3}|[\d$%,.]+|[:;,-]+)(?:\s+(?:[A-Z][\w'’-]*|[a-z]{1,3}|[\d$%,.]+|[:;,-]+))+"
_NARRATION = re.compile(
    r"^(?:in )?(?:this|the following|these|the present) (?:brief|page|one-pager|document|memo|deck|slide|profile|paper|section|pages|report|note)\b"
    r"|^here (?:we|you)\b|^the following (?:sections?|pages?|table)\b|^(?:below|above),? (?:we|you)\b|^as (?:shown|described|noted) (?:below|above)\b", re.I)
_HEADING_NUMBERS = {"27001", "27701", "9001", "2", "3"}  # standard names (ISO 27001) are labels; the gate keeps SOC 1/2/3 and ISO numbers as text
_CONTAINER_NOUNS = (
    r"(?:capabilit(?:y|ies)|foundations?|layers?|overview|landscape|ecosystem|frameworks?|pillars?|principles|"
    r"considerations|enablers|building blocks|components|dimensions|themes|elements|areas|aspects|fundamentals|"
    r"essentials|basics|highlights|context|background|approach|philosophy|vision|stack|platform|architecture|"
    r"framing|scope|summary|agenda|introduction|recap|takeaways|learnings|observations|reflections|opportunities|"
    r"challenges|implications|next steps|key points|the ask|deep[- ]dive|overview and context)"
)
_SELF_JUSTIFYING = [re.compile(p, re.I) for p in (
    r"^how to read (?:this|the)\b",
    r"^how this (?:slide|page|view|diagram|map) (?:works|is organi[sz]ed|reads)\b",
    r"^what this (?:slide|page|deck|diagram|view|map) (?:shows|means|is saying|tells)\b",
    r"^reading (?:this|the) (?:slide|chart|diagram|map|table)\b",
    r"^(?:a )?note on (?:how to read|reading|method|methodology)\b",
    r"^(?:design |guiding |core |our )?principles? (?:served|applied|honou?red|met|addressed|upheld|in play)\b",
    r"^why (?:we|our|us|the \w+|this|it|that) (?:own|control|built|build|chose|choose|keep|hold|matter|matters|care|need|exist)",
    r"^why (?:this|it|that) (?:matters|is different|is hard|works)\b",
    r"^what (?:stays|remains|does ?n[o'’]t change|we (?:control|own|keep|hold|guarantee))\b",
    r"^(?:the |our |design )?rationale\b",
)]
_TRAILING_COMMENTARY = re.compile(
    r"[.!?]\s+(?:Built|Designed|Intended|Meant|Chosen|Included|Added|Kept|Positioned|Shown|Placed|Retained|Selected)"
    r"\s+(?:as|to|because|for|here|so|since)\b"
    r"|[.!?]\s+(?:Serves|Acts|Exists|Stands|Functions)\s+(?:as|to|because|so)\b"
    r"|[.!?]\s+(?:This|It|That) (?:is|was) (?:the|our|a) (?:worked example|reference|proof point|test case|first step)\b")
_SHAPE_STOPWORDS = frozenset(
    "the a an and or but of to in on for with by from at as is are was were be been being it its this that these those "
    "we our you your they their he she his her not no do does did have has had will can into than then so if when what "
    "which who how all any each every one two three".split())
_TITLE_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "at", "by", "for", "with", "from", "into", "than",
    "that", "this", "these", "those", "it", "its", "is", "are", "was", "were", "be", "been", "as", "if", "when",
    "once", "while", "before", "after", "not", "no", "so", "you", "your", "we", "our", "they", "their", "one",
    "each", "every", "any", "all", "can", "will", "now", "then", "here", "there", "what", "who", "how", "per",
    "own", "back", "up", "out", "under", "over", "more", "less", "most", "much", "very", "just", "only",
}


def _words_n(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9$%][\w$%.,'’-]*", text))


def label_slop(text: str, container: bool = True) -> list[str]:
    """Rules for a unit that stands alone (a slide title, a card label, a caption): container title,
    self-justifying section, shouting label. `container` is off for headings in internal documents."""
    t = text.strip()
    out: list[str] = []
    if container:
        stripped = re.sub(r"[.!?:]+$", "", t)
        if _words_n(stripped) <= 4:
            m = re.fullmatch(rf"(?:[\w&/'’-]+\s+){{0,3}}{_CONTAINER_NOUNS}", stripped, re.I)
            if m:
                out.append(f"container title {m.group(0)!r}; name what the slide shows, not the category it belongs to")
        for p in _SELF_JUSTIFYING:
            m = p.search(t)
            if m:
                out.append(f"self-justifying section {m.group(0)!r}; the text argues for itself, delete it or move the one fact into the subtitle")
                break
    letters = re.sub(r"[^A-Za-z]", "", t)
    if len(letters) >= 6 and letters == letters.upper():
        n = _words_n(t)
        question = re.match(r"^(?:WHAT|WHY|HOW|WHERE|WHEN|WHO)\b", t)
        if (n >= 4 and len(letters) >= 12) or (n >= 2 and question):
            out.append(f"shouting label {t!r}; shorten to a plain noun or delete")
    return out


def external_slop(text: str) -> list[str]:
    """The SloptimizerExternal phrase lists: invented status, internal taxonomy codes, marketing register."""
    out: list[str] = []
    for name, tokens, flags, msg in (
        ("invented status", _STATUS_JARGON, re.I, "use a state the reader already knows: in use, built, specified, idea, not adopted, retired"),
        ("taxonomy code", _TAXONOMY, 0, "the reader does not have the map; name the thing or drop the code"),
        ("marketing register", _MARKETING, re.I, "say the plain noun or verb, or the fact the reader can check"),
    ):
        for pat in tokens:
            m = re.search(pat, text, flags)
            if m:
                out.append(f"{name} {m.group(0)!r}; {msg}")
                break
    return out


def bureaucratic_slop(text: str) -> list[str]:
    """HELIX-owned backstop (not vendored) for the human-facing voice profile's bland-prose smells: a
    bureaucratic noun standing in for a plain verb, an empty precision-adjective on a plain noun. Runs
    on titles and bodies alike, since the offending phrase is as likely in an ask line as a heading."""
    for pat in _BUREAUCRATIC_EUPHEMISM:
        m = re.search(pat, text, re.I)
        if m:
            return [f"bureaucratic euphemism {m.group(0)!r}; say the plain verb and the concrete stakes"]
    return []


def shape_slop(text: str) -> list[str]:
    """Rules for a non-title unit on a slide (a bullet, a card label, a caption, a verdict): the label rules plus the
    closer shapes a title cannot carry."""
    t = text.strip()
    out = label_slop(t)
    reversed_ = False
    for p in _REVERSAL:
        m = p.search(t)
        if m:
            out.append(f"contrastive reversal {m.group(0).strip()!r}; state the positive claim")
            reversed_ = True
            break
    for p in _APHORISM:
        m = p.search(t)
        if m:
            out.append(f"pseudo-aphorism {m.group(0)!r}; delete the closer, do not replace it with another")
            break
    for p in _FLATTERY:
        m = p.search(t)
        if m:
            out.append(f"flattery {m.group(0)!r}; replace the compliment with a checkable fact")
            break
    m = _TRAILING_COMMENTARY.search(t)
    if m:
        out.append(f"trailing commentary {m.group(0)!r}; keep the first sentence, move any status into the label")
    out.extend(bureaucratic_slop(t))
    for p in ([] if reversed_ else _BODY_REVERSAL):   # one finding per reversal; the upstream rule wins when both match
        m = p.search(t)
        if m:
            out.append(f"negative parallelism {m.group(0).strip()!r}; state the positive claim and stop")
            break
    if _EM_DASH.search(t):
        out.append("em dash; use a period, a comma, or a colon")
    m = _COPULA_AVOIDANCE.search(t)
    if m:
        out.append(f"copula avoidance {m.group(0)!r}; say is, has, or does")
    m = _BORROWED_AUTHORITY.search(t)
    if m:
        out.append(f"borrowed authority {m.group(0)!r}; name the source or drop the claim")
    if _BOLD_LABEL_BULLET.match(t):
        out.append("bold-label bullet; write the sentence, or make it a table row")
    return out


def _shape_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z'’-]+", text.lower()) if w not in _SHAPE_STOPWORDS and len(w) > 2}


_RESTATEMENT_THRESHOLD = 0.5   # content-word Jaccard at or above this is a restatement
_RESTATEMENT_MIN_WORDS = 4     # units with fewer content words are labels, not candidates


def restatements(shapes: list[str]) -> list[tuple[str, str]]:
    """(text, earlier text) pairs on one slide whose content words overlap by half or more (lexical only)."""
    out: list[tuple[str, str]] = []
    bags = [(t, _shape_words(t)) for t in shapes]
    for i, (t, bag) in enumerate(bags):
        if len(bag) < _RESTATEMENT_MIN_WORDS:
            continue
        for other, obag in bags[:i]:
            if len(obag) < _RESTATEMENT_MIN_WORDS:
                continue
            if len(bag & obag) / len(bag | obag) >= _RESTATEMENT_THRESHOLD:
                out.append((t, other))
                break
    return out


def title_slop(title: str, slide: bool = False, label_heading: bool = False) -> list[str]:
    """Headline slop findings for one title; each is a short message with the match.
    `slide` is a slide title or a heading a reader outside the team will see: the label rules and the external
    phrase lists apply. Off, only the shouting-label check runs, since `## Overview` is a convention inside a team.
    `label_heading` is a reference document's section label (Introduction, Competitive landscape): the container
    rule is off, the external phrase lists stay on."""
    t = title.strip()
    out: list[str] = label_slop(t, container=slide and not label_heading)
    if slide:
        out.extend(external_slop(t))
    out.extend(bureaucratic_slop(t))
    for p in _REVERSAL:
        m = p.search(t)
        if m:
            out.append(f"contrastive reversal {m.group(0).strip()!r}; state the positive claim")
            break
    m = re.search(r"(?<!\d):(?!\d|//)\s*(.+)$", t)
    if m and m.group(1).strip():
        items = [i for i in re.split(r",\s+|\s+(?:and|or)\s+", m.group(1)) if i.strip()]
        if len(items) >= 2:
            out.append(f"colon list {t[m.start():]!r}; keep the one item the unit proves, the list is body")
        else:
            out.append(f"colon reveal {t[m.start():]!r}; write one sentence with a subject and a verb")
    verbs = []
    for seg in re.split(r"[,;]\s+|\.\s+", t):
        seg = re.sub(r"^(?:and|then|or)\s+", "", seg.strip(), flags=re.I)
        w = re.match(r"[A-Za-z]+", seg)
        if w and w.group(0).lower() in _IMPERATIVES:
            verbs.append(w.group(0))
    if len(verbs) >= 3:
        out.append(f"imperative chain {', '.join(verbs)!r}; one verb per title, the steps are body")
    m = re.search(rf"\b(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:[\w-]+\s+){{0,2}}?{_LISTICLE_NOUNS}\b", t, re.I)
    if m:
        out.append(f"listicle count {m.group(0)!r}; name the item that matters")
    neg = re.findall(rf"\b(?:no|not|never|nothing|none|nor|without)\b|n{_APOS}t\b", t, re.I)
    if len(neg) >= 2:
        out.append(f"stacked negation {', '.join(neg)!r}; say what it does or keeps")
    item = r"[\w$%'’-]+(?: [\w$%'’-]+){0,3}"
    m = re.search(rf"\b{item},\s+{item},?\s+(?:and|or)\s+[\w$%'’-]+", t, re.I)
    if m:
        out.append(f"rule-of-three list {m.group(0)!r}; keep one concrete noun")
    for p in _FLATTERY:
        m = p.search(t)
        if m:
            out.append(f"flattery {m.group(0)!r}; replace the compliment with a checkable fact")
            break
    for p in _APHORISM:
        m = p.search(t)
        if m:
            out.append(f"pseudo-aphorism {m.group(0)!r}; replace the slogan with the claim and its number")
            break
    m = re.search(rf"^{_GROUP_NOUNS}\s+{_GROUP_VERBS}\b", t, re.I) or re.search(rf"\b(?:every|all|any)\s+(?:[\w-]+\s+)?{_GROUP_NOUNS}\b", t, re.I)
    if m:
        out.append(f"universal claim {m.group(0)!r}; scope it to which teams, how many, measured where")
    for pat in _MANNERED:
        m = re.search(pat, t, re.I)
        if m:
            out.append(f"mannered phrase {m.group(0)!r}; say what you mean in plain words: the thing, the action, or the number")
            break
    m = re.search(rf"\b{_INVENTORY_VERBS}\s+(?:(?:over|more than|about|nearly|some|up to|around|another)\s+)?{_COUNT}\s+(?:[\w-]+\s+){{0,2}}?[A-Za-z][\w-]*s\b", t, re.I)
    if m:
        out.append(f"inventory count {m.group(0)!r}; the size of the catalog is body, the title says what it does for the reader")
    m = _HEDGES.search(t)
    if m:
        out.append(f"hedge {m.group(0)!r}; delete it, or scope the claim with a number")
    if _EM_DASH.search(t):
        out.append("em dash; one sentence, no aside")
    n = len(re.findall(r"[A-Za-z0-9$%][\w$%.,'’-]*", t))
    if n > _TITLE_MAX_WORDS:
        out.append(f"over-length ({n} words); aim for {_TITLE_TARGET_WORDS} or fewer, hard stop {_TITLE_MAX_WORDS}")
    return out


def content_words(title: str) -> set[str]:
    """Crude stems of the content words in a title, for the horizontal-logic check."""
    out: set[str] = set()
    for w in re.findall(r"[a-z0-9]+", title.lower()):
        if w in _TITLE_STOPWORDS or len(w) < 3:
            continue
        # light stemming so gates/gate, templates/template, drifting/drift, agreed/agree meet; never below 4 letters
        if w.endswith("ing") and len(w) > 6:
            w = w[:-3]
        elif w.endswith("ed") and len(w) > 5:
            w = w[:-2]
        elif w.endswith("s") and len(w) > 4 and not w.endswith("ss"):
            w = w[:-2] if w.endswith(("ses", "xes", "zes", "ches", "shes")) else w[:-1]
        if w.endswith("e") and len(w) > 4:     # drifted -> drift, agree -> agre: strip a trailing e so both forms match
            w = w[:-1]
        out.add(w)
    return out


def load_patterns(catalog: Path | None, script_path: Path) -> dict:
    candidates = []
    if catalog:
        candidates += [catalog / "deliverables" / "slide-patterns.yml",
                       catalog / "workflows" / "deliverables" / "slide-patterns.yml"]
    for parent in [script_path.resolve()] + list(script_path.resolve().parents):
        candidates.append(parent / "workflows" / "deliverables" / "slide-patterns.yml")
    here = Path(__file__).resolve().parent
    candidates += [here.parent / "references" / "deliverables" / "slide-patterns.yml",
                   here.parent.parent.parent / "workflows" / "deliverables" / "slide-patterns.yml"]
    for c in candidates:
        if c.is_file():
            data = yaml.safe_load(c.read_text(encoding="utf-8")) or {}
            return {"path": c, "patterns": {p["id"]: p for p in data.get("patterns", [])},
                    "density": data.get("density", {})}
    return {"path": None, "patterns": {}, "density": {}}


def load_flow(catalog: Path | None, script_path: Path, flow_id: str) -> dict:
    """The chosen flow's own file (deliverables/flows/<id>.yml): heading_style and which beats are required."""
    if not re.fullmatch(r"[a-z][a-z0-9-]*", flow_id or ""):
        return {}
    rel = Path("deliverables") / "flows" / f"{flow_id}.yml"
    candidates = []
    if catalog:
        candidates += [catalog / rel, catalog / "workflows" / rel]
    for parent in [script_path.resolve()] + list(script_path.resolve().parents):
        candidates.append(parent / "workflows" / rel)
    here = Path(__file__).resolve().parent
    candidates += [here.parent / "references" / rel, here.parent.parent.parent / "workflows" / rel]
    for c in candidates:
        if c.is_file():
            return yaml.safe_load(c.read_text(encoding="utf-8")) or {}
    return {}


def load_theme(catalog: Path | None, script_path: Path) -> dict:
    candidates = []
    if catalog:
        candidates += [catalog / "deliverables" / "theme.yml",
                       catalog / "workflows" / "deliverables" / "theme.yml"]
    for parent in [script_path.resolve()] + list(script_path.resolve().parents):
        candidates.append(parent / "workflows" / "deliverables" / "theme.yml")
    here = Path(__file__).resolve().parent
    candidates += [here.parent / "references" / "deliverables" / "theme.yml",
                   here.parent.parent.parent / "workflows" / "deliverables" / "theme.yml"]
    for c in candidates:
        if c.is_file():
            data = yaml.safe_load(c.read_text(encoding="utf-8")) or {}
            return data.get("layout", {}).get("document", {}) or {}
    return {}


def split_frontmatter(text: str) -> tuple[dict, str, int]:
    if not text.startswith("---\n"):
        return {}, text, 0
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text, 0
    fm = yaml.safe_load(text[4:end]) or {}
    body = text[end + 5:]
    return fm, body, text[:end + 5].count("\n")


def sections(body: str) -> dict[str, tuple[int, str]]:
    """H2 title -> (line offset, text)."""
    out: dict[str, tuple[int, str]] = {}
    current, start, buf = None, 0, []
    for i, line in enumerate(body.splitlines()):
        if line.startswith("## "):
            if current is not None:
                out[current] = (start, "\n".join(buf))
            current, start, buf = line[3:].strip(), i, []
        else:
            buf.append(line)
    if current is not None:
        out[current] = (start, "\n".join(buf))
    return out


def units(content: str, offset: int) -> list[dict]:
    out: list[dict] = []
    cur = None
    for i, line in enumerate(content.splitlines()):
        m = re.match(r"^### (\d+)\.\s+(.*)$", line)
        if m:
            cur = {"n": int(m.group(1)), "title": m.group(2).strip(), "line": offset + i + 1,
                   "fields": {}, "raw": []}
            out.append(cur)
            continue
        if cur is None:
            continue
        cur["raw"].append(line)
        fm = re.match(r"^\*\*(Pattern|Body|Visual|Notes|Sources)\*\*:\s*(.*)$", line)
        if fm:
            cur["fields"][fm.group(1)] = {"line": offset + i + 1, "text": fm.group(2).strip(), "lines": []}
            cur["_last"] = fm.group(1)
        elif cur.get("_last") and line.strip():
            lines = cur["fields"][cur["_last"]]["lines"]
            # a wrapped bullet continues the previous bullet; the renderer joins the same way
            if cur["_last"] == "Body" and lines and not line.strip().startswith(("-", "*", "•")):
                lines[-1] = lines[-1] + " " + line.strip()
            else:
                lines.append(line)
    for u in out:
        u.pop("_last", None)
    return out


def words(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9$%][\w$%.,'-]*", s))


def visual_shapes(vline: str) -> list[str]:
    """The text cells a Visual spec puts on the slide: list items, cells, captions, verdicts, headers, the hub label."""
    if not vline.startswith("kind:"):
        return []
    spec_text = vline
    end = re.search(r"\.\s|\.$", vline)
    if end:
        spec_text = vline[: end.start()]
    out: list[tuple[str, bool]] = []
    for part in spec_text.split(" | "):
        kv = re.match(r"^([\w-]+):\s*(.*)$", part)
        if not kv or kv.group(1) in ("kind", "highlight", "now", "prefer", "columns", "split", "side", "icons", "icon", "owners", "dates"):
            continue
        node_field = kv.group(1) in NODE_FIELDS
        for item in kv.group(2).split(";"):
            for k, cell in enumerate(item.split(" / ")):
                cell = cell.strip()
                if cell and re.search(r"[A-Za-z]", cell):
                    # a node label names a part of a figure (a layer, a step, a spoke); it is not a section title
                    out.append((cell, node_field or (k == 0 and kv.group(1) in NODE_FIRST_CELL)))
    return out


# Visual fields whose values label parts of a figure rather than stand as titles: the container-title rule is off for them.
NODE_FIELDS = {"steps", "layers", "milestones", "center", "columns", "left", "right"}
NODE_FIRST_CELL = {"spokes", "items", "rows", "stats", "risks"}
# Patterns whose layout draws the body bullets on the slide; elsewhere the bullets are the script's evidence of record.
BODY_ON_SLIDE = {"claim-evidence", "agenda", "quote", "ask-next-steps", "statement", "section-divider"}


def unit_weight(vtext: str, n_bullets: int) -> float:
    """A rough proxy for a unit's rendered height on a document page: a table/risk-grid/list's row
    count dominates over its bullet count. Mirrors render-doc.js's identical heuristic (used there to
    balance a one-pager's two-column grid), reused here as the one estimate `render_doc_page_estimate`
    needs and word count alone cannot give: a table's cells are short but its rows are tall."""
    for field in ("rows", "risks", "items"):
        m = re.search(rf"\b{field}:\s*(.*?)(?:\s\|\s|\.\s|\.$|$)", vtext)
        if m and m.group(1).strip():
            n = len([p for p in m.group(1).split(";") if p.strip()])
            if n:
                return 2 + n * 1.3
    return 2 + n_bullets * 0.9


# Calibration for the brief page estimate: an empirical weight-per-page constant read off real
# render-doc.js output (an 8-unit brief with a mix of tables, a two-column comparison, and a risk
# grid rendered to 4 pages: total weight 60.3, so ~15.1 weight per page), not a modeled page
# geometry. It is deliberately named and kept in one place so it can be recalibrated without hunting
# through the check; treat its output as a sanity range, not a page count.
DOC_WEIGHT_PER_PAGE = 15.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--catalog")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--dump-units", action="store_true", help="print the parsed units as JSON and exit (parser agreement tests)")
    args = ap.parse_args()
    path = Path(args.script)
    if not path.is_file():
        print(f"no such file: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    fm, body, fm_lines = split_frontmatter(text)
    pats = load_patterns(Path(args.catalog) if args.catalog else None, path)
    doc_layout = load_theme(Path(args.catalog) if args.catalog else None, path)
    findings: list[dict] = []

    def add(sev: str, check: str, msg: str, line: int | None = None) -> None:
        findings.append({"severity": sev, "check": check, "message": msg, "line": line})

    ddx = fm.get("ddx", {}) if isinstance(fm, dict) else {}
    kind = (ddx.get("kind") or "deck") if isinstance(ddx, dict) else "deck"
    is_doc = kind != "deck"   # brief or one-pager: a read page, not a projected slide
    secs = sections(body)
    for required in ("Brief", "Story", "Content", "Sources", "Assumptions and gaps", "Render"):
        if required not in secs:
            add("BLOCKING", "section", f"missing '## {required}'")
    if "Content" not in secs:
        return report(findings, args.format, path)

    for m in PLACEHOLDER.finditer(body):
        line = fm_lines + body.count("\n", 0, m.start()) + 1
        add("BLOCKING", "placeholder", f"placeholder text {m.group(0)!r}", line)
    for m in BRACKET_TOKEN.finditer(body):
        line = fm_lines + body.count("\n", 0, m.start()) + 1
        add("WARNING", "placeholder.bracket", f"bracketed phrase {m.group(0)!r} looks like a template slot", line)

    sources_text = secs.get("Sources", (0, ""))[1]
    source_ids = set(re.findall(r"^\|\s*(S\d+)\s*\|", sources_text, re.M))
    if not source_ids:
        add("BLOCKING", "sources", "Sources table has no S<n> rows")

    # The chosen flow decides two things the gate needs early: whether headings are claims (a deck or a
    # persuasive document) or labels (a reference such as candidate-briefing), and whether the ask beat
    # is required. Without a flow file both default to the deck's rules.
    story_text = secs.get("Story", (0, ""))[1]
    flow_m = re.search(r"\*\*Flow\*\*:\s*([\w-]+)", story_text)
    flow = load_flow(Path(args.catalog) if args.catalog else None, path, flow_m.group(1) if flow_m else "")
    label_headings = flow.get("heading_style") == "label"
    ask_required = next((bool(b.get("required", True)) for b in flow.get("beats", []) if b.get("name") == "ask"), True)

    h1 = re.search(r"^# (.+)$", body, re.M)
    if h1:
        h1_line = fm_lines + body.count("\n", 0, h1.start()) + 1
        h1_text = h1.group(1).strip()
        if not label_headings and (h1_text.lower().strip(" .:") in LABEL_TITLES or words(h1_text) < 3):
            add("BLOCKING", "title.claim", f"document title is a label, not a claim: {h1_text!r}", h1_line)
        for msg in title_slop(h1_text, slide=True, label_heading=label_headings):
            add("BLOCKING", "title.slop", f"document title: {msg}", h1_line)
        if re.search(_COUNT_OF, h1_text, re.I):
            add("BLOCKING", "title.count", f"document title carries a count: {h1_text!r}; the finding goes in the introduction, the title names the subject", h1_line)
        if re.fullmatch(_TITLE_CASE, h1_text) and words(h1_text) >= 4:
            add("BLOCKING", "title.case", f"document title is in Title Case: {h1_text!r}; write it as a sentence", h1_line)

    content_off = fm_lines + secs["Content"][0]
    us = units(secs["Content"][1], content_off)
    if args.dump_units:
        dump = []
        for u in us:
            bf = u["fields"].get("Body", {})
            bl = ([bf["text"]] if bf.get("text") else []) + [l for l in bf.get("lines", []) if l.strip().startswith(("-", "*", "•"))]
            dump.append({"n": u["n"], "title": u["title"], "pattern": u["fields"].get("Pattern", {}).get("text", ""),
                         "bullets": [re.sub(r"^[-*•]\s+", "", b.strip()) for b in bl],
                         "visual": (u["fields"].get("Visual", {}).get("text", "") + " " + " ".join(u["fields"].get("Visual", {}).get("lines", []))).strip()})
        print(json.dumps(dump, indent=2))
        return 0
    if not us:
        add("BLOCKING", "units", "no '### <n>. <claim title>' units under ## Content")

    doc_word_total = 0   # one-pager budget: matches render-doc.js's own word counter
    doc_weight_total = 0.0   # brief page estimate: see unit_weight/DOC_WEIGHT_PER_PAGE
    prev_pattern, run = None, 0
    # slide-patterns.yml's density and per-pattern limits size a projected slide (read in seconds,
    # at a distance); a document page is read up close, at leisure, and normally repeats a pattern
    # (two tables back to back is a fact, not monotony) — so a document gets more room, not the
    # slide's own numbers. WORD_SCALE/COUNT_SCALE are a deliberately rough multiple, not a modeled
    # page geometry; DOC_WEIGHT_PER_PAGE below is the same kind of estimate, calibrated against
    # real render-doc.js output, for the one check (brief length) a word-count proxy can't reach.
    WORD_SCALE, COUNT_SCALE = 2.5, 1.5
    limit_consec = int(pats["density"].get("consecutive_same_pattern_max", 2)) * (2 if is_doc else 1)
    for u in us:
        t = u["title"]
        f = u["fields"]
        pattern = f.get("Pattern", {}).get("text", "")
        if pattern != "appendix-sources" and not label_headings and (t.lower().strip(" .:") in LABEL_TITLES or words(t) < 3):
            add("BLOCKING", "title.claim", f"unit {u['n']} title is a label, not a claim: {t!r}", u["line"])
        if pattern != "appendix-sources":
            for msg in title_slop(t, slide=True, label_heading=label_headings):
                add("BLOCKING", "title.slop", f"unit {u['n']} title: {msg}", u["line"])
            if re.search(_COUNT_OF, t, re.I):
                add("BLOCKING", "title.count", f"unit {u['n']} title carries a count: {t!r}; the finding goes in the first sentence of the body", u["line"])
            if is_doc and re.fullmatch(_TITLE_CASE, t) and words(t) >= 4:
                add("BLOCKING", "title.case", f"unit {u['n']} heading is in Title Case: {t!r}; write it as a sentence", u["line"])
        for name in ("Pattern", "Body", "Visual", "Notes", "Sources"):
            if name not in f:
                add("BLOCKING", f"unit.{name.lower()}", f"unit {u['n']} has no **{name}** line", u["line"])
        if pats["patterns"] and pattern and pattern not in pats["patterns"]:
            add("BLOCKING", "pattern.unknown", f"unit {u['n']} pattern {pattern!r} not in slide-patterns.yml", u["line"])
        if pattern == prev_pattern:
            run += 1
        else:
            prev_pattern, run = pattern, 1
        if run > limit_consec:
            add("WARNING", "density.consecutive", f"unit {u['n']}: more than {limit_consec} consecutive {pattern!r} units", u["line"])
        vis = f.get("Visual", {})
        vtext = (vis.get("text", "") + " " + " ".join(vis.get("lines", []))).strip()
        if vtext.startswith("kind:"):
            cut = re.search(r"\.\s|\.$", vtext)
            prose = vtext[cut.end():].lstrip() if cut else ""
            if prose and (prose[0].islower() or prose[0] in ";|" or prose[0].isdigit() or " | " in prose):
                add("BLOCKING", "visual.spec", f"unit {u['n']} visual spec is cut at {vtext[max(0, cut.start() - 12):cut.start() + 1]!r}; "
                    "no period inside a field value (the spec ends at the first '. ')", vis.get("line"))
        if vis and (vtext.lower().strip(" .") in GENERIC_VISUALS or words(vtext) < 6):
            add("BLOCKING", "visual.generic", f"unit {u['n']} visual is not specified (say what it shows, its series, and source)", vis.get("line"))
        # An owner, a date, or a likelihood/impact grade on the page is a plan or a judgment; the source has to
        # state it, or the Assumptions section has to say it was inferred and why. The number check cannot see
        # "two weeks" or "medium / high", so this does.
        if vtext.startswith("kind:"):
            provenance = (sources_text + "\n" + secs.get("Assumptions and gaps", (0, ""))[1]).lower()
            for field in ("owners", "dates"):
                fm_ = re.search(rf"\b{field}:\s*([^|.]+)", vtext)
                if fm_:
                    for item in [x.strip() for x in fm_.group(1).split(";") if x.strip()]:
                        if item.lower() not in provenance:
                            add("BLOCKING", "visual.unsourced", f"unit {u['n']} names {field[:-1]} {item!r} that no Sources row or Assumptions entry states", vis.get("line"))
            if re.search(r"/\s*(?:low|medium|high)\s*/\s*(?:low|medium|high)\b", vtext, re.I) and not re.search(r"likelihood|impact|probabilit", provenance):
                add("BLOCKING", "visual.unsourced", f"unit {u['n']} grades likelihood and impact that no Sources row or Assumptions entry states", vis.get("line"))
        bodyf = f.get("Body", {})
        btext = "\n".join([bodyf.get("text", "")] + bodyf.get("lines", []))
        notes = f.get("Notes", {})
        ntext = "\n".join([notes.get("text", "")] + notes.get("lines", []))
        for label, txt, ln in (("body", btext, bodyf.get("line")), ("notes", ntext, notes.get("line")), ("title", t, u["line"])):
            for m in HELIX_VOCAB.finditer(txt):
                add("BLOCKING", "vocabulary", f"unit {u['n']} {label} uses HELIX vocabulary {m.group(0)!r}; move it to Sources", ln)
        for label, txt, ln in (("body", btext, bodyf.get("line")), ("title", t, u["line"])):
            for m in JARGON.finditer(txt):
                add("WARNING", "vocabulary.jargon", f"unit {u['n']} {label} uses {m.group(0)!r}, a term the audience would need defined", ln)
        bullets = ([bodyf["text"]] if bodyf.get("text") else []) + [l for l in bodyf.get("lines", []) if l.strip().startswith(("-", "*", "•"))]
        # every text shape the slide will carry gets the shape rules; the title and the shapes together get the
        # restatement check (a bullet that repeats a panel, a verdict that repeats the title)
        if pattern == "title" and is_doc:
            # on a brief or one-pager the title unit's Body is the rendered introduction, the most-read prose
            # on the page; it gets the shape rules (reversals, closers, dashes) like any bullet
            for sh in [re.sub(r"^[-*•]\s+", "", b.strip()) for b in bullets]:
                for msg in shape_slop(sh):
                    add("BLOCKING", "shape.slop", f"unit {u['n']} introduction {sh[:50]!r}: {msg}", bodyf.get("line"))
                if _NARRATION.search(sh):
                    add("BLOCKING", "shape.narration", f"unit {u['n']} introduction narrates the document: {sh[:50]!r}; open with the reader's situation", bodyf.get("line"))
        if pattern not in ("appendix-sources", "title"):
            bullet_shapes = [re.sub(r"^[-*•]\s+", "", b.strip()) for b in bullets]
            cells_ = visual_shapes(vtext)
            for sh in bullet_shapes:
                for msg in shape_slop(sh):
                    add("BLOCKING", "shape.slop", f"unit {u['n']} bullet {sh[:50]!r}: {msg}", bodyf.get("line"))
                if is_doc and _NARRATION.search(sh):
                    add("BLOCKING", "shape.narration", f"unit {u['n']} bullet narrates the document: {sh[:50]!r}; give the finding", bodyf.get("line"))
            for sh, node in cells_:
                for msg in (label_slop(sh, container=False) if node else shape_slop(sh)):
                    add("BLOCKING", "shape.slop", f"unit {u['n']} visual cell {sh[:50]!r}: {msg}", vis.get("line"))
            on_slide = [t] + (bullet_shapes if pattern in BODY_ON_SLIDE else []) + [c for c, _ in cells_]
            for later, earlier in restatements(on_slide):
                add("WARNING", "restatement", f"unit {u['n']}: {later[:50]!r} restates {earlier[:50]!r} on the same slide; keep one", bodyf.get("line"))
        if pattern != "title":   # the title unit's words land in the masthead, not a numbered page
            doc_word_total += words(t) + words(btext)
            vis_prose = vtext[re.search(r"\.\s|\.$", vtext).end():] if vtext.startswith("kind:") and re.search(r"\.\s|\.$", vtext) else (vtext if not vtext.startswith("kind:") else "")
            doc_word_total += words(vis_prose)
        if pattern != "appendix-sources":
            doc_weight_total += unit_weight(vtext, len(bullets))
        spec = pats["patterns"].get(pattern, {}).get("limits", {}) if pats["patterns"] else {}
        if spec:
            doc_note = " (page limit, scaled up from the slide limit in slide-patterns.yml)" if is_doc else ""
            bullets_max = spec["bullets"] * COUNT_SCALE if is_doc and "bullets" in spec else spec.get("bullets")
            if bullets_max is not None and len(bullets) > bullets_max:
                add("WARNING", "limits.bullets", f"unit {u['n']}: {len(bullets)} bullets, {pattern} allows {round(bullets_max)}{doc_note}", bodyf.get("line"))
            if "words_per_bullet" in spec:
                wpb_max = spec["words_per_bullet"] * WORD_SCALE if is_doc else spec["words_per_bullet"]
                for b in bullets:
                    if words(b) > wpb_max:
                        add("WARNING", "limits.words_per_bullet", f"unit {u['n']}: bullet over {round(wpb_max)} words{doc_note}: {b.strip()[:60]!r}", bodyf.get("line"))
            if "body_words" in spec:
                bw_max = spec["body_words"] * WORD_SCALE if is_doc else spec["body_words"]
                if words(btext) > bw_max:
                    add("WARNING", "limits.body_words", f"unit {u['n']}: body {words(btext)} words, {pattern} allows {round(bw_max)}{doc_note}", bodyf.get("line"))
            if "title_words" in spec and words(t) > spec["title_words"]:
                # a section heading, not a slide title: no document scaling — a claim heading stays
                # a claim heading no matter the kind, this limit is about label discipline, not room
                add("WARNING", "limits.title_words", f"unit {u['n']}: title over {spec['title_words']} words", u["line"])
        # numbers in body must appear in Sources
        for m in NUMBER.finditer(btext):
            num = m.group(0).strip().rstrip(",.")
            if re.fullmatch(r"\d", num):  # single digits are usually list counts
                continue
            if not re.search(rf"(?<![\w.]){re.escape(num)}(?![\w.])", sources_text):
                add("BLOCKING", "numbers.sourced", f"unit {u['n']}: figure {num!r} is not in the Sources table", bodyf.get("line"))
        # the same rule for the text a Visual spec puts on the page: cells, captions, verdicts; the spec's own
        # layout fields (columns: 1, highlight: 2, n: 3) are structure, not figures
        vcells = re.sub(r"\b(?:columns|highlight|n|cols|rows_max|width|size):\s*\d+", " ", vtext)
        for m in NUMBER.finditer(vcells):
            num = m.group(0).strip().rstrip(",.")
            if re.fullmatch(r"\d", num) or num in _HEADING_NUMBERS:
                continue
            if not re.search(rf"(?<![\w.]){re.escape(num)}(?![\w.])", sources_text):
                add("BLOCKING", "numbers.sourced", f"unit {u['n']}: figure {num!r} in the Visual spec is not in the Sources table", vis.get("line"))
        cited = set(re.findall(r"S\d+", f.get("Sources", {}).get("text", "")))
        for c in cited - source_ids:
            add("BLOCKING", "sources.dangling", f"unit {u['n']} cites {c} which is not in the Sources table", f["Sources"]["line"])
        if f.get("Sources") and not cited:
            add("BLOCKING", "sources.empty", f"unit {u['n']} cites no S<n> source", f["Sources"]["line"])

    # Whole-document budgets: a one-pager and a brief are read as a page, not projected as slides,
    # so the thing worth checking is the page itself, not per-unit slide limits. Both estimates are
    # approximate (word count for the one-pager, the same weight heuristic render-doc.js uses to lay
    # out a page for the brief) — a warning that says so, never a block, because the render-and-look
    # step in `actions/present.md` is the actual ground truth.
    if kind == "one-pager":
        title_m = re.search(r"^# (.+)$", body, re.M)
        doc_word_total += words(title_m.group(1)) if title_m else 0
        budget = int(doc_layout.get("max_words_one_pager", 450) or 450)
        if doc_word_total > budget:
            add("WARNING", "limits.one_pager_words",
                f"one-pager: {doc_word_total} words exceeds theme.yml's max_words_one_pager ({budget}); "
                "drop a unit rather than thin every bullet")
    # a brief has no page budget: it runs as many pages as its record needs (NFR-3)

    # horizontal logic: reading only the titles must tell the story, so each
    # title should share at least one content word with the one before it.
    story = [] if label_headings else [u for u in us if u["fields"].get("Pattern", {}).get("text") != "appendix-sources"]
    for prev, cur in zip(story, story[1:]):
        if not (content_words(prev["title"]) & content_words(cur["title"])):
            add("WARNING", "horizontal_logic",
                f"units {prev['n']} and {cur['n']}: titles share no content word; the titles-only read may not connect "
                f"({prev['title'][:40]!r} -> {cur['title'][:40]!r})", cur["line"])

    # Coverage: the Brief declares breadth and concept controls; the Story's
    # Concept coverage table accounts for every inventory group.
    brief = secs.get("Brief", (0, ""))[1]
    story = secs.get("Story", (0, ""))[1]
    def brief_field(name: str) -> str:
        m = re.search(r"^- \*\*" + re.escape(name) + r"\*\*:\s*(.*)$", brief, re.M)
        return m.group(1).strip() if m else ""
    breadth = brief_field("Breadth").lower()
    must_cover = [x.strip().lower() for x in re.split(r";", brief_field("Must cover")) if x.strip() and x.strip().lower() != "none"]
    must_omit = [x.strip().lower() for x in re.split(r";", brief_field("Must omit")) if x.strip() and x.strip().lower() != "none"]
    if breadth and breadth not in ("survey", "deep-dive"):
        add("BLOCKING", "coverage.breadth", f"Breadth must be survey or deep-dive, not {breadth!r}")
    if not breadth:
        add("BLOCKING", "coverage.breadth", "Brief has no **Breadth** line; breadth is a declared choice")
    cov_start = story.find("**Concept coverage**")
    rows = []
    if cov_start == -1:
        add("BLOCKING", "coverage.table", "Story has no **Concept coverage** table; every inventory group must be marked covered or omitted")
    else:
        for line in story[cov_start:].splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 5 and cells[0].isdigit():
                rows.append({"group": cells[1], "status": cells[3].lower(), "note": cells[4]})
        if not rows:
            add("BLOCKING", "coverage.table", "Concept coverage table has no rows")
        for r in rows:
            if r["status"] not in ("covered", "omitted"):
                add("BLOCKING", "coverage.status", f"concept group {r['group']!r} has status {r['status']!r}; use covered or omitted")
            elif r["status"] == "omitted" and words(r["note"]) < 3:
                add("BLOCKING", "coverage.reason", f"concept group {r['group']!r} is omitted without a reason")
        covered = [r["group"].lower() for r in rows if r["status"] == "covered"]
        if breadth == "survey" and rows and len(covered) < 5:
            add("BLOCKING", "coverage.survey", f"a survey covers at least five concept groups; {len(covered)} covered")
        for mc in must_cover:
            if not any(content_words(mc) & content_words(g) for g in covered):
                add("BLOCKING", "coverage.must_cover", f"must-cover concept {mc!r} shares no content word with any covered group")
    if must_omit:
        for u in us:
            hay = (u["title"] + " " + "\n".join([u["fields"].get("Body", {}).get("text", "")] + u["fields"].get("Body", {}).get("lines", []))).lower()
            for mo in must_omit:
                mo_words = content_words(mo)
                if mo in hay or (len(mo_words) >= 2 and len(mo_words & content_words(hay)) >= max(2, (len(mo_words) + 1) // 2) and len(mo_words) <= 4):
                    add("BLOCKING", "coverage.must_omit", f"unit {u['n']} mentions must-omit concept {mo!r}", u["line"])

    if kind == "deck" and us:
        first = us[0]["fields"].get("Pattern", {}).get("text")
        if first != "title":
            add("BLOCKING", "deck.order", "first unit of a deck must use the 'title' pattern", us[0]["line"])
        tail = [u["fields"].get("Pattern", {}).get("text") for u in us[-2:]]
        if ask_required and tail != ["ask-next-steps", "appendix-sources"]:
            add("BLOCKING", "deck.order", "a deck ends with 'ask-next-steps' then 'appendix-sources'", us[-1]["line"])
        elif not ask_required and tail[-1:] != ["appendix-sources"]:
            add("BLOCKING", "deck.order", "a deck ends with 'appendix-sources'", us[-1]["line"])
        content_units = [u for u in us if u["fields"].get("Pattern", {}).get("text") not in ("title", "agenda", "section-divider", "appendix-sources")]
        if len(content_units) > 12:
            add("WARNING", "deck.length", f"{len(content_units)} content slides; more than 12 needs an explicit exception in Brief")

    render = secs.get("Render", (0, ""))[1]
    if "Render" in secs:
        if "inspected" not in render.lower():
            # a warning, not a block: a host without the render toolchain still ships the script, and the Render
            # section then says which targets were not produced and why (meta.yml carries the same severity)
            add("WARNING", "render.inspected", "Render section does not record that every slide was rendered to an image and inspected; "
                "if the host lacks the render toolchain, say which targets were not produced and why")
        if not re.search(r"\.(pptx|html|pdf|docx)\b", render):
            add("BLOCKING", "render.targets", "Render section lists no rendered target path")
    exports = (ddx.get("authoring", {}) or {}).get("export") if isinstance(ddx, dict) else None
    if not exports:
        add("WARNING", "frontmatter.export", "ddx.authoring.export lists no rendered files")

    return report(findings, args.format, path)


def report(findings: list[dict], fmt: str, path: Path) -> int:
    blocking = sum(1 for f in findings if f["severity"] == "BLOCKING")
    warning = sum(1 for f in findings if f["severity"] == "WARNING")
    if fmt == "json":
        print(json.dumps({"script": str(path), "findings": findings,
                          "summary": {"blocking": blocking, "warning": warning}}, indent=2))
    else:
        for f in findings:
            loc = f"  [line {f['line']}]" if f.get("line") else ""
            print(f"{f['severity']:<9} {f['check']:<24} {f['message']}{loc}")
        status = "FAIL" if blocking else "OK"
        print(f"{status}: {path} blocking={blocking} warning={warning}")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
