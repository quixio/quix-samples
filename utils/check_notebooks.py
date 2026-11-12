#!/usr/bin/env python3
"""Check every notebook library item. Usage: check_notebooks.py [root]

A notebook item has Type "Notebook" in library.json. It must be a plain copy
source: no DeploySettings, no Variables, one .py file, no token placeholder.
"""
import json
import sys
from pathlib import Path


def check_item(lib: Path) -> list[str]:
    errors = []
    folder = lib.parent
    data = json.loads(lib.read_text(encoding="utf-8"))
    for key in ("DeploySettings", "Variables"):
        if key in data:
            errors.append(f"{lib}: notebook item must not have {key}")
    py_files = [p for p in folder.rglob("*.py")]
    if len(py_files) != 1:
        errors.append(f"{lib}: notebook item needs exactly one .py file, found {len(py_files)}")
    for f in folder.rglob("*"):
        if f.is_file() and "{placeholder:token}" in f.read_text(encoding="utf-8", errors="ignore").lower():
            errors.append(f"{f}: token placeholder is not allowed in a notebook item")
    return errors


def check(root: Path) -> list[str]:
    errors = []
    for lib in root.rglob("library.json"):
        try:
            data = json.loads(lib.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if "Notebook" in (data.get("tags") or {}).get("Type", []):
            errors += check_item(lib)
    return errors


if __name__ == "__main__":
    errs = check(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    print("\n".join(errs) or "notebook items OK")
    sys.exit(1 if errs else 0)
