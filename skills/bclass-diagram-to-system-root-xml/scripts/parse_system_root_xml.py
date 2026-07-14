#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
from simulink_xml_common import parse_system_root_xml, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse Simulink system_root.xml into SimulinkSystemJSON.")
    parser.add_argument("xml", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    write_json(args.output, parse_system_root_xml(args.xml))
    print(f"OK: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
