#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from simulink_xml_common import summarize_for_compare


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two Simulink system_root.xml files structurally.")
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    ref = summarize_for_compare(args.reference)
    cand = summarize_for_compare(args.candidate)
    errors = []
    for key in ("blocks", "lines", "annotations"):
        if len(ref[key]) != len(cand[key]):
            errors.append(f"{key}: count differs, reference={len(ref[key])}, candidate={len(cand[key])}")
        if ref[key] != cand[key]:
            errors.append(f"{key}: structural signature differs")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(
        "OK: structurally equivalent "
        f"({len(ref['blocks'])} blocks, {len(ref['lines'])} lines, {len(ref['annotations'])} annotations)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
