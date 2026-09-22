---
title: "Anti-slop rules"
weight: 5
generated: true
description: "Every deterministic rule the deliverable gate, the prose lint, and the visual gate enforce, generated from the scripts that enforce them."
---

This page is generated from the code that enforces the rules, so it cannot drift from them: `skills/helix/scripts/check-deliverable.py` (the script gate), the vendored sloptimizer fixture, `workflows/deliverables/slide-patterns.yml` (limits), the Vale styles under `.vale/styles/Helix`, `skills/helix/scripts/deck-qa.py` (the visual gate), and `skills/helix/scripts/render-deck.js`. The narrative on [Anti-slop](../../use/anti-slop/) says why each rule exists and how the passes are sequenced.

Severities: **blocking** stops the deliverable at the gate; **warning** is reported and left to judgment. Every title check is a suggestion in sloptimizer and a block here, because a deck title is read aloud in sequence and cannot carry a footnote.

## Title and shape rules

Titles run through every rule marked *title*; a deck title is a slide title for an audience outside the team, so the *slide title* rules apply too. Bullets, card labels, captions, and verdicts run through the *shape* rules. Titles fail above 10 words and aim for 8 or fewer.

| Rule | Applies to | Trigger | Flagged example (from the upstream fixture) |
| --- | --- | --- | --- |
| ContrastiveReversal (`contrastive reversal`) | title, shape | any of: `\b(?:(?:is|are|was|were|do|does|did|has|have|had|will|can|could|should)\s+not|(?:isn|aren|wasn|weren|doesn|don|hasn|haven)(?:'|’)t)\s*[.!]?$`; `,\s*not\s+(?:a|an|the|your|our|their|just|only|merely|simply|because)\b`; `^not\s+(?:a|an|the|just|only|because)\b`; `\bnot\s+[^,;.]{1,40}?,?\s+but\s+\w`; `\b(?:isn(?:'|’)t|aren(?:'|’)t|is not|are not|doesn(?:'|’)t|don(?:'|’)t)\b[^,;.]{1,60}[,;.]\s*(?:it(?:'|’)s|it is|they(?:'|’)re|they are|but)\b`; `^(?:less|fewer|more)\b[^,]{1,40},\s*(?:less|fewer|more)\b` | `AI-assisted development is now the default, and the practice behind it is not` |
| ColonList (`colon list`) | title | `(?<!\d):(?!\d|//)` followed by two or more items split on commas or `and`/`or` (clock times, ratios, and URLs are exempt) | `Three failures repeat on every AI-assisted team: drift, local decisions, lost context` |
| ColonReveal (`colon reveal`) | title | the same colon followed by one item | `The best part: it learns` |
| ImperativeChain (`imperative chain`) | title | three or more clauses (split on `,` `;` `.`) that open with an imperative verb from the list below | `Write the brief, check alignment, plan the work, run it in your own factory` |
| Listicle (`listicle count`) | title | `(two|three|…|ten|\d+)` then up to two words then a listicle noun (list below) | `Five things change once the catalog and the alignment skill are in place` |
| StackedNegation (`stacked negation`) | title | two or more of `no|not|never|nothing|none|nor|without|n't` | `HELIX takes no runtime, no tracker, and no technology choice away from you` |
| Triplet (`rule-of-three list`) | title | `A, B, and C` where each item is one to four words (`or` too) | `HELIX takes no runtime, no tracker, and no technology choice away from you` |
| Flattery (`flattery`) | title, shape | any phrase in the flattery list below | `Your agents can ship with the discipline your best teams already use` |
| Aphorism (`pseudo-aphorism`) | title, shape | any phrase in the aphorism list below | `Documentation is the new code review` |
| UniversalClaim (`universal claim`) | title | a group noun opening the title followed by a behavior verb, or `every`/`all`/`any` plus a group noun (lists below) | `Three failures repeat on every AI-assisted team: drift, local decisions, lost context` |
| Mannered (`mannered phrase`) | title | any of the 43 mannered phrases below (the same list Vale applies to body prose upstream) | `Documentation earns its keep on every review` |
| InventoryCount (`inventory count`) | title | an inventory verb (list below), an optional `over`/`about`/`up to`, a count (digits or a number word), up to two words, then a plural noun | `HELIX answers with 53 document templates across a seven-activity loop` |
| Hedge (`hedge`) | title | `\b(?:also|(?<!not )just|simply|really|actually|basically|essentially|arguably|perhaps|maybe|somewhat|quite|very|truly|genuinely|literally|surprisingly|frankly|honestly|fairly|rather|pretty)\b` | `Every layer also yields documents people outside engineering read` |
| Length (`over-length`) | title | more than 10 words | `Your agents can ship with the discipline your best teams already use` |
| ContainerTitle (`container title`) | slide title, shape | four words or fewer, ending in a container noun (list below); off for headings inside a team's own documents | `Firm capabilities` |
| SelfJustifying (`self-justifying`) | slide title, shape | any of: `^how to read (?:this|the)\b`; `^how this (?:slide|page|view|diagram|map) (?:works|is organi[sz]ed|reads)\b`; `^what this (?:slide|page|deck|diagram|view|map) (?:shows|means|is saying|tells)\b`; `^reading (?:this|the) (?:slide|chart|diagram|map|table)\b`; `^(?:a )?note on (?:how to read|reading|method|methodology)\b`; `^(?:design |guiding |core |our )?principles? (?:served|applied|honou?red|met|addressed|upheld|in play)\b`; `^why (?:we|our|us|the \w+|this|it|that) (?:own|control|built|build|chose|choose|keep|hold|matter|matters|care|need|exist)`; `^why (?:this|it|that) (?:matters|is different|is hard|works)\b`; `^what (?:stays|remains|does ?n[o'’]t change|we (?:control|own|keep|hold|guarantee))\b`; `^(?:the |our |design )?rationale\b` | `Why we control it` |
| ShoutingLabel (`shouting label`) | title, shape | all caps with six or more letters and either four or more words (twelve or more letters) or two or more words opening with WHAT, WHY, HOW, WHERE, WHEN, or WHO | `WHAT EXISTS AND WHERE IT STANDS` |
| StatusJargon (`invented status`) | slide title | any of the 23 invented-status phrases below (case-insensitive) | `Working hypothesis` |
| Taxonomy (`taxonomy code`) | slide title | any of the 3 taxonomy-code shapes below | `Zone 6 capabilities` |
| Marketing (`marketing register`) | slide title | any of the 17 marketing-register phrases below (case-insensitive) | `Leverage the platform layer` |
| TrailingCommentary (`trailing commentary`) | shape | `[.!?]\s+(?:Built|Designed|Intended|Meant|Chosen|Included|Added|Kept|Positioned|Shown|Placed|Retained|Selected)\s+(?:as|to|because|for|here|so|since)\b|[.!?]\s+(?:Serves|Acts|Exists|Stands|Functions)\s+(?:as|to|because|so)\b|[.!?]\s+(?:This|It|That) (?:is|was) (?:the|our|a) (?:worked example|reference|proof point|test case|first step)\b` | `Verifies citations. Built as the worked example for moving a check between products.` |

Titles in the fixture that pass every rule:

- `Document discipline catches agent drift before review`
- `Most developers now ship agent-written code every day`
- `Agent code drifts from its specs and decisions`
- `HELIX traces every agent change to a governing document`
- `HELIX ships document templates and one alignment skill`
- `One alignment pass finds three affected specs before coding`
- `Alignment reviews audit documents instead of chat transcripts`
- `A healthy document set averages under 3 findings per run`
- `HELIX runs on the runtime and tracker you own`
- `Pilot HELIX on one project this quarter`
- `Approve the budget and name a recruiter by month end`
- `Year one costs $262,000 and breaks even in month 18`
- `The 10:30 standup moves to 9:00 on Mondays`
- `Q3 churn fell 12% after prebill review`
- `One typed table carries every transport`
- `Install from https://example.com/releases`
- `One alignment check found three drifted specs before coding`
- `Each document layer governs the next, from vision to code`
- `Use cases`
- `Five checks are built and one is in use`
- `Firm capabilities`
- `Overview`

## Phrase lists

Vendored from sloptimizer at commit `a269347`; `tests/validate-headline-sync.sh` fails when any list or the fixture differs from upstream.

### Mannered phrases (regular expressions)

- `\bearns? (?:its|their) keep\b`
- `\b(?:a|the|one) (?:dial|knob|lever) worth (?:turning|pulling)\b`
- `\b(?:dials|knobs|levers) (?:to|worth) (?:turn|pull|turning|pulling)\b`
- `\bpulls? (?:its|their|his|her) (?:own )?weight\b`
- `\bpunch(?:es)? above (?:its|their) weight\b`
- `\b(?:do|does|did|doing) (?:the|all the|most of the) heavy lifting\b`
- `\b(?:is|are|was|were) doing (?:a lot of|most of the|the real|all the) work\b`
- `\bmoves? the needle\b`
- `\blow-hanging fruit\b`
- `\btable stakes\b`
- `\bnorth star\b`
- `\bsilver bullet\b`
- `\bsecret sauce\b`
- `\bunder the hood\b`
- `\bdouble-edged sword\b`
- `\bcuts both ways\b`
- `\ba tale of two\b`
- `\bthe lion(?:'|’)s share\b`
- `\bboils? down to\b`
- `\bthe elephant in the room\b`
- `\bthe beating heart of\b`
- `\ba breath of fresh air\b`
- `\bthrough the lens of\b`
- `\bat the intersection of\b`
- `\bfirst-class citizen\b`
- `\bin lockstep\b`
- `\bwears? (?:two|many|several|multiple) hats\b`
- `\bpaints? a (?:clear |vivid |fuller |complete )?picture\b`
- `\bthe wheels (?:come|came|fall|fell) off\b`
- `\bload-bearing (?:assumption|claim|idea|sentence|word|phrase|question|decision|detail|premise|distinction)\b`
- `\bthe connective tissue (?:of|between)\b`
- `\bthe glue that holds\b`
- `\bthe plumbing (?:of|behind|underneath)\b`
- `\bthe scaffolding (?:of|for|around)\b`
- `\bthe engine (?:of|behind|driving)\b`
- `\bshine[sd]? a light on\b`
- `\bpeel(?:s|ing)? back the (?:layers|curtain|onion)\b`
- `\bthe tip of the iceberg\b`
- `\bthe missing piece of the puzzle\b`
- `\ba (?:seat|place) at the table\b`
- `\bat a crossroads\b`
- `\bthe (?:road|path) ahead\b`
- `\bfull circle\b`

### Invented status (regular expressions)

- `\bportability reference\b`
- `\brepresentative workload\b`
- `\bworking hypothesis\b`
- `\bproposed contract\b`
- `\bcandidate,? (?:scope open|tbd|pending)\b`
- `\bscope (?:open|tbd|to be (?:defined|determined))\b`
- `\bfit (?:unproven|tbd|unclear)\b`
- `\bnot (?:yet )?committed\b`
- `\bdirectionally (?:correct|right|aligned)\b`
- `\bunder (?:exploration|consideration|evaluation|investigation)\b`
- `\bin flight\b`
- `\bto be validated\b`
- `\bsubject to (?:validation|confirmation|alignment)\b`
- `\bpending (?:alignment|validation|confirmation|decision)\b`
- `\baspirational\b`
- `\bnascent\b`
- `\blighthouse (?:project|use case|customer|initiative)\b`
- `\bpathfinder\b`
- `\bexemplar\b`
- `\bstraw ?man\b`
- `\bnaming tbd\b`
- `\btbd\b`
- `\bwip\b`

### Internal taxonomy codes (regular expressions)

- `\b(?i:zone|plane|pillar|horizon|wave|workstream|swimlane|quadrant|lane|epic|theme)s? \d{1,2}\b`
- `\bP\d{1,2}(?:[ ,/]+P\d{1,2})+\b`
- `\b(?i:principle|pillar)s? P?\d{1,2}\b`

### Marketing register (regular expressions)

- `\bleverag(?:e|es|ed|ing)\b`
- `\bdifferentiat(?:ed|ing|or|ors)\b`
- `\bcommoditi[sz](?:e|es|ed|ing|ation)\b`
- `\bbest[- ]of[- ]breed\b`
- `\benterprise[- ]grade\b`
- `\bfuture[- ]proof(?:ed|ing)?\b`
- `\bturnkey\b`
- `\bholistic(?:ally)?\b`
- `\bfrictionless\b`
- `\bnext[- ]gen(?:eration)?\b`
- `\bsynerg(?:y|ies|istic)\b`
- `\bvalue[- ]add(?:ed)?\b`
- `\bmission[- ]critical\b`
- `\bstate[- ]of[- ]the[- ]art\b`
- `\b(?:universal|unified|seamless|delightful) experience\b`
- `\bsingle (?:pane|source) of (?:glass|truth)\b`
- `\bgoverned (?:conversational|data|ai) access\b`

### Flattery (regular expressions)

- `\byour best (?:teams?|people|engineers?|work|days?)\b`
- `\b(?:teams|people|leaders|companies) like yours?\b`
- `\bhold(?:s|ing)? (?:ourselves|yourself|yourselves|themselves) to\b`
- `\byou deserve\b`
- `\bthe (?:smartest|best|brightest) (?:teams|people|minds|engineers)\b`
- `\byou already (?:know|use|have|do|trust)\b`
- `\bworld[- ]class\b`
- `\bbest[- ]in[- ]class\b`
- `\bindustry[- ]leading\b`
- `\bthe (?:bar|standard) we (?:set|hold|keep)\b`

### Aphorism (regular expressions)

- `\bis the new\b`
- `\bthe only \w+ that matters\b`
- `\bis everything\b`
- `\bmore than ever\b`
- `\bdone right\b`
- `\bis (?:a|the) (?:feature|superpower|multiplier|moat|journey|mindset)\b`
- `\bis (?:a|an) (?:nice-to-have|luxury)\b`
- `\b(?:wins|matters|counts)\s*[.!]?$`
- `\bat scale\s*[.!]?$`
- `\bthe hard way\b`
- `\bchanges everything\b`
- `\bhere to stay\b`
- `\bthe future of\b`
- `\bwelcome to\b`
- `^that(?:'|’)?s what makes\b`
- `^that is what makes\b`
- `^(?:this|that) is (?:what|how|why) \w+ (?:works|matters|wins|scales|holds)\b`
- `\beverything else is (?:detail|plumbing|noise|downstream)\b`

### Container nouns

- `capabilit(?:y`
- `ies)`
- `foundations?`
- `layers?`
- `overview`
- `landscape`
- `ecosystem`
- `frameworks?`
- `pillars?`
- `principles`
- `considerations`
- `enablers`
- `building blocks`
- `components`
- `dimensions`
- `themes`
- `elements`
- `areas`
- `aspects`
- `fundamentals`
- `essentials`
- `basics`
- `highlights`
- `context`
- `background`
- `approach`
- `philosophy`
- `vision`
- `stack`
- `platform`
- `architecture`
- `framing`
- `scope`
- `summary`
- `agenda`
- `introduction`
- `recap`
- `takeaways`
- `learnings`
- `observations`
- `reflections`
- `opportunities`
- `challenges`
- `implications`
- `next steps`
- `key points`
- `the ask`
- `deep[- ]dive`
- `overview and context`

### Listicle nouns

- `things`
- `reasons`
- `ways`
- `lessons`
- `mistakes`
- `signs`
- `secrets`
- `tips`
- `takeaways`
- `truths`
- `myths`
- `ideas`
- `insights`
- `principles`
- `habits`
- `rules`
- `questions`
- `shifts`
- `changes`
- `factors`
- `points`
- `patterns`
- `steps`
- `keys`
- `pillars`
- `traps`

### Group nouns (universal claim)

- `teams?`
- `people`
- `leaders`
- `engineers`
- `developers`
- `companies`
- `organi[sz]ations`
- `customers`
- `users`
- `buyers`
- `founders`
- `executives`
- `managers`
- `businesses`
- `enterprises`
- `startups`

### Group verbs (universal claim)

- `switch`
- `win`
- `lose`
- `choose`
- `prefer`
- `want`
- `need`
- `trust`
- `buy`
- `adopt`
- `leave`
- `stay`
- `succeed`
- `fail`
- `care`
- `love`
- `hate`
- `ignore`
- `struggle`
- `expect`
- `demand`
- `know`
- `forget`
- `resist`
- `deserve`

### Inventory verbs

- `with`
- `has`
- `have`
- `had`
- `offers?`
- `ships?`
- `includes?`
- `provides?`
- `contains?`
- `routes?`
- `spans?`
- `across`
- `covers?`
- `supports?`
- `brings?`
- `delivers?`
- `packs?`
- `features?`
- `comes with`
- `made (?:up )?of`
- `consists? of`
- `bundles?`
- `holds?`
- `carries`
- `carry`
- `adds?`
- `lists?`
- `boasts?`
- `totals?`
- `comprises?`

### Number words counted as a count

- `\d[\d,]*`
- `a dozen`
- `dozens`
- `hundreds`
- `thousands`
- `(?:twenty`
- `thirty`
- `forty`
- `fifty`
- `sixty`
- `seventy`
- `eighty`
- `ninety)(?:-(?:one`
- `two`
- `three`
- `four`
- `five`
- `six`
- `seven`
- `eight`
- `nine))?`
- `eleven`
- `twelve`
- `thirteen`
- `fourteen`
- `fifteen`
- `sixteen`
- `seventeen`
- `eighteen`
- `nineteen`
- `two`
- `three`
- `four`
- `five`
- `six`
- `seven`
- `eight`
- `nine`
- `ten`

### Imperative verbs (imperative chain)

- `add`
- `adopt`
- `align`
- `ask`
- `audit`
- `build`
- `buy`
- `call`
- `check`
- `choose`
- `close`
- `commit`
- `configure`
- `count`
- `cut`
- `decide`
- `define`
- `deploy`
- `design`
- `document`
- `draft`
- `drive`
- `edit`
- `find`
- `fix`
- `follow`
- `frame`
- `get`
- `give`
- `go`
- `grow`
- `hire`
- `hold`
- `install`
- `join`
- `keep`
- `launch`
- `lead`
- `learn`
- `let`
- `list`
- `make`
- `map`
- `measure`
- `merge`
- `move`
- `name`
- `open`
- `own`
- `pick`
- `plan`
- `publish`
- `push`
- `put`
- `read`
- `release`
- `remove`
- `review`
- `run`
- `scale`
- `see`
- `sell`
- `send`
- `set`
- `share`
- `ship`
- `show`
- `sign`
- `start`
- `stop`
- `take`
- `tell`
- `test`
- `track`
- `train`
- `try`
- `turn`
- `use`
- `validate`
- `verify`
- `watch`
- `write`

## Restatement

Within one slide, the title and every shape the layout draws are compared pairwise on content words (lowercase words of three or more letters, minus 66 stopwords). Two units with at least 4 content words each whose Jaccard overlap is 0.5 or higher are a `restatement` (warning). Bullets count only on patterns whose layout draws them (agenda, ask-next-steps, claim-evidence, quote, section-divider, statement); node labels in a figure (center, columns, layers, left, milestones, right, steps and the first cell of items, risks, rows, spokes, stats) skip the container-title rule.

Stopwords: `a`, `all`, `an`, `and`, `any`, `are`, `as`, `at`, `be`, `been`, `being`, `but`, `by`, `can`, `did`, `do`, `does`, `each`, `every`, `for`, `from`, `had`, `has`, `have`, `he`, `her`, `his`, `how`, `if`, `in`, `into`, `is`, `it`, `its`, `no`, `not`, `of`, `on`, `one`, `or`, `our`, `she`, `so`, `than`, `that`, `the`, `their`, `then`, `these`, `they`, `this`, `those`, `three`, `to`, `two`, `was`, `we`, `were`, `what`, `when`, `which`, `who`, `will`, `with`, `you`, `your`

## Horizontal logic

Consecutive titles (title slide through the ask) must share at least one content word after light stemming: `-ing` is stripped from words over six letters, `-ed` over five, a trailing `-s` over four unless the word ends in `-ss` (`-es` after `s`, `x`, `z`, `ch`, `sh`), then a trailing `-e` over four letters; words under three letters and the title stopwords are ignored. A pair with no shared word is a `horizontal_logic` warning. The same stems decide whether a must-cover concept matches a covered group.

Title stopwords: `a`, `after`, `all`, `an`, `and`, `any`, `are`, `as`, `at`, `back`, `be`, `been`, `before`, `but`, `by`, `can`, `each`, `every`, `for`, `from`, `here`, `how`, `if`, `in`, `into`, `is`, `it`, `its`, `just`, `less`, `more`, `most`, `much`, `no`, `not`, `now`, `of`, `on`, `once`, `one`, `only`, `or`, `our`, `out`, `over`, `own`, `per`, `so`, `than`, `that`, `the`, `their`, `then`, `there`, `these`, `they`, `this`, `those`, `to`, `under`, `up`, `very`, `was`, `we`, `were`, `what`, `when`, `while`, `who`, `will`, `with`, `you`, `your`

## Script gate checks

Every check `check-deliverable.py` can report, with its severity. A title that is a label (`about us`, `agenda`, `appendix`, `background`, `conclusion`, `context`, `introduction`, `next steps`, `overview`, `problem`, `questions`, `recommendation`, `results`, `risks`, `roadmap`, `solution`, `sources`, `status`, `summary`, `team`, `thank you`, `timeline`, `update`) or under three words fails `title.claim`.

| Check | Severity | Message shape |
| --- | --- | --- |
| `coverage.breadth` | blocking | Breadth must be survey or deep-dive, not … |
| `coverage.must_cover` | blocking | must-cover concept … shares no content word with any covered group |
| `coverage.must_omit` | blocking | unit … mentions must-omit concept … |
| `coverage.reason` | blocking | concept group … is omitted without a reason |
| `coverage.status` | blocking | concept group … has status …; use covered or omitted |
| `coverage.survey` | blocking | a survey covers at least five concept groups; … covered |
| `coverage.table` | blocking | Story has no **Concept coverage** table; every inventory group must be marked covered or omitted |
| `deck.length` | warning | … content slides; more than 12 needs an explicit exception in Brief |
| `deck.order` | blocking | first unit of a deck must use the 'title' pattern |
| `density.consecutive` | warning | unit …: more than … consecutive … units |
| `frontmatter.export` | warning | ddx.authoring.export lists no rendered files |
| `horizontal_logic` | warning | units … and …: titles share no content word; the titles-only read may not connect |
| `limits.body_words` | warning | unit …: body … words, … allows …… |
| `limits.bullets` | warning | unit …: … bullets, … allows …… |
| `limits.one_pager_words` | warning | one-pager: … words exceeds theme.yml's max_words_one_pager (…); |
| `limits.title_words` | warning | unit …: title over … words |
| `limits.words_per_bullet` | warning | unit …: bullet over … words…: … |
| `numbers.sourced` | blocking | unit …: figure … is not in the Sources table |
| `pattern.unknown` | blocking | unit … pattern … not in slide-patterns.yml |
| `placeholder` | blocking | placeholder text … |
| `placeholder.bracket` | warning | bracketed phrase … looks like a template slot |
| `render.inspected` | warning | Render section does not record that every slide was rendered to an image and inspected; |
| `render.targets` | blocking | Render section lists no rendered target path |
| `restatement` | warning | unit …: … restates … on the same slide; keep one |
| `section` | blocking | missing '## …' |
| `shape.narration` | blocking | unit … introduction narrates the document: …; open with the reader's situation |
| `shape.slop` | blocking | unit … introduction …: … |
| `sources` | blocking | Sources table has no S<n> rows |
| `sources.dangling` | blocking | unit … cites … which is not in the Sources table |
| `sources.empty` | blocking | unit … cites no S<n> source |
| `title.case` | blocking | document title is in Title Case: …; write it as a sentence |
| `title.claim` | blocking | document title is a label, not a claim: … |
| `title.count` | blocking | document title carries a count: …; the finding goes in the introduction, the title names the subject |
| `title.slop` | blocking | document title: … |
| `units` | blocking | no '### <n>. <claim title>' units under ## Content |
| `visual.generic` | blocking | unit … visual is not specified (say what it shows, its series, and source) |
| `visual.spec` | blocking | unit … visual spec is cut at …; |
| `visual.unsourced` | blocking | unit … names … … that no Sources row or Assumptions entry states |
| `vocabulary` | blocking | unit … … uses HELIX vocabulary …; move it to Sources |
| `vocabulary.jargon` | warning | unit … … uses …, a term the audience would need defined |

Patterns the vocabulary, number, placeholder, and visual checks use:

- HELIX vocabulary (blocking in a title, body, or notes): `\b(?:FR|US|FEAT|ADR|TD|SD|TP|PRD|DEL|CONTRACT|WS)-\d+|\bbeads?\b|\bratchets?\b|\bwork items?\b|\bacceptance criteri(?:a|on)\b|\bAC\d+\b|\bartifact graph\b|\b(?:discover|frame|build|deploy|iterate) activity\b|\bddx\b|\bstoryboard beats?\b|\bflow beats?\b|\bcandidate-briefing\b|\bkeep_when_short\b`
- Jargon (warning): `\b(?:concerns?|stop triggers?|autonomy levels?|quality floors?|ratchets?|framing|[\w-]+ modes?|the record|the profile|spikes?|project artifacts?|sibling profiles?)\b`
- Placeholder (blocking): `\[NEEDS CLARIFICATION|\[TODO\]|\bTBD\b|\[Fill in\]|<placeholder>|\[\.\.\.\]`; bracketed phrase (warning): `(?<!\[)\[(?:[A-Z][a-z]+)(?:[ /][A-Za-z]+)*\](?!\()`
- A number in a body that must appear in the Sources table: `(?<![\w.])(?:\$?\d[\d,]*(?:\.\d+)?\s?(?:%|k|K|M|B|x)?)(?![\w.])` (single digits excepted)
- Generic visuals (blocking, with anything under six words): `chart`, `diagram`, `graph`, `image`, `n/a`, `none`, `photo`, `picture`, `screenshot`, `table`

## Pattern limits and density

From `workflows/deliverables/slide-patterns.yml`, the single owner of limits; exceeding one is a warning.

| Pattern | Limits |
| --- | --- |
| `title` | title_words 10, subtitle_words 18 |
| `agenda` | items 5, words_per_item 10 |
| `section-divider` | title_words 10, bridge_words 25 |
| `claim-evidence` | bullets 4, words_per_bullet 14, body_words 60 |
| `stat-callout` | stats 3, words_total 30 |
| `two-column-comparison` | rows 5, words_per_cell 12 |
| `table` | columns 6, rows 7, words_per_cell 8 |
| `timeline` | milestones 6, words_per_milestone 10 |
| `diagram` | parts 8, words_per_part 8, body_words 60 |
| `statement` | title_words 10, body_words 40 |
| `process-flow` | steps 5, words_per_step 8 |
| `quote` | quote_words 40 |
| `risk-matrix` | risks 6, words_per_mitigation 12 |
| `ask-next-steps` | steps 4, words_per_step 14 |
| `appendix-sources` | rows 20, words_per_row 20 |

Density: title_words_target 8; title_words_max 10; words_per_content_slide_max 60; words_per_bullet_max 14; bullets_per_slide_max 5; consecutive_same_pattern_max 2; stat_callouts_per_section_max 1; table_or_comparison_every_n_slides 3; diagram_or_statement_per_n_content_slides 10; content_slides_max 12; slides_per_minute_of_talk 0.5

## Prose lint (Vale, Helix styles)

Runs on the hand-authored site pages and on every deliverable script (`just lint-prose`). Errors block; warnings and suggestions are reported.

### Helix.AISlop

error; existence. Avoid '%s'. Name the concrete mechanism, artifact, result, or constraint instead.

Tokens (16): `\bdelve(?: into)?\b`, `\bleverage\b`, `\bseamless(?:ly)?\b`, `\brobust\b`, `\bpivotal\b`, `\bunderscores\b`, `\blandscape\b`, `\brealm\b`, `\butilize\b`, `\bgame[- ]changer\b`, `\bat its core\b`, `\bin conclusion\b`, `\bin summary\b`, `\bto summarize\b`, `\bunlock(?:s|ing)?\b`, `\bsupercharge(?:s|d)?\b`

### Helix.EmDash

error; existence. Avoid em dashes in prose. Use a comma, colon, parentheses, or a shorter sentence.

Tokens (1): `—`

### Helix.Hedges

warning; existence. Review '%s' — often a weak hedge. Keep only if it names a real contrast or limit.

Tokens (16): `\bjust\b`, `\bvery\b`, `\breally\b`, `\bquite\b`, `\bsimply\b`, `\bactually\b`, `\bbasically\b`, `\bliterally\b`, `\bessentially\b`, `\bgenerally\b`, `\busually\b`, `\boften\b`, `\bsomewhat\b`, `\brather\b`, `\bclearly\b`, `\bobviously\b`

### Helix.PassiveVoice

warning; existence. Passive voice: '%s'. Prefer active where the actor matters.

Tokens (2): `\b(?:am|is|are|was|were|be|been|being)\s+(?:\w+(?:ed|en))\b`, `\b(?:am|is|are|was|were|be|been|being)\s+(?:made|done|told|kept|known|taken|shown|seen|sent|put|set|left|read|paid|met|lost|hit|cut|bought|brought|caught|chosen|driven|fallen|forgotten|frozen|given|hidden|held|sold|spoken|stolen|swept|swung|thought|thrown|understood|won|worn|written|broken|built|burst|dealt|drawn|drunk|eaten|fed|felt|fought|found|forbidden|gotten|grown|heard|laid|laid|led|let|lit|paid|proven|risen|rung|run|said|seen|shaken|shed|shot|shrunk|shut|sung|sunk|spread|stood|stuck|sunk|sworn|taught|torn|told|trodden|undertaken|woken|wound)\b`

### Helix.SentenceLength

warning; existence. Long sentence (>30 words). Split or tighten if it does not earn the length.

Tokens (1): `[A-Z][^.!?\n]*?(?:\s+\S+){30,}[^.!?\n]*[.!?]`

### Helix.Tics

warning; existence. Avoid '%s' unless the sentence names the concrete contrast or consequence.

Tokens (7): `\bhonest(?:ly)?\b`, `\bto be honest\b`, `\binteresting(?:ly)?\b`, `\bwhat stands out\b`, `\b(?:it is|it's|that is|that's)\s+worth\b`, `\bworth\s+(?:noting|saying|flagging|mentioning|remembering|reading|checking|exploring)\b`, `\b(?:real|actual|genuine|true)\s+(?:answer|approach|architecture|behavior|boundary|constraint|contract|default|design|gate|intent|mechanism|methodology|problem|reason|result|source|spec|story|takeaway|test|truth|value|version|workflow)\b`

### Helix.Wordiness

warning; substitution. Tighten '%s' → '%s'.

Substitutions (36): `in order to → to`; `in order for → so`; `due to the fact that → because`; `the fact that → that`; `in the event that → if`; `at this point in time → now`; `with regard to → about`; `with respect to → about`; `in regards to → about`; `a number of → some`; `the majority of → most`; `on a daily basis → daily`; `on a weekly basis → weekly`; `on a monthly basis → monthly`; `make use of → use`; `makes use of → uses`; `in spite of → despite`; `prior to → before`; `subsequent to → after`; `in conjunction with → with`; `in addition to → besides`; `it should be noted that → (delete)`; `it is important to note that → (delete)`; `it is worth noting that → (delete)`; `please note that → (delete)`; `it is the case that → (delete)`; `as a matter of fact → (delete)`; `needless to say → (delete)`; `in essence → (delete)`; `for the purpose of → for`; `for the purposes of → for`; `in the process of → (delete)`; `has the ability to → can`; `have the ability to → can`; `is able to → can`; `are able to → can`

## Visual gate (deck-qa.py)

Reads every slide's shapes from the file. Safe margin 0.5 in; readable floor 12.0 pt; autofit may shrink to 0.75 of the nominal size before a fit that depends on it becomes blocking. It also notes any typeface the deck names that the host lacks, rasterizes every slide when LibreOffice and pdftoppm are present, and builds a contact sheet for inspection.

| Check | Severity | Message shape |
| --- | --- | --- |
| `off-slide` | blocking | … extends past the slide edge |
| `margin` | warning | … sits inside the …in margin |
| `text-autofit` | warning | … needs …in for …in; relies on autofit shrink |
| `text-autofit` | blocking | … needs …in for …in; autofit would shrink below … pt |
| `text-overflow` | blocking | … needs …in of height, has …in |
| `small-type` | warning | … uses … pt (floor …) |
| `table-overflow` | blocking | table at y=… grows to …in and crosses the bottom margin |
| `table-grows` | warning | table rows need …in, declared …in; rows below will shift |
| `text-collision` | blocking | … overlaps … |
| `text-crosses-shape` | warning | … crosses the edge of … |
| `line-crosses-text` | warning | line … passes through … |
| `repeated-layout` | warning | same layout signature as the previous slide |

## What the renderer refuses to hide

`render-deck.js` writes the file so it can be inspected, then reports these and exits non-zero (problems) or reports and exits normally (warnings):

- problem: unit …: '…' does not fit its box at …pt (autofit will shrink it below the floor)
- problem: unit …: … bullets do not fit at …pt
- problem: unit …: … table row(s) did not fit beside the bullets; use the table pattern
- problem: unit …: table row '…' is taller than the slide body and was clamped
- problem: unit …: the Visual spec was cut at a period inside a field value; fields after it were read as prose
- problem: unit …: … table row(s) did not fit in 4 slides and were dropped
- warning: unit …: the ask band has no 'ask:' field, so it repeats the title; give the band the decision in the room's terms
- problem: sources: … row(s) did not fit in 6 appendix slides and were dropped
