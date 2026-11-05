#!/usr/bin/env python3
"""Run the actual CLI against synthetic inputs and compare complete outputs."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    inputs = sorted((ROOT / "examples").glob("*.input.json"))
    if len(inputs) < 2:
        raise RuntimeError("At least two runnable examples are required")
    for path in inputs:
        expected_path = path.with_name(path.name.replace(".input.json", ".expected.json"))
        process = subprocess.run(
            [sys.executable, "-B", str(ROOT / "memory-applicability-guard/scripts/guard_decision.py")],
            input=path.read_text(), text=True, capture_output=True, check=True,
        )
        result = json.loads(process.stdout)
        if result != json.loads(expected_path.read_text()):
            raise AssertionError(f"Unexpected output for {path.name}")
        print(f"{path.stem}: {result['guard_verdict']} / {result['memory_action']} / {result['reason_code']}")
    print(f"All {len(inputs)} examples passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
