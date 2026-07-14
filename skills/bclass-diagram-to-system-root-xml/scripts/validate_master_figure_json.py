#!/usr/bin/env python
"""Validate MasterFigureJSON v0.1 files with lightweight checks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT_KEYS = {"meta", "nodes", "edges", "layout", "style"}
ID_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


def endpoint_node(endpoint: str) -> str:
    return endpoint.split(".", 1)[0]


def validate_doc(doc: object, path: Path) -> list[str]:
    errors: list[str] = []
    where = str(path)

    if not isinstance(doc, dict):
        return [f"{where}: root must be an object"]

    keys = set(doc)
    missing = ROOT_KEYS - keys
    extra = keys - ROOT_KEYS
    if missing:
        errors.append(f"{where}: missing root keys: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"{where}: unsupported root keys: {', '.join(sorted(extra))}")

    meta = doc.get("meta")
    if not isinstance(meta, dict):
        errors.append(f"{where}: meta must be an object")
    else:
        for key in ("diagram_type", "domain", "version", "source"):
            if not isinstance(meta.get(key), str) or not meta.get(key):
                errors.append(f"{where}: meta.{key} must be a non-empty string")

    nodes = doc.get("nodes")
    node_ids: set[str] = set()
    if not isinstance(nodes, list) or not nodes:
        errors.append(f"{where}: nodes must be a non-empty array")
    else:
        for idx, node in enumerate(nodes):
            prefix = f"{where}: nodes[{idx}]"
            if not isinstance(node, dict):
                errors.append(f"{prefix} must be an object")
                continue
            node_id = node.get("id")
            if not isinstance(node_id, str) or not ID_RE.match(node_id):
                errors.append(f"{prefix}.id must be a stable identifier")
            elif node_id in node_ids:
                errors.append(f"{prefix}.id duplicates {node_id}")
            else:
                node_ids.add(node_id)
            if not isinstance(node.get("type"), str) or not node.get("type"):
                errors.append(f"{prefix}.type must be a non-empty string")
            if not isinstance(node.get("label"), str):
                errors.append(f"{prefix}.label must be a string")
            ports = node.get("ports")
            if not isinstance(ports, list) or not ports or not all(isinstance(p, str) and p for p in ports):
                errors.append(f"{prefix}.ports must be a non-empty string array")
            signs = node.get("signs")
            if signs is not None and not isinstance(signs, dict):
                errors.append(f"{prefix}.signs must be an object when present")

    edges = doc.get("edges")
    if not isinstance(edges, list):
        errors.append(f"{where}: edges must be an array")
    else:
        for idx, edge in enumerate(edges):
            prefix = f"{where}: edges[{idx}]"
            if not isinstance(edge, dict):
                errors.append(f"{prefix} must be an object")
                continue
            source = edge.get("from")
            target = edge.get("to")
            if not isinstance(source, str) or "." not in source:
                errors.append(f"{prefix}.from must be an endpoint string like node.port")
            elif node_ids and endpoint_node(source) not in node_ids:
                errors.append(f"{prefix}.from references missing node {endpoint_node(source)}")
            targets = target if isinstance(target, list) else [target]
            if not targets or not all(isinstance(t, str) and "." in t for t in targets):
                errors.append(f"{prefix}.to must be an endpoint string or array of endpoint strings")
            else:
                for item in targets:
                    if node_ids and endpoint_node(item) not in node_ids:
                        errors.append(f"{prefix}.to references missing node {endpoint_node(item)}")
            if not isinstance(edge.get("type"), str) or not edge.get("type"):
                errors.append(f"{prefix}.type must be a non-empty string")

    if not isinstance(doc.get("layout"), dict):
        errors.append(f"{where}: layout must be an object")
    if not isinstance(doc.get("style"), dict):
        errors.append(f"{where}: style must be an object")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate MasterFigureJSON v0.1 files.")
    parser.add_argument("json_files", nargs="+", type=Path)
    args = parser.parse_args()

    all_errors: list[str] = []
    for json_file in args.json_files:
        try:
            with json_file.open("r", encoding="utf-8") as handle:
                doc = json.load(handle)
        except Exception as exc:
            all_errors.append(f"{json_file}: failed to read JSON: {exc}")
            continue
        all_errors.extend(validate_doc(doc, json_file))

    if all_errors:
        for error in all_errors:
            print(error, file=sys.stderr)
        return 1
    print(f"OK: validated {len(args.json_files)} MasterFigureJSON file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
