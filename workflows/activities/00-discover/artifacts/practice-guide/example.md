---
ddx:
  id: practice-guide-continuous-integration
  type: practice-guide
  authoring:
    home: repo
---

# Continuous Integration

Continuous integration is the practice of building and testing every change
automatically and merging work into the shared codebase in small pieces.
A team that works this way finds conflicts and faults within minutes of
introducing them.

## The problem

Software written by several people has to be combined, and combining it gets
harder as the amount of change grows. Consider three
developers who each spend three weeks on a separate feature, working on
their own copies of the code. Each feature works when tested alone.

When the three are merged, the application fails in ways none of the
developers observed, because each feature was written against code the
others have since changed. Resolving the conflicts takes a further week and
the release date slips. The developers did competent work. The cost came from
merging late, when the differences were large and the deadline was near.

## How it works

Continuous integration has three parts. First, every change a developer
submits is built and tested automatically by a build service, so that a fault
is reported within minutes. Second, work in progress is kept up to date. The latest shared code is merged
into each open change regularly and the change is tested again, so that it is
always checked against what the rest of your team has done. Third, your team
keeps changes small and short-lived. It tracks how long each change stays open
and how large it is, with the aim of merging work within days.

The term is sometimes used more narrowly, for teams in which every developer
merges into the shared code at least once a day. That is the same practice
taken further, and teams generally gain more the closer they get to it.

## Benefits

Merging becomes routine. A day's work merges with few conflicts, and those
that occur are easy to resolve because the code involved is small and recent.
Faults are also cheaper to fix. When a test fails a few minutes after a small
change, the cause is almost certainly in that change, whereas a failure after
a large merge could come from anywhere in it.

Small changes improve code review as well. A reviewer can read a short change
carefully and respond the same day, while long changes tend to wait and then
receive a superficial review. Because the shared code always builds and
passes its tests, there is always a version that can be demonstrated, tested
or released.

## Getting started

1. Automate the build so that a single command produces the application from
   a clean copy of the code.
2. Run the build and tests on every change, using the build service provided
   by the code host, and display the result alongside the change under
   review.
3. Write automated tests, beginning with the most important behavior, and add
   tests with each new piece of work.
4. Prevent a change from being merged until it passes against the latest
   shared code.
5. When the shared build fails, fix it or revert the change responsible
   before doing other work.
6. Record how long changes stay open and how large they are, set a target
   for each, and review the figures every few weeks.

## Reference setup

The setup has four parts. The code is kept in a hosted repository with one
shared branch that represents the current state of the product. A build
service, which runs the build and tests for each change and reports the
result, is connected to that repository. The instructions for the build are a
file stored in the repository alongside the code, so that they are reviewed
and versioned like everything else. The shared branch is protected, so that a
change cannot join it until the build service reports success.

GitHub Actions, GitLab CI and Azure Pipelines are the common build services,
and each is part of the corresponding code hosting product. If you already
host your code with one of them, you have the service available. If you have
several applications, keep a standard build definition that new projects
copy, so that each one starts with the practice in place.

## Deployment

Builds can run on machines provided by the vendor or on your own. In either case the build service needs credentials for the systems it
deploys to, which makes it a security-sensitive system. It should be given the minimum access
it needs. Secrets should be held in its protected store and kept out of the
code, and the right to change build definitions should be limited.

Build speed determines whether the practice holds, because developers stop
waiting for results that take an hour. The main build should finish in about
ten minutes, with slower tests run in parallel or moved to a later stage.

The package produced by the build should be numbered and used unchanged for
testing and release, so that what is released is what was tested. Feature
flags, which are switches that hide unfinished functionality from users,
allow incomplete work to be merged without being released.

## Views

### Risk & Compliance

Every change is tested and recorded before it is merged, which provides
evidence of control over what reaches production. The build service holds
credentials and needs the same access controls as production systems.

### Finance

The build service is often included with code hosting. The main cost is
developer time spent writing and maintaining automated tests.

### IT Operations

Operations runs the build service and manages its credentials and capacity.
The practice depends on the build being fast and reliable.

### Apps Dev

Developers write tests alongside code, divide work into small changes, and
repair a broken build before continuing other work. Merging and review take
less time as a result.

## Questions for your team

- What happens automatically when a developer submits a change?
- How long does that take to report back?
- Can a change that fails its tests reach the shared code?
- How long does a typical change stay open, and how large is it?
- When the build last broke, how long did it take to fix?

## Common mistakes

The most common failure is to install the build service without changing how
your team works. If builds run on every change but changes still stay open for
weeks, the work is not being integrated and the benefits do not appear. Slow
builds have a similar effect, because developers stop waiting for the result.

A build that is left failing teaches your team to disregard it, so a failure
should be fixed, or the change responsible reverted, straight away. Two
further problems are a test suite that covers too little, which makes a
passing build misleading, and large changes, which wait longest to be reviewed
and are the hardest to merge.
