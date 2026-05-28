---
title: Who it's for
weight: 4
---

HELIX is built for a specific shape of work. It rewards some teams and
overburdens others. Knowing which side you're on saves time.

## You should use HELIX if

**You're using AI agents on non-trivial software work.** HELIX is
designed for the case where agents are real participants in the work — not
autocomplete inside an IDE, but agents that need durable intent, clear
authority, and structured context before they change software. If you have
ever watched an agent loop without making progress because it was
re-deriving requirements from existing code, HELIX is for you.

**Your project has more than one person — or more than one agent — over
time.** Knowledge that lives in one head doesn't survive turnover. HELIX's
artifact graph keeps intent durable across humans rotating in and out and
across model upgrades that make the previous agent obsolete.

**You care about coherence as the project grows.** Some projects can run
on memory and momentum until they ship. Others need to stay aligned across
months or years of incremental change. HELIX is built for the second case
— it pays a small upfront tax in artifacts to prevent the much larger tax
of drift.

**You want supervised autonomy, not full autonomy.** HELIX helps humans
decide what should be true, helps agents work from that shared context, and
helps reviewers detect drift. It is not a promise that a runtime can run
forever without judgment. Explicit human decision points are part of the
methodology.

**You want a portable method instead of a platform bet.** HELIX separates
the artifact graph and alignment practices from the execution surface. You
can apply the same methodology through DDx, Databricks Genie, Claude Code,
or another platform as long as the runtime can consume the artifacts and
respect the authority order.

**You think in documents.** HELIX assumes that writing down intent, in a
form your collaborators can read and amend, is worth doing. Teams that
treat documentation as a chore will fight the system. Teams that treat
documentation as engineering will find HELIX is mostly already how they
think.

## You should not use HELIX if

**You're writing a one-off script.** A scratch utility doesn't need an
artifact graph. The smallest sufficient action is to write the script.

**You're prototyping a new idea where coherence doesn't matter yet.**
Throwaway prototypes are throwaway by design. HELIX optimizes for
projects that need to stay coherent past the first ship; it doesn't
optimize for projects you intend to throw away.

**You don't use AI agents and don't want the artifact discipline.** A team
writing all of its own code can still benefit from HELIX's artifact types,
authority order, and alignment checks. But if you do not need durable
machine-readable context and do not want to maintain it, the method will
feel heavier than the problem requires.

**You need to ship in a strictly regulated environment where AI cannot
write code.** Some industries forbid the very pattern HELIX is built
around. The framework is honest about being designed for AI-assisted
work; it does not retrofit cleanly to environments that cannot accept
that.

**You want a task runner more than a methodology.** HELIX does not replace
your platform, issue tracker, CI system, or deployment runtime. It gives
those tools a coherent artifact spine to work from. If your main need is
queue execution or automation plumbing, choose a runtime first and treat
HELIX as optional governance around it.

## What you give up to use it

HELIX has costs. Every team adopting it pays:

- **Up-front artifact discipline.** A one-paragraph idea won't run; you
  need at least a vision, a requirements outline, and a first feature
  spec before agents have enough authority to make non-trivial changes.
  For small projects this can feel heavy.
- **Authority discipline.** Teams must agree which artifacts govern which
  decisions, how conflicts are resolved, and when changes need to propagate
  through the graph.
- **Platform discipline.** You still need to choose where execution happens:
  DDx, Databricks Genie, Claude Code, or another runtime. HELIX does not
  hide that decision; it keeps the methodology portable across it.
- **Document maintenance.** Artifacts drift. Cross-cutting concerns
  evolve. Specs need amendments. HELIX's alignment practice helps you find
  the drift, but the work of resolving it is real.

In return, you get a system where AI agents do meaningful work without
losing the plot, where institutional knowledge survives turnover, and
where the next change is easy to make because the last change was
properly recorded. Whether that trade is worth it depends on the project.

If you're not sure, the cheapest experiment is to try HELIX on a single
non-trivial feature. The framework is designed to be adopted incrementally
— start by learning the [Methodology](/use/workflow/methodology/), browsing
the [Artifact Types](/artifact-types/), then applying the smallest useful
artifact graph to one feature.
