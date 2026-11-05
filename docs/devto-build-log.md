---
title: "When Relevant Memory Is Not Applicable: Building an Open-Source Agent Skill"
published: false
description: "Packaging Memory Applicability Guard with explicit evidence, deterministic rules, and reproducible examples."
tags: ai, opensource, python
---

An agent can remember something correctly and still use it in the wrong
situation. A preference from an earlier task may have changed. A remembered
fact may require current verification. Permission to use it may have been
revoked. Retrieval answers where to find the memory; it does not settle
whether that memory should influence today's recommendation.

I packaged **Memory Applicability Guard** as an open-source agent skill to
make that review explicit. It is a research-informed decision-support
prototype, not a production-validated safety system.

[The repository](https://github.com/Jesse-Zeng423/memory-applicability-guard)
contains the skill, a Python helper, synthetic examples, and automated tests.
The current package is MIT-licensed and runs without model access or Python
package dependencies.

## The problem: relevance is only the beginning

Consider an older memory that the user preferred slides for workshop notes.
Today the user explicitly requests a plain-text outline. The older memory is
relevant to the topic and may be historically true. Using it to produce
slides would still disregard the current instruction.

I wanted an audit that separates the candidate memory, the current task,
the proposed reliance decision, and the evidence establishing scope or
permission. That separation also makes uncertainty easier to discuss:
sometimes the next step is a user question, sometimes external verification,
and sometimes a reversible action works without relying on disputed memory.

## Design decisions

### Keep classification separate from rule execution

An agent reads the request and classifies fields such as permission,
relationship, evidence status, and risk. A deterministic helper validates
those fields and applies explicit precedence rules. It does not infer a
relationship from prose.

This makes rule execution reproducible, but creates a clear limitation:
incorrect classifications can produce an inappropriate recommendation.
Validation cannot prove that the supplied evidence supports the agent's
interpretation. The skill therefore asks callers to keep unknowns explicit.

### Separate memory reliance from the task itself

The helper returns a verdict and a `memory_action`: `USE`, `IGNORE`, or `ASK`.
A `PASS` means that the proposed reliance matches the rule recommendation.
It never approves the underlying task or executes it.

### Preserve evidence roles

Evidence records have IDs, text, kinds, and a decisive flag. A memory source
can explain provenance, but it cannot be marked as decisive applicability
evidence. The output preserves the supplied decisive evidence for inspection.
This does not independently verify its truth or relevance.

### Prefer a robust option when one is supplied

Uncertainty does not always justify interrupting the user. If the caller
supplies a useful action that works across reasonable interpretations, the
helper can recommend ignoring the disputed memory and taking that option.
The helper does not establish robustness on its own; that remains a caller
judgment supported by the current task.

## Architecture

```text
Task + memory + proposed reliance + supplied evidence
                        |
              Agent classifies the inputs
                        |
             JSON validation and rule helper
                        |
       Verdict + memory action + evidence + next step
                        |
                   Caller reviews
```

The installable folder contains `SKILL.md`, agent metadata, the helper, and
references for the decision model and research boundary. Executable examples
and package-level tests live outside it so the skill stays portable.

The rules consider revoked permission first, then high risk, then required
external verification. They next handle a missing transfer bridge and
superseded memory, followed by supported direct or explicit transfer,
user-resolvable uncertainty, robust alternatives, and remaining gaps.
Revoked permission therefore always prevents reliance on that memory,
even when other conditions also apply. It does not clear a high-risk task
for autonomous execution.

## Testing the package

Run the offline checks from a clone:

```bash
python3 -B examples/run_examples.py
python3 -B -m unittest discover -s tests -v
python3 -B scripts/verify_release.py
```

Three examples demonstrate superseded preferences, explicit transfer, and a
robust alternative. Each includes a synthetic input and expected JSON output.
The runner executes the actual command-line helper and compares the complete
result, including evidence and boundary text.

The automated suite exercises rule branches, conflicting-condition precedence,
permission and evidence gaps, malformed input, evidence-role constraints,
repeatable command-line output, and the executable examples. During packaging,
I found that arrays or objects in enum fields could cause an uncaught type
error. I changed validation to reject those values through the same structured
error contract as other invalid inputs and added regression tests.

A GitHub Actions workflow is configured for Python 3.10, 3.12, and 3.14.
Local test success and remote CI execution are separate evidence; the workflow
configuration alone is not a claim that every matrix job has run successfully.
Integrity verification checks package files against the manifest and checksums.
Those checks detect changes relative to the recorded files; they do not
independently establish authenticity or safety.

## What the research did not show

The earlier frozen v0.7 experiment ended at `STOP_AT_V07`. The compared
conditions both scored 110/128, with matched net improvement of zero. This
packaging work does not overturn that result.

Passing software tests shows that the helper follows specified rules on the
tested inputs. It does not demonstrate better real-world memory decisions,
reliable extraction across models, or safe autonomous high-risk behavior.
The project does not train or fine-tune an open-weight model.

## Lessons learned

Packaging exposed details that a research prototype can leave implicit:
installation paths, concrete inputs, error behavior, and the difference
between a recommendation and permission to act. Keeping the examples
synthetic made them shareable and reproducible without publishing personal
memories or private evaluation material.

The most useful architectural boundary is the one between evidence
classification and deterministic execution. A future model adapter would
need its own extraction evaluation; the helper's rule tests would not be a
substitute for that evidence.

## A reusable portfolio project for Hacktoberfest

The project is primarily a portfolio deliverable and an open-source agent
skill. Hacktoberfest 2026 focuses on open-source AI and open-weight models;
its [official FAQ](https://hacktoberfest.com/questions/) also makes clear that
pull requests no longer count toward rewards.

I am keeping the core independent of unknown challenge prompts. The repo has
a separate challenge map and entry worksheet, ready to adapt when DEV and
Global Hack Week publish their requirements. A relevant theme does not
establish eligibility: an entry still needs to satisfy the actual prompt,
existing-work rules, submission format, and dashboard activity requirements.

If you try the skill, a useful contribution is a synthetic case showing a
specific failure or ambiguous boundary, with the expected behavior explained.
That gives the next iteration something concrete to test.
