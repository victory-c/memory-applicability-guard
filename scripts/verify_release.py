#!/usr/bin/env python3
"""Offline package integrity and behavior checks; not a safety certification."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "memory-applicability-guard"
IGNORED_PARTS = {".git", "__pycache__", ".pytest_cache", ".venv", "dist"}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def package_files():
    return sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
                  if p.is_file() and not (set(p.relative_to(ROOT).parts) & IGNORED_PARTS)
                  and p.name not in {".DS_Store", ".coverage"} and p.suffix != ".pyc")

def verify():
    errors = []
    actual = package_files()
    inventory = (ROOT / "release/FILE_INVENTORY.txt").read_text().splitlines()
    if inventory != actual:
        errors.append("Repository inventory mismatch")
    sums = {}
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        value, relative = line.split("  ", 1)
        sums[relative] = value
    if set(sums) != set(actual) - {"SHA256SUMS"}:
        errors.append("Checksum coverage mismatch")
    for relative, expected in sums.items():
        if relative not in actual or digest(ROOT / relative) != expected:
            errors.append(f"Hash mismatch: {relative}")
    manifest = json.loads((ROOT / "release/package_manifest.json").read_text())
    if manifest.get("license") != "MIT" or manifest.get("research_disposition") != "STOP_AT_V07":
        errors.append("Package license or research disposition mismatch")
    expected_skill = sorted(item["path"] for item in manifest["skill_files"])
    actual_skill = sorted(str(Path(relative).relative_to("memory-applicability-guard"))
                          for relative in actual if relative.startswith("memory-applicability-guard/"))
    if actual_skill != expected_skill:
        errors.append("Skill inventory mismatch")
    for item in manifest["skill_files"]:
        if item["path"] not in actual_skill or digest(SKILL / item["path"]) != item["sha256"]:
            errors.append(f"Skill hash mismatch: {item['path']}")
    skill_text = (SKILL / "SKILL.md").read_text()
    frontmatter = skill_text.split("---", 2)
    if not skill_text.startswith("---\n") or len(frontmatter) != 3:
        errors.append("Missing skill frontmatter")
    else:
        header = dict(line.split(":", 1) for line in frontmatter[1].splitlines() if line.strip())
        if header.get("name", "").strip() != "memory-applicability-guard" or not header.get("description", "").strip():
            errors.append("Invalid skill name or description")
    license_text = (ROOT / "LICENSE").read_text()
    for marker in ("MIT License", "Copyright (c) 2026 Jesse Zeng", "Permission is hereby granted", "THE SOFTWARE IS PROVIDED"):
        if marker not in license_text:
            errors.append("MIT license marker missing")
    if "STOP_AT_V07" not in (ROOT / "NOTICE").read_text():
        errors.append("Research notice missing")
    for relative in actual:
        path = ROOT / relative
        if path.is_symlink():
            errors.append(f"Symlink in package: {relative}")
        text = path.read_text(encoding="utf-8")
        for marker in ("/" + "Users" + "/", "Authorization" + ": " + "Bearer", "api." + "openai.com"):
            if marker in text:
                errors.append(f"Private-data marker in {relative}")
    helper = (SKILL / "scripts/guard_decision.py").read_text()
    compile(helper, str(SKILL / "scripts/guard_decision.py"), "exec")
    for marker in ("import os", "import socket", "import urllib", "import requests", "http.client", "subprocess", "OPENAI_API_KEY"):
        if marker in helper:
            errors.append(f"Unexpected helper dependency: {marker}")
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    count = suite.countTestCases()
    test_result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
    if not test_result.wasSuccessful():
        errors.append("Automated tests failed")
    return {"status": "PASS" if not errors else "FAIL", "errors": errors,
            "files": len(actual), "skill_files": len(actual_skill),
            "tests_run": test_result.testsRun, "tests_discovered": count,
            "license": "MIT", "boundary": "Package checks do not establish production validation."}

def main():
    try:
        result = verify()
    except (OSError, ValueError, KeyError) as error:
        result = {"status": "FAIL", "errors": [str(error)]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
