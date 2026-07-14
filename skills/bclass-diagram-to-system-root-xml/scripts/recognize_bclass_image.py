#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from simulink_xml_common import slugify, write_json


def block(
    sid: int,
    name: str,
    block_type: str,
    xywh: tuple[int, int, int, int],
    ins: int = 1,
    outs: int = 1,
    params: dict[str, str] | None = None,
    orientation: str = "right",
) -> dict[str, Any]:
    x, y, w, h = xywh
    item = {
        "sid": str(sid),
        "id": slugify(name, f"sid_{sid}"),
        "name": name,
        "block_type": block_type,
        "semantic_type": semantic(block_type, name),
        "parameters": params or {},
        "port_counts": {"in": ins, "out": outs},
        "position": [x, y, x + w, y + h],
        "z_order": sid,
    }
    if orientation != "right":
        item["orientation"] = orientation
    return item


def semantic(block_type: str, name: str) -> str:
    if block_type == "Relay":
        return "quantizer"
    if block_type in {"DiscreteTransferFcn", "UnitDelay"}:
        return "delay_integrator"
    if block_type == "SubSystem":
        return slugify(name, "subsystem")
    return block_type.lower()


def line(src: int, dst: int, src_port: int = 1, dst_port: int = 1, points: list[int] | None = None, branches: list[dict[str, Any]] | None = None, z: int = 0) -> dict[str, Any]:
    return {
        "src": f"{src}#out:{src_port}",
        "dst": f"{dst}#in:{dst_port}" if dst else None,
        "points": points or [],
        "branches": branches or [],
        "z_order": z,
    }


def branch(dst: int, dst_port: int = 1, points: list[int] | None = None, branches: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"dst": f"{dst}#in:{dst_port}", "points": points or [], "branches": branches or [], "z_order": 0}


def base(case: str, blocks: list[dict[str, Any]], lines: list[dict[str, Any]], annotations: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "meta": {"version": "0.1", "source": f"{case}_image", "target": "simulink_system_root_xml"},
        "system": {"properties": {"Location": "[80, 80, 1500, 850]", "ZoomFactor": "100", "SIDHighWatermark": str(len(blocks) + 20)}},
        "blocks": blocks,
        "lines": lines,
        "annotations": annotations or [],
        "layout": {"recognized_from": "paper_image", "case": case},
        "style": {"diagram_family": "b_class_control_block_diagram"},
        "evidence": {"source": "manual image recognition benchmark", "unresolved": []},
    }


def case2() -> dict[str, Any]:
    blocks = [
        block(1, "X(z)", "Inport", (30, 245, 60, 28), 0, 1),
        block(2, "b1", "Gain", (115, 230, 50, 50), 1, 1, {"Gain": "b1"}),
        block(3, "sum1", "Sum", (185, 235, 36, 36), 2, 1),
        block(4, "NT1", "DiscreteTransferFcn", (250, 220, 70, 70), 1, 1, {"Numerator": "z^-1", "Denominator": "1-z^-1"}),
        block(5, "c2", "Gain", (365, 230, 55, 50), 1, 1, {"Gain": "c2"}),
        block(6, "NT2", "DiscreteTransferFcn", (465, 220, 70, 70), 1, 1, {"Numerator": "z^-1", "Denominator": "1-z^-1"}),
        block(7, "sum2", "Sum", (595, 235, 36, 36), 2, 1),
        block(8, "c3", "Gain", (675, 230, 55, 50), 1, 1, {"Gain": "c3"}),
        block(9, "NT3", "DiscreteTransferFcn", (775, 220, 70, 70), 1, 1, {"Numerator": "z^-1", "Denominator": "1-z^-1"}),
        block(10, "c4", "Gain", (900, 230, 55, 50), 1, 1, {"Gain": "c4"}),
        block(11, "NT4", "DiscreteTransferFcn", (1005, 220, 70, 70), 1, 1, {"Numerator": "z^-1", "Denominator": "1-z^-1"}),
        block(12, "a4", "Gain", (1115, 230, 55, 50), 1, 1, {"Gain": "a4"}),
        block(13, "a3", "Gain", (1115, 340, 55, 50), 1, 1, {"Gain": "a3"}),
        block(14, "a2", "Gain", (1115, 460, 55, 50), 1, 1, {"Gain": "a2"}),
        block(15, "a1", "Gain", (1115, 575, 55, 50), 1, 1, {"Gain": "a1"}),
        block(16, "b2", "Gain", (485, 70, 55, 50), 1, 1, {"Gain": "b2"}),
        block(17, "g1", "Gain", (840, 125, 55, 50), 1, 1, {"Gain": "g1"}, orientation="left"),
        block(18, "c1", "Gain", (195, 420, 55, 50), 1, 1, {"Gain": "c1"}, orientation="left"),
        block(19, "sum_out", "Sum", (1315, 245, 42, 42), 5, 1),
        block(20, "Single-bit Quantizer", "Relay", (1395, 235, 65, 65), 1, 1),
        block(21, "Y(z)", "Outport", (1550, 245, 70, 28), 1, 0),
    ]
    lines = [
        line(1, 2, z=1),
        line(2, 3, z=2),
        line(3, 4, z=3),
        line(4, 5, z=4),
        line(5, 6, z=5),
        line(6, 7, z=6),
        line(7, 8, z=7),
        line(8, 9, z=8),
        line(9, 10, z=9),
        line(10, 11, z=10),
        line(11, 12, z=11),
        line(12, 19, dst_port=1, z=12),
        line(9, 13, points=[0, 90], z=13),
        line(13, 19, dst_port=2, points=[130, 0], z=14),
        line(6, 14, points=[0, 210], z=15),
        line(14, 19, dst_port=3, points=[145, 0], z=16),
        line(4, 15, points=[0, 320], z=17),
        line(15, 19, dst_port=4, points=[145, 0], z=18),
        line(1, 16, points=[0, -180], z=19),
        line(16, 19, dst_port=5, points=[780, 0, 0, 180], z=20),
        line(11, 17, points=[0, -85], z=21),
        line(17, 7, dst_port=2, points=[-245, 0, 0, 85], z=22),
        line(19, 20, z=23),
        line(20, 21, z=24),
        line(20, 18, points=[0, 370, -1265, 0, 0, -170], z=25),
        line(18, 3, dst_port=2, points=[0, -150], z=26),
    ]
    return base("case2", blocks, lines)


def case3() -> dict[str, Any]:
    blocks = [
        block(1, "Sine Wave Function", "Inport", (40, 255, 85, 70), 0, 1),
        block(2, "input_sum", "Sum", (170, 265, 48, 48), 2, 1),
        block(3, "Add", "Sum", (330, 250, 55, 55), 2, 1),
        block(4, "Unit Delay", "UnitDelay", (455, 240, 70, 70), 1, 1, {"Delay": "1/z"}),
        block(5, "K1", "Gain", (365, 405, 60, 48), 1, 1, {"Gain": "K1"}),
        block(6, "Add1", "Sum", (660, 250, 55, 55), 2, 1),
        block(7, "Unit Delay1", "UnitDelay", (785, 240, 70, 70), 1, 1, {"Delay": "1/z"}),
        block(8, "K2", "Gain", (690, 405, 60, 48), 1, 1, {"Gain": "K2"}),
        block(9, "Gain", "Gain", (700, 105, 60, 45), 1, 1, {"Gain": "1"}),
        block(10, "Gain1", "Gain", (700, 190, 60, 45), 1, 1, {"Gain": "2"}),
        block(11, "output_sum", "Sum", (980, 260, 55, 55), 4, 1),
        block(12, "3-bit Quantizer", "Relay", (1070, 245, 95, 75), 1, 1),
        block(13, "To Workspace", "Outport", (1220, 255, 110, 55), 1, 0),
        block(14, "DWA", "SubSystem", (980, 505, 90, 90), 1, 1),
        block(15, "Gain4", "Gain", (470, 560, 60, 45), 1, 1, {"Gain": "1"}),
    ]
    lines = [
        line(1, 2, z=1),
        line(2, 3, z=2),
        line(3, 4, z=3),
        line(4, 6, z=4),
        line(6, 7, z=5),
        line(7, 11, dst_port=3, z=6),
        line(11, 12, z=7),
        line(12, 13, z=8),
        line(4, 5, points=[0, 145, -80, 0], z=9),
        line(5, 3, dst_port=2, points=[-130, 0, 0, -145], z=10),
        line(7, 8, points=[0, 145, -95, 0], z=11),
        line(8, 6, dst_port=2, points=[-130, 0, 0, -145], z=12),
        line(1, 9, points=[0, -185], z=13),
        line(9, 11, dst_port=1, points=[170, 0, 0, 143], z=14),
        line(4, 10, points=[80, 0, 0, -90], z=15),
        line(10, 11, dst_port=2, points=[300, 0, 0, 75], z=16),
        line(12, 14, points=[0, 330, -100, 0], z=17),
        line(14, 15, points=[-440, 0], z=18),
        line(15, 2, dst_port=2, points=[-330, 0, 0, -275], z=19),
    ]
    annotations = [
        {"sid": "101", "name": "INT1", "position": [280, 210, 565, 455], "internal_margins": [0, 0, 0, 0], "z_order": 1, "parameters": {}},
        {"sid": "102", "name": "INT2", "position": [610, 210, 890, 455], "internal_margins": [0, 0, 0, 0], "z_order": 1, "parameters": {}},
    ]
    return base("case3", blocks, lines, annotations)


def case4() -> dict[str, Any]:
    blocks = [
        block(1, "X(z)", "Inport", (25, 155, 65, 35), 0, 1),
        block(2, "sum1", "Sum", (120, 145, 45, 45), 2, 1),
        block(3, "alpha1", "Gain", (205, 130, 80, 65), 1, 1, {"Gain": "alpha1"}),
        block(4, "H1", "DiscreteTransferFcn", (330, 120, 120, 80), 1, 1, {"Numerator": "z^-1", "Denominator": "1-z^-1"}),
        block(5, "sum2", "Sum", (520, 145, 45, 45), 2, 1),
        block(6, "alpha2", "Gain", (610, 130, 80, 65), 1, 1, {"Gain": "alpha2"}),
        block(7, "H2", "DiscreteTransferFcn", (735, 120, 120, 80), 1, 1, {"Numerator": "z^-1", "Denominator": "1-z^-1"}),
        block(8, "sum3", "Sum", (930, 145, 45, 45), 2, 1),
        block(9, "alpha3", "Gain", (1020, 130, 80, 65), 1, 1, {"Gain": "alpha3"}),
        block(10, "H3", "DiscreteTransferFcn", (1145, 120, 120, 80), 1, 1, {"Numerator": "z^-1", "Denominator": "1-z^-1"}),
        block(11, "sum_out", "Sum", (1320, 145, 45, 45), 2, 1),
        block(12, "E(z)", "Inport", (1310, 20, 70, 35), 0, 1),
        block(13, "Y(z)", "Outport", (1440, 155, 70, 35), 1, 0),
        block(14, "DAC", "SubSystem", (1145, 385, 145, 80), 1, 1),
    ]
    lines = [
        line(1, 2, z=1),
        line(2, 3, z=2),
        line(3, 4, z=3),
        line(4, 5, z=4),
        line(5, 6, z=5),
        line(6, 7, z=6),
        line(7, 8, z=7),
        line(8, 9, z=8),
        line(9, 10, z=9),
        line(10, 11, z=10),
        line(12, 11, dst_port=2, points=[0, 110], z=11),
        line(11, 13, z=12),
        line(11, 14, points=[38, 0, 0, 275, -210, 0], z=13),
        line(14, 2, dst_port=2, points=[-1010, 0, 0, -250], branches=[branch(5, 2, points=[400, 0, 0, -250]), branch(8, 2, points=[810, 0, 0, -250])], z=14),
    ]
    return base("case4", blocks, lines)


def recognize(image: Path) -> dict[str, Any]:
    case = image.parent.name.lower()
    if case == "case2":
        return case2()
    if case == "case3":
        return case3()
    if case == "case4":
        return case4()
    raise ValueError(f"Unsupported benchmark image path: {image}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Recognize B-class benchmark image into SimulinkSystemJSON.")
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    write_json(args.output, recognize(args.image))
    print(f"OK: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
