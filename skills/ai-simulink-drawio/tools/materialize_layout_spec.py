#!/usr/bin/env python
"""Mechanical LayoutSpec -> draw.io materializer.

This tool intentionally does not parse Simulink XML, infer semantics, choose
component keys, place nodes, or route edges. It only copies catalog templates
and writes the draw.io XML described by an existing LayoutSpec.
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path


def parse_style(style: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in style.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
    return out


def set_style(style: str, key: str, value: str) -> str:
    parts = [p for p in style.split(";") if p]
    found = False
    for i, part in enumerate(parts):
        if part.startswith(key + "="):
            parts[i] = f"{key}={value}"
            found = True
            break
    if not found:
        parts.append(f"{key}={value}")
    return ";".join(parts) + ";"


def load_catalog(path: Path):
    root = ET.parse(path).getroot()
    cells = root.findall(".//mxCell")
    by_id = {c.attrib["id"]: c for c in cells if "id" in c.attrib}
    templates = {}
    children = {}
    for cell in cells:
        parent = cell.attrib.get("parent")
        if parent:
            children.setdefault(parent, []).append(cell)
        style = cell.attrib.get("style", "")
        match = re.search(r"componentKey=([^;]+)", style)
        if match and "group" in style:
            key = match.group(1)
            templates[key] = cell
    return templates, children


def geom_of(cell: ET.Element):
    geom = cell.find("mxGeometry")
    if geom is None:
        return {}
    return {k: float(v) for k, v in geom.attrib.items() if k in {"x", "y", "width", "height"}}


def scale_geom(elem: ET.Element, sx: float, sy: float):
    geom = elem.find("mxGeometry")
    if geom is None:
        return
    for k, scale in (("x", sx), ("width", sx), ("y", sy), ("height", sy)):
        if k in geom.attrib:
            geom.attrib[k] = fmt(float(geom.attrib[k]) * scale)
    for pt in geom.findall(".//mxPoint"):
        if "x" in pt.attrib:
            pt.attrib["x"] = fmt(float(pt.attrib["x"]) * sx)
        if "y" in pt.attrib:
            pt.attrib["y"] = fmt(float(pt.attrib["y"]) * sy)


def fmt(value):
    value = round(float(value), 3)
    if value == int(value):
        return str(int(value))
    return str(value)


def ensure_root():
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "agent": "Codex ai-simulink-drawio",
            "version": "26.0.14",
            "type": "device",
        },
    )
    diagram = ET.SubElement(mxfile, "diagram", {"id": "ai-generated", "name": "AI Simulink Draw.io"})
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": "1600",
            "dy": "900",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": "1600",
            "pageHeight": "900",
            "math": "1",
            "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    return mxfile, root


def endpoint_id(endpoint: str) -> tuple[str, str | None]:
    if "." in endpoint:
        node, port = endpoint.rsplit(".", 1)
        return node, port
    return endpoint, None


def apply_gain_orientation(cell: ET.Element, orientation: str):
    direction = {"right": "east", "left": "west", "up": "north", "down": "south"}.get(orientation, "east")
    style = cell.attrib.get("style", "")
    if "shape=triangle" in style:
        cell.attrib["style"] = set_style(style, "direction", direction)


def rewrite_subtree(group, group_children, node, id_map, port_map, root):
    old_group_id = group.attrib["id"]
    group_copy = deepcopy(group)
    group_copy.attrib["id"] = node["id"]
    group_copy.attrib["parent"] = "1"
    group_copy.attrib["value"] = ""
    geom = group_copy.find("mxGeometry")
    target = node["geometry"]
    source = geom_of(group)
    tw = source.get("width") or target["w"]
    th = source.get("height") or target["h"]
    sx = target["w"] / tw if tw else 1
    sy = target["h"] / th if th else 1
    if geom is not None:
        geom.attrib.update({"x": fmt(target["x"]), "y": fmt(target["y"]), "width": fmt(target["w"]), "height": fmt(target["h"])})
    root.append(group_copy)
    id_map[old_group_id] = node["id"]

    for child in group_children.get(old_group_id, []):
        copied = deepcopy(child)
        old_id = copied.attrib["id"]
        new_id = f"{node['id']}__{old_id}"
        copied.attrib["id"] = new_id
        copied.attrib["parent"] = node["id"]
        if copied.attrib.get("source") in id_map:
            copied.attrib["source"] = id_map[copied.attrib["source"]]
        if copied.attrib.get("target") in id_map:
            copied.attrib["target"] = id_map[copied.attrib["target"]]
        style = copied.attrib.get("style", "")
        if node.get("component_key") == "gain_inline":
            apply_gain_orientation(copied, node.get("orientation", "right"))
            if copied.attrib.get("value") == "1":
                copied.attrib["value"] = str(node.get("label_bindings", {}).get("main", node.get("label", "")))
        scale_geom(copied, sx, sy)
        port = parse_style(copied.attrib.get("style", "")).get("portName")
        if port:
            port_map.setdefault(node["id"], {})[port] = new_id
            adjust_port_for_orientation(copied, port, node.get("orientation", "right"), target)
        root.append(copied)
        id_map[old_id] = new_id

    if node.get("component_key") == "junction_dot_inline":
        port_map.setdefault(node["id"], {})["center"] = node["id"]


def adjust_port_for_orientation(cell: ET.Element, port: str, orientation: str, target: dict):
    if orientation not in {"left", "up", "down"}:
        return
    geom = cell.find("mxGeometry")
    if geom is None:
        return
    w = float(geom.attrib.get("width", "2"))
    h = float(geom.attrib.get("height", "2"))
    if orientation == "left":
        if port == "in1":
            geom.attrib["x"] = fmt(target["w"] - w)
        elif port == "out1":
            geom.attrib["x"] = "0"
    elif orientation == "up":
        if port == "in1":
            geom.attrib["x"] = fmt((target["w"] - w) / 2)
            geom.attrib["y"] = fmt(target["h"] - h)
        elif port == "out1":
            geom.attrib["x"] = fmt((target["w"] - w) / 2)
            geom.attrib["y"] = "0"
    elif orientation == "down":
        if port == "in1":
            geom.attrib["x"] = fmt((target["w"] - w) / 2)
            geom.attrib["y"] = "0"
        elif port == "out1":
            geom.attrib["x"] = fmt((target["w"] - w) / 2)
            geom.attrib["y"] = fmt(target["h"] - h)


def add_generic_node(root, node):
    g = node["geometry"]
    style = node.get("style", {}).get(
        "mx_style",
        "rounded=0;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;strokeColor=#000000;fillColor=#ffffff;strokeWidth=3;",
    )
    cell = ET.SubElement(root, "mxCell", {"id": node["id"], "value": str(node.get("label", "")), "style": style, "vertex": "1", "parent": "1"})
    ET.SubElement(cell, "mxGeometry", {"x": fmt(g["x"]), "y": fmt(g["y"]), "width": fmt(g["w"]), "height": fmt(g["h"]), "as": "geometry"})


def add_edge(root, edge, port_map, manifest):
    source_node, source_port = endpoint_id(edge["source"])
    target_endpoint = edge.get("target")
    if not target_endpoint:
        targets = edge.get("targets") or []
        target_endpoint = targets[0] if targets else ""
    target_node, target_port = endpoint_id(target_endpoint)
    source_cell = port_map.get(source_node, {}).get(source_port, source_node)
    target_cell = port_map.get(target_node, {}).get(target_port, target_node)
    if source_port and source_node in port_map and source_port not in port_map.get(source_node, {}):
        manifest["warnings"].append({"type": "missing_component_port", "node": source_node, "port": source_port})
    if target_port and target_node in port_map and target_port not in port_map.get(target_node, {}):
        manifest["warnings"].append({"type": "missing_component_port", "node": target_node, "port": target_port})
    route = edge.get("route", {})
    style = route.get(
        "mx_style",
        "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;strokeColor=#000000;strokeWidth=3;",
    )
    cell = ET.SubElement(
        root,
        "mxCell",
        {"id": edge["id"], "value": "", "style": style, "edge": "1", "parent": "1", "source": source_cell, "target": target_cell},
    )
    geom = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    if route.get("source_xy"):
        ET.SubElement(geom, "mxPoint", {"x": fmt(route["source_xy"][0]), "y": fmt(route["source_xy"][1]), "as": "sourcePoint"})
    if route.get("waypoints"):
        arr = ET.SubElement(geom, "Array", {"as": "points"})
        for x, y in route["waypoints"]:
            ET.SubElement(arr, "mxPoint", {"x": fmt(x), "y": fmt(y)})
    if route.get("target_xy"):
        ET.SubElement(geom, "mxPoint", {"x": fmt(route["target_xy"][0]), "y": fmt(route["target_xy"][1]), "as": "targetPoint"})


def materialize(layout_path: Path, catalog_path: Path, output_path: Path, manifest_path: Path):
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    templates, catalog_children = load_catalog(catalog_path)
    mxfile, root = ensure_root()
    id_map = {}
    port_map = {}
    manifest = {
        "status": "generated",
        "layout_spec": layout_path.name,
        "component_catalog": catalog_path.name,
        "component_templates_used": {},
        "node_to_mxcell": {},
        "edge_to_mxcell": {},
        "warnings": [],
    }
    for node in layout.get("nodes", []):
        key = node.get("component_key")
        if key in templates:
            rewrite_subtree(templates[key], catalog_children, node, id_map, port_map, root)
            manifest["component_templates_used"][node["id"]] = key
        else:
            add_generic_node(root, node)
        manifest["node_to_mxcell"][node["id"]] = node["id"]
    for edge in layout.get("edges", []):
        add_edge(root, edge, port_map, manifest)
        manifest["edge_to_mxcell"][edge["id"]] = edge["id"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(mxfile).write(output_path, encoding="utf-8", xml_declaration=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("layout_spec")
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    materialize(Path(args.layout_spec), Path(args.catalog), Path(args.output), Path(args.manifest))


if __name__ == "__main__":
    main()
