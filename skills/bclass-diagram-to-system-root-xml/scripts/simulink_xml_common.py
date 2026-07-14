#!/usr/bin/env python
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def slugify(value: str, fallback: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
    if not value:
        return fallback
    if value[0].isdigit():
        value = f"b_{value}"
    return value


def parse_vector(value: str | None) -> list[int | float] | None:
    if not value:
        return None
    nums = re.findall(r"-?\d+(?:\.\d+)?", value)
    parsed: list[int | float] = []
    for item in nums:
        number = float(item)
        parsed.append(int(number) if number.is_integer() else number)
    return parsed


def format_vector(values: list[Any] | None) -> str | None:
    if values is None:
        return None
    return "[" + ", ".join(str(int(v)) if isinstance(v, float) and v.is_integer() else str(v) for v in values) + "]"


def get_p_map(elem: ET.Element) -> dict[str, str]:
    return {child.attrib.get("Name", ""): child.text or "" for child in elem.findall("P")}


def add_p(parent: ET.Element, name: str, value: Any) -> None:
    p = ET.SubElement(parent, "P", {"Name": name})
    p.text = str(value)


def semantic_type(block_type: str, name: str) -> str:
    bt = block_type.lower()
    if bt in {"inport", "outport", "gain", "sum", "integrator", "switch", "constant"}:
        return bt
    if bt == "relay":
        return "quantizer"
    return slugify(name or block_type, "block")


def parse_branch(elem: ET.Element) -> dict[str, Any]:
    p_map = get_p_map(elem)
    return {
        "dst": p_map.get("Dst"),
        "points": parse_vector(p_map.get("Points")) or [],
        "z_order": int(p_map["ZOrder"]) if p_map.get("ZOrder", "").lstrip("-").isdigit() else None,
        "branches": [parse_branch(child) for child in elem.findall("Branch")],
    }


def emit_branch(parent: ET.Element, branch: dict[str, Any]) -> None:
    elem = ET.SubElement(parent, "Branch")
    if branch.get("z_order") is not None:
        add_p(elem, "ZOrder", branch["z_order"])
    if branch.get("points"):
        add_p(elem, "Points", format_vector(branch["points"]))
    if branch.get("dst"):
        add_p(elem, "Dst", branch["dst"])
    for child in branch.get("branches", []):
        emit_branch(elem, child)


def parse_system_root_xml(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    if root.tag != "System":
        raise ValueError(f"Expected <System>, got <{root.tag}>")
    system_props = get_p_map(root)
    blocks = []
    for block in root.findall("Block"):
        p_map = get_p_map(block)
        position = parse_vector(p_map.get("Position")) or []
        z_order = p_map.get("ZOrder")
        params = {k: v for k, v in p_map.items() if k not in {"Position", "ZOrder"}}
        pc = block.find("PortCounts")
        port_counts = {k: int(v) for k, v in pc.attrib.items()} if pc is not None else {}
        sid = block.attrib.get("SID", "")
        name = block.attrib.get("Name", "")
        block_type = block.attrib.get("BlockType", "")
        blocks.append(
            {
                "sid": sid,
                "id": slugify(name, f"sid_{sid}"),
                "name": name,
                "block_type": block_type,
                "semantic_type": semantic_type(block_type, name),
                "parameters": params,
                "port_counts": port_counts,
                "position": position,
                "z_order": int(z_order) if z_order and z_order.lstrip("-").isdigit() else 0,
            }
        )
    lines = []
    for line in root.findall("Line"):
        p_map = get_p_map(line)
        z_order = p_map.get("ZOrder")
        lines.append(
            {
                "src": p_map.get("Src"),
                "dst": p_map.get("Dst"),
                "points": parse_vector(p_map.get("Points")) or [],
                "branches": [parse_branch(child) for child in line.findall("Branch")],
                "z_order": int(z_order) if z_order and z_order.lstrip("-").isdigit() else 0,
            }
        )
    annotations = []
    for ann in root.findall("Annotation"):
        p_map = get_p_map(ann)
        annotations.append(
            {
                "sid": ann.attrib.get("SID", ""),
                "name": p_map.get("Name", ""),
                "position": parse_vector(p_map.get("Position")) or [],
                "internal_margins": parse_vector(p_map.get("InternalMargins")) or [],
                "z_order": int(p_map["ZOrder"]) if p_map.get("ZOrder", "").lstrip("-").isdigit() else 0,
                "parameters": {k: v for k, v in p_map.items() if k not in {"Name", "Position", "InternalMargins", "ZOrder"}},
            }
        )
    return {
        "meta": {"version": "0.1", "source": "system_root_xml", "target": "simulink_system_root_xml"},
        "system": {"properties": system_props},
        "blocks": blocks,
        "lines": lines,
        "annotations": annotations,
        "layout": {},
        "style": {},
        "evidence": {"unresolved": [], "source_file": str(path)},
    }


def emit_system_root_xml(data: dict[str, Any], path: Path) -> None:
    root = ET.Element("System")
    for name, value in data.get("system", {}).get("properties", {}).items():
        add_p(root, name, value)
    for block in data.get("blocks", []):
        elem = ET.SubElement(root, "Block", {"BlockType": str(block["block_type"]), "Name": str(block["name"]), "SID": str(block["sid"])})
        pc = block.get("port_counts") or {}
        if pc:
            ET.SubElement(elem, "PortCounts", {k: str(v) for k, v in pc.items()})
        if block.get("position"):
            add_p(elem, "Position", format_vector(block["position"]))
        add_p(elem, "ZOrder", block.get("z_order", 0))
        for name, value in block.get("parameters", {}).items():
            add_p(elem, name, value)
    for line in data.get("lines", []):
        elem = ET.SubElement(root, "Line")
        add_p(elem, "ZOrder", line.get("z_order", 0))
        if line.get("src"):
            add_p(elem, "Src", line["src"])
        if line.get("points"):
            add_p(elem, "Points", format_vector(line["points"]))
        if line.get("dst"):
            add_p(elem, "Dst", line["dst"])
        for branch in line.get("branches", []):
            emit_branch(elem, branch)
    for ann in data.get("annotations", []):
        elem = ET.SubElement(root, "Annotation", {"SID": str(ann.get("sid", ""))})
        add_p(elem, "Name", ann.get("name", ""))
        if ann.get("position"):
            add_p(elem, "Position", format_vector(ann["position"]))
        if ann.get("internal_margins"):
            add_p(elem, "InternalMargins", format_vector(ann["internal_margins"]))
        add_p(elem, "ZOrder", ann.get("z_order", 0))
        for name, value in ann.get("parameters", {}).items():
            add_p(elem, name, value)
    ET.indent(root, space="  ")
    path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def validate_simulink_system_json(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"meta", "system", "blocks", "lines", "annotations", "layout", "style", "evidence"}
    missing = required - set(data)
    if missing:
        errors.append(f"missing root keys: {sorted(missing)}")
    seen_sids = set()
    for index, block in enumerate(data.get("blocks", [])):
        for key in ("sid", "id", "name", "block_type", "parameters", "position", "z_order"):
            if key not in block:
                errors.append(f"block[{index}] missing {key}")
        sid = block.get("sid")
        if sid in seen_sids:
            errors.append(f"duplicate block sid: {sid}")
        seen_sids.add(sid)
        if block.get("position") and len(block["position"]) != 4:
            errors.append(f"block {sid} position must have 4 numbers")
    for index, line in enumerate(data.get("lines", [])):
        if not line.get("src"):
            errors.append(f"line[{index}] missing src")
        if not line.get("dst") and not line.get("branches"):
            errors.append(f"line[{index}] has no dst or branches")
    return errors


def summarize_for_compare(path: Path) -> dict[str, Any]:
    data = parse_system_root_xml(path)
    return {
        "blocks": [(b["sid"], b["block_type"], b["name"], b.get("port_counts", {}), b.get("parameters", {})) for b in data["blocks"]],
        "lines": [(line.get("src"), line.get("dst"), line.get("points"), branch_signature(line.get("branches", []))) for line in data["lines"]],
        "annotations": [(ann.get("sid"), ann.get("name")) for ann in data["annotations"]],
    }


def branch_signature(branches: list[dict[str, Any]]) -> list[Any]:
    return [(b.get("dst"), b.get("points"), branch_signature(b.get("branches", []))) for b in branches]

