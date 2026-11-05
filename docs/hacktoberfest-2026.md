# Hacktoberfest 2026: reusable core, adaptable entries

Planning snapshot: September 29, 2026. Dates below use America/Toronto (EDT)
unless explicitly labeled UTC. Recheck official pages when a prompt launches.

## Purpose and event boundary

The primary deliverable is a public portfolio project: an MIT-licensed,
installable agent skill with executable examples, tests, and a clear account
of its limitations. It aligns with the event's open-source AI theme through
reusable agent instructions and a deterministic helper. It does not train,
fine-tune, or bundle an open-weight model.

Hacktoberfest runs throughout October and is managed by MLH and DEV with
DigitalOcean. Pull requests and merge requests do not count toward rewards.
Reward progress depends on the participant dashboard and listed activities;
a public repository or build log alone does not establish completion.
See the [official FAQ](https://hacktoberfest.com/questions/) and
[activities page](https://hacktoberfest.com/activities/).

## Sequence

| Stage | When | Deliverable or decision |
| --- | --- | --- |
| Repository skeleton | Before October 1 | Public repository, MIT license, English README, installable `SKILL.md`. |
| Reusable core | Before selecting a challenge | Synthetic runnable examples, meaningful automated tests, offline verification, CI configuration. |
| Build-log draft | After core checks pass | Problem, design decisions, architecture, testing, lessons, and research limitations. |
| Dashboard mapping | From October 1 | Record exact activity requirements and evidence in `submissions/challenge-map.md`. |
| DEV weekend review | October 1, 10 p.m. EDT / October 2, 02:00 UTC | Read the published prompt and rules; decide whether this project fits before adapting the article. |
| DEV Week 1 review | October 5 | Recheck prompt, eligibility, dates, required tools, tags, and submission template. |
| Global Hack Week review | October 9, noon EDT | Read actual challenges and select a fitting extension or demonstration. |
| Submission | Each published deadline | Use the required platform and verify that it recorded the entry. |

The [DEV weekend page](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01)
lists a deadline of October 5 at 2:59 a.m. EDT (06:59 UTC). Its prompt is
revealed at launch. The [Week 1 page](https://dev.to/challenges/hacktoberfest-week1-2026-10-05)
currently lists October 5–11; a precise closing time must be rechecked.
[Global Hack Week](https://events.mlh.com/events/14553-global-hack-week-open-source)
runs October 9 at noon through October 15 at 1 p.m. EDT. An individual
challenge may use a different deadline.

## Keep the core reusable

The skill folder holds platform-independent rules and a standard-library
helper. `examples/` supplies reusable synthetic cases. `docs/` contains the
portfolio narrative. `submissions/` holds event-specific requirements and
entry drafts. If a prompt requires a new integration, place its adapter in a
separate `integrations/<tool>/` folder with documented optional dependencies,
synthetic inputs, and its own tests. Add such a folder only when a real prompt
justifies it. Do not rewrite the core merely to match event wording.

Possible adaptations, conditional on actual rules:

- A skills challenge: demonstrate installation and a complete structured audit.
- An open-source agent challenge: add a small caller that passes explicit
  evidence to the helper and presents the result for review.
- An open-weight model challenge: add an optional extraction adapter and
  evaluate classification separately from deterministic rule execution.
- A writing challenge: adapt the build log to its exact prompt and template.

These are options, not planned claims. If a challenge requires a trained
model, a specific tool, or work created within its entry period, assess the
cost and eligibility honestly. An existing project may be ineligible;
record the pre-event baseline and any work completed during the challenge.

## Submission workflow

1. Read the live official prompt, rules, entry template, required tags, and
   deadline. Record the URL, timezone, existing-work policy, and requirements.
2. Map each requirement to a concrete file, demo, or evidence link. Leave
   uncertain requirements pending; do not infer eligibility from theme fit.
3. Choose the smallest useful extension. Keep core tests passing and record
   the baseline commit and challenge-period changes.
4. Adapt the article using `submissions/entry-template.md`. Add required
   sections and tags only after they are published.
5. Submit through DEV or MLH as instructed, then record the entry URL and
   dashboard confirmation separately from the code's test status.

No accounts have been registered, articles published, or entries submitted
by this packaging task. This plan creates no automatic monitoring or
scheduled reminders. Reward and challenge status remain pending until the
participant completes the required activities and verifies them.
