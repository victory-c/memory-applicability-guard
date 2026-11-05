#!/usr/bin/env python3
"""Deterministic decision support for structured memory-applicability audits."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TextIO


__version__ = "1.0.0"

PERMISSIONS = {"ALLOWED", "REVOKED", "UNKNOWN"}
RELATIONSHIPS = {"DIRECT", "EXPLICIT_TRANSFER", "NO_BRIDGE", "SUPERSEDED", "CONFLICTING", "UNKNOWN"}
EVIDENCE_STATUSES = {"SUFFICIENT", "USER_RESOLVABLE", "EXTERNAL_REQUIRED", "UNKNOWN"}
RISKS = {"LOW", "MEDIUM", "HIGH"}
MEMORY_ACTIONS = {"USE", "IGNORE", "ASK"}
EVIDENCE_KINDS = {"MEMORY_SOURCE", "APPLICABILITY", "PERMISSION", "CURRENT_EXTERNAL", "USER_STATEMENT"}
REQUIRED_FIELDS = {
    "current_task",
    "candidate_memory",
    "proposed_memory_action",
    "permission",
    "relationship",
    "evidence_status",
    "robust_action_available",
    "risk",
    "evidence",
}
OPTIONAL_FIELDS = {"robust_action"}
EVIDENCE_FIELDS = {"id", "text", "kind", "decisive"}
BOUNDARY = "Research-informed decision-support prototype; not production validated; no autonomous execution or high-risk approval."
NONEMPTY_STRING_PATTERN = r"^(?!\s*$).+"


class InputValidationError(ValueError):
    """Raised when a guard input violates the closed input contract."""

    def __init__(self, message: str, issues: list[str] | None = None) -> None:
        super().__init__(message)
        self.issues = issues if issues is not None else [message]


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_enum(payload: dict[str, Any], field: str, allowed: set[str], errors: list[str]) -> None:
    value = payload.get(field)
    if not isinstance(value, str) or value not in allowed:
        errors.append(f"{field} must be one of {sorted(allowed)}; got {value!r}")


def _enum_schema(values: set[str]) -> dict[str, Any]:
    return {"type": "string", "enum": sorted(values)}


def _nonempty_string_schema(description: str) -> dict[str, Any]:
    return {
        "type": "string",
        "minLength": 1,
        "pattern": NONEMPTY_STRING_PATTERN,
        "description": description,
    }


def input_schema() -> dict[str, Any]:
    """Return the machine-readable closed input contract as JSON Schema."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/Jesse-Zeng423/memory-applicability-guard/schema/guard-input.schema.json",
        "title": "Memory Applicability Guard input",
        "description": (
            "Closed input contract for the deterministic helper. "
            "Classifications must be supplied explicitly; the helper does not infer them from prose. "
            "Decision support only; not production validated."
        ),
        "type": "object",
        "additionalProperties": False,
        "required": sorted(REQUIRED_FIELDS),
        "properties": {
            "current_task": _nonempty_string_schema("The current task the Agent is considering."),
            "candidate_memory": _nonempty_string_schema("The memory proposed to influence the task."),
            "proposed_memory_action": {
                **_enum_schema(MEMORY_ACTIONS),
                "description": "The Agent's proposed memory reliance decision.",
            },
            "permission": {
                **_enum_schema(PERMISSIONS),
                "description": "Whether current permission allows relying on the memory.",
            },
            "relationship": {
                **_enum_schema(RELATIONSHIPS),
                "description": "How the candidate memory relates to the current task.",
            },
            "evidence_status": {
                **_enum_schema(EVIDENCE_STATUSES),
                "description": "Whether supplied evidence is enough to decide applicability.",
            },
            "robust_action_available": {
                "type": "boolean",
                "description": "True when one named action is acceptable across reasonable applicability worlds.",
            },
            "robust_action": {
                "type": ["string", "null"],
                "minLength": 1,
                "pattern": NONEMPTY_STRING_PATTERN,
                "description": "Required when robust_action_available is true; omit or null otherwise.",
            },
            "risk": {
                **_enum_schema(RISKS),
                "description": "Risk of relying on the memory for the current task.",
            },
            "evidence": {
                "type": "array",
                "minItems": 1,
                "description": "Non-empty list of structured evidence objects with stable IDs.",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": sorted(EVIDENCE_FIELDS),
                    "properties": {
                        "id": _nonempty_string_schema("Stable evidence identifier."),
                        "text": _nonempty_string_schema("Evidence text as supplied; not inferred."),
                        "kind": {
                            **_enum_schema(EVIDENCE_KINDS),
                            "description": "Evidence category. MEMORY_SOURCE cannot be decisive.",
                        },
                        "decisive": {
                            "type": "boolean",
                            "description": "True only for current boundary evidence that decides applicability.",
                        },
                    },
                    "allOf": [
                        {
                            "if": {"properties": {"kind": {"const": "MEMORY_SOURCE"}}, "required": ["kind"]},
                            "then": {"properties": {"decisive": {"const": False}}},
                        }
                    ],
                },
            },
        },
        "allOf": [
            {
                "if": {"properties": {"robust_action_available": {"const": True}}, "required": ["robust_action_available"]},
                "then": {"required": ["robust_action"]},
            },
            {
                "if": {"properties": {"robust_action_available": {"const": False}}, "required": ["robust_action_available"]},
                "then": {"properties": {"robust_action": {"type": "null"}}},
            },
        ],
    }


def collect_input_errors(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["input must be a single JSON object"]
    keys = set(payload)
    missing = sorted(REQUIRED_FIELDS - keys)
    unknown = sorted(keys - REQUIRED_FIELDS - OPTIONAL_FIELDS)
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if unknown:
        errors.append(f"unknown fields: {', '.join(unknown)}")
    if not _nonempty_string(payload.get("current_task")):
        errors.append("current_task must be a non-empty string")
    if not _nonempty_string(payload.get("candidate_memory")):
        errors.append("candidate_memory must be a non-empty string")
    _validate_enum(payload, "proposed_memory_action", MEMORY_ACTIONS, errors)
    _validate_enum(payload, "permission", PERMISSIONS, errors)
    _validate_enum(payload, "relationship", RELATIONSHIPS, errors)
    _validate_enum(payload, "evidence_status", EVIDENCE_STATUSES, errors)
    _validate_enum(payload, "risk", RISKS, errors)
    if not isinstance(payload.get("robust_action_available"), bool):
        errors.append("robust_action_available must be a boolean")
    robust_action = payload.get("robust_action")
    if payload.get("robust_action_available") is True and not _nonempty_string(robust_action):
        errors.append("robust_action must be a non-empty string when robust_action_available is true")
    if payload.get("robust_action_available") is False and robust_action is not None:
        errors.append("robust_action must be absent or null when robust_action_available is false")

    evidence = payload.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty array")
        return errors
    seen: set[str] = set()
    for index, item in enumerate(evidence):
        prefix = f"evidence[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        item_keys = set(item)
        if item_keys != EVIDENCE_FIELDS:
            errors.append(f"{prefix} fields must be exactly {sorted(EVIDENCE_FIELDS)}")
        evidence_id = item.get("id")
        if not _nonempty_string(evidence_id):
            errors.append(f"{prefix}.id must be a non-empty string")
        elif evidence_id in seen:
            errors.append(f"duplicate evidence id: {evidence_id}")
        else:
            seen.add(evidence_id)
        if not _nonempty_string(item.get("text")):
            errors.append(f"{prefix}.text must be a non-empty string")
        if not isinstance(item.get("kind"), str) or item.get("kind") not in EVIDENCE_KINDS:
            errors.append(f"{prefix}.kind must be one of {sorted(EVIDENCE_KINDS)}")
        if not isinstance(item.get("decisive"), bool):
            errors.append(f"{prefix}.decisive must be a boolean")
        if item.get("kind") == "MEMORY_SOURCE" and item.get("decisive") is True:
            errors.append(f"{prefix}: MEMORY_SOURCE cannot be decisive applicability evidence")
    return errors


def validate_input(payload: Any) -> dict[str, Any]:
    errors = collect_input_errors(payload)

    if errors:
        raise InputValidationError("; ".join(errors), issues=errors)
    return payload


def _decisive_evidence(payload: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"id": item["id"], "kind": item["kind"], "text": item["text"]}
        for item in payload["evidence"]
        if item["decisive"]
    ]


def _aligned_verdict(proposed: str, recommended: str) -> str:
    return "PASS" if proposed == recommended else "REVISE"


def decide(value: Any) -> dict[str, Any]:
    payload = validate_input(value)
    proposed = payload["proposed_memory_action"]
    permission = payload["permission"]
    relationship = payload["relationship"]
    evidence_status = payload["evidence_status"]
    robust = payload["robust_action_available"]
    risk = payload["risk"]

    if permission == "REVOKED":
        verdict, action, state, source, reason = _aligned_verdict(proposed, "IGNORE"), "IGNORE", "CLEAR_INAPPLICABLE", "USER", "PERMISSION_REVOKED"
        next_step = "Do not rely on the candidate memory; continue only with permission-safe information."
    elif risk == "HIGH":
        verdict, action, state, source, reason = "ESCALATE", "IGNORE", "UNCERTAIN", "HUMAN_REVIEW", "HIGH_RISK_HUMAN_REVIEW_REQUIRED"
        next_step = "Pause memory-grounded action and escalate to a qualified human decision-maker."
    elif evidence_status == "EXTERNAL_REQUIRED":
        verdict, action, state, source, reason = "VERIFY_EXTERNAL", "IGNORE", "UNCERTAIN", "EXTERNAL_EVIDENCE", "EXTERNAL_VERIFICATION_REQUIRED"
        next_step = "Verify current or third-party facts externally before relying on the memory; do not ask the user to guess."
    elif relationship == "NO_BRIDGE":
        verdict, action, state, source, reason = _aligned_verdict(proposed, "IGNORE"), "IGNORE", "CLEAR_INAPPLICABLE", "SUPPLIED_EVIDENCE", "NO_BRIDGE"
        next_step = "Continue without relying on the candidate memory unless explicit transfer evidence is supplied."
    elif relationship == "SUPERSEDED":
        verdict, action, state, source, reason = _aligned_verdict(proposed, "IGNORE"), "IGNORE", "CLEAR_INAPPLICABLE", "SUPPLIED_EVIDENCE", "SUPERSEDED"
        next_step = "Use the newer supplied evidence and do not rely on the superseded memory."
    elif relationship in {"DIRECT", "EXPLICIT_TRANSFER"} and permission == "ALLOWED" and evidence_status == "SUFFICIENT":
        verdict, action, state, source = _aligned_verdict(proposed, "USE"), "USE", "CLEAR_APPLICABLE", "SUPPLIED_EVIDENCE"
        reason = relationship
        next_step = "The recommendation may rely on the candidate memory within the evidenced scope and permission."
    elif evidence_status == "USER_RESOLVABLE" and not robust:
        verdict, action, state, source, reason = "ASK_USER", "ASK", "UNCERTAIN", "USER", "USER_RESOLVABLE_UNCERTAINTY"
        next_step = "Ask one targeted question whose answer would change the memory or task action."
    elif robust:
        verdict, action, state, source, reason = _aligned_verdict(proposed, "IGNORE"), "IGNORE", "UNCERTAIN", "NONE", "ROBUST_ACTION_AVAILABLE"
        next_step = f"Take the robust action without relying on the disputed memory: {payload['robust_action']}"
    else:
        verdict, action, state, source, reason = "ASK_USER", "ASK", "UNCERTAIN", "USER", "EVIDENCE_GAP"
        next_step = "Request only the missing applicability or permission information that could change the action."

    return {
        "boundary": BOUNDARY,
        "decisive_evidence": _decisive_evidence(payload),
        "guard_verdict": verdict,
        "memory_action": action,
        "memory_state": state,
        "next_step": next_step,
        "reason_code": reason,
        "resolution_source": source,
    }


def _dump_json(value: Any, pretty: bool, stream: TextIO) -> None:
    if pretty:
        print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), file=stream)
    else:
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")), file=stream)


def _error_payload(error: BaseException) -> dict[str, Any]:
    message: dict[str, Any] = {"error": "INPUT_VALIDATION_ERROR"}
    if isinstance(error, json.JSONDecodeError):
        message["details"] = f"invalid JSON at line {error.lineno} column {error.colno}: {error.msg}"
        message["issues"] = [message["details"]]
        return message
    if isinstance(error, InputValidationError):
        message["details"] = str(error)
        message["issues"] = list(error.issues)
        return message
    message["details"] = str(error)
    message["issues"] = [str(error)]
    return message


def load_payload(path: str | None) -> Any:
    if path:
        source = Path(path)
        if not source.is_file():
            raise InputValidationError(f"input file not found: {path}")
        return json.loads(source.read_text(encoding="utf-8"))
    if sys.stdin.isatty():
        raise InputValidationError("no input: pass JSON on stdin or use --file PATH")
    return json.load(sys.stdin)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="guard_decision.py",
        description=(
            "Deterministic memory-applicability decision helper. "
            "Reads one JSON object and prints a recommendation. "
            "Decision support only; not production validated."
        ),
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="PATH",
        help="Read input JSON from PATH instead of stdin",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--schema", action="store_true", help="Print the closed input JSON Schema and exit")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the input contract and exit without producing a decision",
    )
    parser.add_argument("--version", action="store_true", help="Print the helper version and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pretty = bool(args.pretty)
    if args.version:
        print(__version__)
        return 0
    if args.schema:
        _dump_json(input_schema(), pretty=True, stream=sys.stdout)
        return 0
    try:
        payload = load_payload(args.file)
        if args.validate_only:
            validate_input(payload)
            _dump_json({"status": "VALID"}, pretty, sys.stdout)
            return 0
        result = decide(payload)
    except (json.JSONDecodeError, InputValidationError, OSError) as error:
        _dump_json(_error_payload(error), pretty, sys.stderr)
        return 2
    _dump_json(result, pretty, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
