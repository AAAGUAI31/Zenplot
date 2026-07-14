#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
from simulink_xml_common import emit_system_root_xml, read_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit Simulink system_root.xml <System> from SimulinkSystemJSON.")
    parser.add_argument("json", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    emit_system_root_xml(read_json(args.json), args.output)
    print(f"OK: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
