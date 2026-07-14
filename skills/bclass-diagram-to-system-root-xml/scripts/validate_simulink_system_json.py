#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from simulink_xml_common import read_json, validate_simulink_system_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SimulinkSystemJSON.")
    parser.add_argument("json_files", nargs="+", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    for path in args.json_files:
        for error in validate_simulink_system_json(read_json(path)):
            errors.append(f"{path}: {error}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"OK: validated {len(args.json_files)} SimulinkSystemJSON file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
