#!/usr/bin/env python3
"""Refresh current integrity metadata after reviewing intentional changes."""
import json
from pathlib import Path
from verify_release import ROOT, digest, package_files

def main():
    manifest = {
        "schema_version": "1.0", "package_name": "memory-applicability-guard",
        "packaging_date": "2026-09-29", "license": "MIT",
        "skill_root": "memory-applicability-guard", "python_requires": ">=3.10",
        "research_disposition": "STOP_AT_V07",
        "boundary": "Research-informed decision support only; not production validated.",
        "historical_release": "release/public_release_manifest_v1.0.0.json",
        "skill_files": [{"path": str(Path(p).relative_to("memory-applicability-guard")), "sha256": digest(ROOT / p)}
                        for p in package_files() if p.startswith("memory-applicability-guard/")],
    }
    (ROOT / "release/package_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    # Include the inventory and checksum file themselves before enumerating.
    for relative in ("release/FILE_INVENTORY.txt", "SHA256SUMS"):
        (ROOT / relative).touch(exist_ok=True)
    files = package_files()
    (ROOT / "release/FILE_INVENTORY.txt").write_text("\n".join(files) + "\n")
    (ROOT / "SHA256SUMS").write_text("".join(f"{digest(ROOT / p)}  {p}\n" for p in files if p != "SHA256SUMS"))
    print(f"Refreshed integrity metadata for {len(files)} files. Run verify_release.py next.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
