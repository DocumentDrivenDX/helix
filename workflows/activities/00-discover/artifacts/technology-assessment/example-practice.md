---
ddx:
  id: TA-009
  type: technology-assessment
  scope: practice
  authoring:
    home: repo
---

# TA-009: Continuous integration for web applications

## Summary

When several developers work on one application, their changes have to be combined, and combining them late is
slow and unpredictable [1]. Continuous integration is the practice of building and testing every change
automatically and merging work into the shared code in small pieces [1][2]. It suits any web
application with more than one developer.

Continuous integration lowers two risks. The first is a long, uncertain merge just before a release, when time
is shortest [1]. The second is a fault that hides for weeks. When a test fails minutes after a small change,
the cause is in that change [1][2].

Two things remain yours to manage. The practice depends on automated tests, which your developers have to
write and keep up to date [1][3]. It also asks them to split large pieces of work into small steps, which takes
practice and can make a large feature feel slower to finish [2].

Cost supports the case and should not drive it. The service that runs the builds usually comes with the code
hosting you already have. What you spend is developer time on tests, which the accounts cited argue is repaid in
merges and reviews that take less time [1].

We mean more by the term than a build that runs on every change. Keep each piece of work current with the
shared code, and work to shorten how long a change stays open and how large it is.

## Scope

This paper is for technology leaders whose teams build a web application together. It applies from the first
week that two developers share a codebase.

It examines continuous integration as a way of working: how changes are built, tested and merged. It names
build services as examples and advises on none of them. Continuous delivery, which takes each passing change on
to release, is the next step and has its own considerations. The facts are as published on November 12, 2026.

## Where to Start

| Reader | Start with |
|--------|------------|
| The sponsor of the decision | Executive summary, then Continuous integration in practice |
| Finance and procurement | Cost and commitment |
| Security, risk and compliance | Security and compliance |
| Infrastructure and operations | Running it, then Operational considerations |
| Engineering leads and architects | Building on it, then Common questions |

## Continuous integration in practice

Software written by several people has to be combined, and combining it gets harder as the amount of change
grows. Consider three developers who each spend three weeks on a separate feature. Each feature works when
tested alone. When the three are merged, the application fails in ways none of them saw, because each was
written against code the others have since changed [1].

Continuous integration has three parts. Every change a developer submits is built and tested automatically,
so a fault is reported within minutes [1][2]. Work in progress is kept current: the latest shared code is
merged into each open change and the change is tested again. Changes are kept small and short-lived, so that
work joins the shared code within days.

Some people reserve the name for teams in which every developer merges into the shared code at least once a
day [1][2]. That is the same practice taken further, and teams gain more the closer they get to it [1].

**Where to begin**

1. Automate the build, so that one command produces the application from a clean copy of the code [1][2].
2. Run the build and the tests on every change, and show the result where the change is reviewed [2].
3. Write automated tests, starting with the behavior that matters most, and add tests with each new piece of
   work [2].
4. Block merging on failure, so that a change joins the shared code only after it passes against the latest
   version.
5. When the shared build breaks, fix it or undo the change that broke it before other work continues [1][2].
6. Record how long changes stay open and how large they are. Agree a target for each and review the numbers
   every few weeks.

The most common failure is to install a build service and change nothing else. If builds run on every change
but changes still stay open for weeks, nothing has been integrated and the benefits do not appear [1][2]. In a
study of 1,270 open-source projects that used a build service, about 60% committed infrequently [4].

## Findings

### Cost and commitment

Continuous integration has no license of its own and does not depend on an expensive tool [1]. Build services
such as GitHub Actions, GitLab CI and Azure Pipelines come with their code hosting products.

What you commit is developer time. Setting up the build takes effort, and so does writing and maintaining the
automated tests [3]. Developers also have to split large changes into small steps, and a large feature can
take longer to finish that way [2]. We found no published figure for the cost of adopting the practice.

The return is argued more than it is measured. The fullest account of the practice says its author has seen
no serious study of the time teams spend integrating, and relies on experience [1]. DORA reports that teams
perform better when developers merge into the shared code at least daily, and attributes that to its 2015
State of DevOps Report [2].

### Security and compliance

Every change is built, tested and logged before it joins the shared code, which leaves a log of what
reached production and when.

The build service is itself a system to protect. It handles source code, credentials and the packages you
deploy, so a compromised build can affect everything downstream [3]. Give it the least access it needs, keep
secrets in its protected store, and limit who may change the build's instructions [3].

Some assurance regimes for safety-critical software require documentation and review that are hard to fit
into frequent merges [3]. If one applies to you, plan the review step with your assurance team before you
adopt the practice.

### Running it

There is little to run. The build service builds and tests each change and shows the result to the whole team
[1][2]. Show results where the change is reviewed and in the team's chat, because emailed results are ignored
[2].

Speed decides whether the practice holds. Aim for a result in about ten minutes, and move slower tests to a
later stage [1][2]. In the study of open-source projects, most builds finished within ten minutes [4].

A broken build is urgent. A build that stays broken teaches the team to ignore it. In the same study, 85% of
projects had at least one broken build that took more than four days to fix [4].

### Building on it

Your developers do three things differently. They write automated tests with their code, they split work into
steps small enough to merge within days, and they keep unfinished work current with the shared code [1][2].

Tests are the foundation. Without them a passing build says only that the code compiles, and the team has no
way to screen out faults [1]. Start with the behavior that matters most, then cover each new piece of work as
it is written [2].

Review before merging is the usual reason a change stays open. It can add hours or days, which is the delay
the practice exists to remove [1]. A reviewer can read a small change the same day, and pairing shortens the
wait further [1].

### Operational considerations

The setup has four parts. Keep the code in a hosted repository with one shared branch that holds the current
state of the product [1]. Connect a build service that builds and tests every change [1][2]. Store the build's
instructions in the repository beside the code, so that they are reviewed and versioned like everything else
[2]. Protect the shared branch, so that a change joins it only after its build passes against the latest code.

The package the build produces should be numbered and used unchanged for testing and release, so that what you
release is what you tested [2].

If you have several applications, keep a standard set of build instructions that new projects copy. Each one
then starts with the practice in place.

### Common questions

| Question | Answer |
|----------|--------|
| We already run a build on every branch. Is that continuous integration? | It is half of it. Until work is merged nobody else can see it, and branches still drift apart [1] |
| Do we have to merge every day? | Daily merging is the stricter form. Start by halving how long a change stays open [1][2] |
| What does it cost? | Developer time for tests and for working in smaller steps. The build service usually comes with your code hosting [2][3] |
| How fast should the build be? | About ten minutes for the main build, with slower tests in a later stage [1][2] |
| What do we do when the build breaks? | Fix it, or undo the change that broke it, before other work continues [1][2] |
| Does it replace code review? | No. Small changes make review quicker and more careful [1] |

### When continuous integration is not the right choice

Continuous integration suits a team working together on one product. Two situations call for something less.

The first is a project with one or two part-time maintainers and many outside contributors. Its maintainers
cannot know when contributions will arrive or to what standard, so longer-lived changes and review before
merging are the workable course [1]. Build and test every contribution, and keep each one small.

The second is a team with no automated tests yet. Merging often without tests lets faults through, because
nothing screens them out [1]. Write tests for the most important behavior first, then raise how often you
merge.

## Contradictions and Gaps

| Question | What is known | How to settle it |
|----------|---------------|------------------|
| Does a build on every branch count as continuous integration? | Two accounts require merging into the shared code at least daily; an encyclopedia describes a build on each change or on a schedule [1][2][3] | Agree your own definition and measure against it |
| How much does the practice improve delivery? | DORA attributes one finding to its 2015 report, and the fullest account relies on experience [1][2] | Read the 2015 State of DevOps Report |
| Do smaller, shorter-lived changes lower the number of defects? | We found no study that measures the size of a change or how long it stays open | Measure your own changes and defects over a quarter |
| Do the study's findings hold outside open source? | Its sample is open-source projects on one build service [4] | Read the full study |

## Sources

1. [Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html), Martin Fowler, January 18, 2024. Read November 12, 2026.
2. [Continuous integration](https://dora.dev/capabilities/continuous-integration/), DORA. Read November 12, 2026.
3. [Continuous integration](https://en.wikipedia.org/wiki/Continuous_integration), Wikipedia, revision of November 9, 2026. Read November 12, 2026.
4. [Continuous Integration Theater](https://arxiv.org/abs/1907.01602), Felidré, Furtado, da Costa, Cartaxo and Pinto, July 2, 2019. Abstract read November 12, 2026.
