# Memory Applicability Guard

An open-source agent skill for reviewing whether a remembered fact should influence a current recommendation. It pairs concise agent instructions with a deterministic Python helper that checks explicit, structured inputs.

**Research-informed decision support only; not production validated.**

A memory can be relevant and true while still being outside the current task's scope, superseded by newer evidence, or unavailable under current permission. This skill makes those boundaries visible before an agent relies on the memory.

## Quick start

Requires Python 3.10 or later. No packages, model access, credentials, or network access are needed to run the helper and examples.

```bash
git clone https://github.com/Jesse-Zeng423/memory-applicability-guard.git
cd memory-applicability-guard
python3 -B examples/run_examples.py
python3 -B -m unittest discover -s tests -v
python3 -B scripts/verify_release.py
```

The example runner checks full expected outputs for three synthetic cases: a superseded preference, explicit transfer into a new context, and an uncertain memory with a robust alternative. See [examples/README.md](examples/README.md) for individual commands.

## Install the skill

The installable folder is [`memory-applicability-guard/`](memory-applicability-guard/SKILL.md), not the repository root. Copy that entire folder into your agent's supported skill directory. Keep `scripts/`, `references/`, and `agents/` together with `SKILL.md`.

For a local Codex installation using its existing `~/.codex/skills` directory:

```bash
mkdir -p ~/.codex/skills
# First check that this destination does not already exist.
test ! -e ~/.codex/skills/memory-applicability-guard && cp -R memory-applicability-guard ~/.codex/skills/
```

If the destination already exists, review the installed version before replacing it. For another skill-capable agent, use its documented discovery directory. The helper is independent of any agent platform; automatic discovery depends on the host.

Example request:

> Use $memory-applicability-guard to audit the supplied candidate memory and proposed memory action. Use only the evidence in this request. Return the structured decision and its limitations.

Provide the fields documented in [the decision model](memory-applicability-guard/references/decision-model.md). To run the helper directly:

```bash
python3 -B memory-applicability-guard/scripts/guard_decision.py < examples/superseded-preference.input.json
```

## How it works

```text
Current task + candidate memory + proposed reliance + supplied evidence
                              |
                    Agent classifies fields
                              |
                     JSON input validation
                              |
                  Deterministic precedence rules
                              |
               Structured decision for caller review
```

The output includes `guard_verdict`, `memory_action`, `memory_state`, `resolution_source`, `decisive_evidence`, `reason_code`, `next_step`, and `boundary`.

| Verdict | Meaning |
| --- | --- |
| `PASS` | Proposed memory reliance matches the recommendation. |
| `REVISE` | Change the proposed memory reliance. |
| `ASK_USER` | Ask for missing, user-resolvable information. |
| `VERIFY_EXTERNAL` | Obtain current or third-party evidence before relying on memory. |
| `ESCALATE` | High-risk input requires qualified human review. |

`memory_action` is `USE`, `IGNORE`, or `ASK`. `PASS` never approves the underlying task. The helper cannot verify that an agent classified prose correctly; callers must support those classifications with evidence. Unknown fields should remain unknown.

## Helper command-line options

```bash
python3 -B memory-applicability-guard/scripts/guard_decision.py --file examples/superseded-preference.input.json --pretty
python3 -B memory-applicability-guard/scripts/guard_decision.py --validate-only --file examples/superseded-preference.input.json
python3 -B memory-applicability-guard/scripts/guard_decision.py --schema
```

Invalid inputs produce a JSON error on stderr and exit with status 2. `--schema` prints the closed input contract; `--validate-only` checks it without producing a decision. The contract is also available in `schema/guard-input.schema.json`, with examples in `schema/examples/`.

## Install the Python helper

The skill remains standalone. From a clone, install the optional Python wrapper with `python3 -m pip install .`; the wheel includes the same helper used by the skill. Run it with `python3 -m memory_applicability_guard --file schema/examples/superseded-pool.json --pretty`.

## Repository map

- `memory-applicability-guard/`: portable skill instructions, helper, and references.
- `examples/`: runnable synthetic inputs, expected results, and a checked runner.
- `schema/`: JSON Schema contracts and example inputs.
- `src/`: optional Python package wrapper.
- `tests/`: rule, validation, precedence, and command-line regression tests.
- `scripts/`: offline integrity verification and manifest refresh tools.
- `docs/agent-workflow.md`: guide for integrating the guard into an agent workflow.
- `docs/devto-build-log.md`: English build-log draft for editorial review.
- `docs/hacktoberfest-2026.md`: flexible event plan and official sources.
- `submissions/`: challenge mapping and a reusable entry worksheet.
- `release/` and `SHA256SUMS`: current integrity metadata and historical provenance.


## Research boundary

The frozen v0.7 experiment ended at `STOP_AT_V07`. A0 and M1 both scored 110/128, with matched net improvement of zero. Strict-twin stable flips were 28/40 for A0 and 27/40 for M1; ASK recall was 60% for both. These are historical research results, not measurements of this packaging update. See [research boundaries](memory-applicability-guard/references/research-boundaries.md).

Passing software tests establishes behavior on specified inputs. It does not show improved agent accuracy, reliable evidence extraction, or production safety. The helper does not retrieve memories, train or fine-tune a model, call an API, or execute recommended actions.

## Hacktoberfest 2026

This package is a portfolio deliverable and reusable open-source AI skill. Event participation requires a separate mapping to the published dashboard activities or challenge rules. Pull requests do not count toward rewards, per the [official FAQ](https://hacktoberfest.com/questions/). No challenge eligibility or reward is claimed. See [the event plan](docs/hacktoberfest-2026.md) before preparing an entry.

## Contributing and license

Add synthetic cases and tests for observed failures. Keep challenge-specific adapters separate from the core and run the checks above before proposing a change. After intentionally changing package files, regenerate integrity metadata with `python3 -B scripts/refresh_release.py`, then run verification again.

Current package: [MIT](LICENSE), copyright 2026 Jesse Zeng. Earlier license grants and release records are preserved; see [license scope](LICENSE_SCOPE.md). Do not include personal memories or private research data in contributions.
