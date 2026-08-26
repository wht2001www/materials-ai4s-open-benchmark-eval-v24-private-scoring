#!/usr/bin/env python3
"""Standalone deterministic oracle for one Materials AI4S V24 task.

The file is self-contained: task gold data, scoring rules, tolerances, and input
hashes are embedded at build time. It never imports or executes submission code.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import re
import statistics
import struct
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

TASK_ID = 'MS04-Q2'
REQUIRED_OUTPUTS = ['cif_audit.csv', 'summary.json', 'report.md', 'analyze.py', 'run_log.jsonl', 'algorithm_summary.csv']
MAIN_FILE = 'cif_audit.csv'
EXPECTED_COLUMNS = ['algorithm', 'formula', 'path', 'present', 'parseable', 'formula_match', 'issue_codes']
ORACLE = json.loads('{"coverage":[{"algorithm":"CALYPSO","formula":"Ca3SnO","file_present":true},{"algorithm":"CALYPSO","formula":"Co2Ni2Sn2","file_present":true},{"algorithm":"CALYPSO","formula":"Co2Te2","file_present":true},{"algorithm":"CALYPSO","formula":"Cr6Ga2","file_present":true},{"algorithm":"CALYPSO","formula":"Hf4Mn8","file_present":true},{"algorithm":"CALYPSO","formula":"Hf4Ni2","file_present":true},{"algorithm":"CALYPSO","formula":"HfCo2Sn","file_present":true},{"algorithm":"CALYPSO","formula":"InHg","file_present":true},{"algorithm":"CALYPSO","formula":"Li2CuSn","file_present":true},{"algorithm":"CALYPSO","formula":"LiMg2Ga","file_present":true},{"algorithm":"CALYPSO","formula":"MgCu4Sn","file_present":true},{"algorithm":"CALYPSO","formula":"MgInCu4","file_present":true},{"algorithm":"CALYPSO","formula":"NaGa4","file_present":true},{"algorithm":"CALYPSO","formula":"ScCu","file_present":true},{"algorithm":"CALYPSO","formula":"SrGa4","file_present":true},{"algorithm":"CALYPSO","formula":"SrGaCu2","file_present":true},{"algorithm":"CALYPSO","formula":"Ti2Cd","file_present":true},{"algorithm":"CALYPSO","formula":"TiGa3","file_present":true},{"algorithm":"CALYPSO","formula":"Y3Al9","file_present":true},{"algorithm":"CALYPSO","formula":"YHg2","file_present":true},{"algorithm":"CALYPSO","formula":"Zn2C2O6","file_present":true},{"algorithm":"CALYPSO","formula":"ZnCdPt2","file_present":true},{"algorithm":"CALYPSO","formula":"ZrHg","file_present":true},{"algorithm":"USPEX","formula":"Ca3SnO","file_present":true},{"algorithm":"USPEX","formula":"Co2Ni2Sn2","file_present":true},{"algorithm":"USPEX","formula":"Co2Te2","file_present":true},{"algorithm":"USPEX","formula":"Cr6Ga2","file_present":true},{"algorithm":"USPEX","formula":"Hf4Mn8","file_present":true},{"algorithm":"USPEX","formula":"Hf4Ni2","file_present":true},{"algorithm":"USPEX","formula":"HfCo2Sn","file_present":true},{"algorithm":"USPEX","formula":"InHg","file_present":true},{"algorithm":"USPEX","formula":"Li2CuSn","file_present":true},{"algorithm":"USPEX","formula":"LiMg2Ga","file_present":true},{"algorithm":"USPEX","formula":"MgCu4Sn","file_present":true},{"algorithm":"USPEX","formula":"MgInCu4","file_present":true},{"algorithm":"USPEX","formula":"NaGa4","file_present":true},{"algorithm":"USPEX","formula":"ScCu","file_present":true},{"algorithm":"USPEX","formula":"SrGa4","file_present":true},{"algorithm":"USPEX","formula":"SrGaCu2","file_present":true},{"algorithm":"USPEX","formula":"Ti2Cd","file_present":true},{"algorithm":"USPEX","formula":"TiGa3","file_present":true},{"algorithm":"USPEX","formula":"Y3Al9","file_present":true},{"algorithm":"USPEX","formula":"YHg2","file_present":true},{"algorithm":"USPEX","formula":"Zn2C2O6","file_present":true},{"algorithm":"USPEX","formula":"ZnCdPt2","file_present":true},{"algorithm":"USPEX","formula":"ZrHg","file_present":true}],"expected_rows":46}')
SCORING_SPEC = json.loads('{"type":"archive_audit","invalid_in_denominator":true}')
INPUT_MANIFEST = json.loads('{"question_id":"MS04-Q2","files":[{"path":"inputs/23-predicted-data.zip","bytes":28383,"sha256":"CA645DF91DC07077A4A9458130BAB82CF70DB161D8DA3EAEEB1F5B66465C7642"},{"path":"inputs/metadata.csv","bytes":1212,"sha256":"5AA3B18C6CFD905389743C1A50714F2A1D325A53241BC23568E53F1EAAF552A5"},{"path":"inputs/source_manifest.json","bytes":729,"sha256":"F8858722E8006137394BA569931996F8ACE844D7975B6DB0E32CD01C9AF9CBB0"}]}')
EMBEDDED_ORACLE_SHA256 = '2D6B1205E268D4551508A7DEB5F7AD063A4957EFB04A25B5AEA018A8E9FEA807'
DERIVED_GOLD = json.loads('{}')
MANUAL_TASKS = set()
MANUAL_ANCHORS = json.loads('{}')
REGRESSION_CONFIG = json.loads('{}')
CRITERIA_LAYOUT = [('覆盖矩阵', 30), ('CIF 质检', 25), ('算法汇总', 15), ('复现', 5), ('报告', 5)]

GRADER_VERSION = "v24-standalone-oracle-1.0"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def truthy(value: Any) -> bool:
    return str(value).strip().casefold() in {"1", "true", "yes", "y", "eligible", "valid", "ok"}


def norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


def flatten_strings(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for child in value.values():
            result.extend(flatten_strings(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(flatten_strings(child))
    elif value is not None:
        result.append(str(value))
    return result


def reject_nonfinite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite JSON number")
    if isinstance(value, dict):
        for child in value.values():
            reject_nonfinite(child)
    elif isinstance(value, list):
        for child in value:
            reject_nonfinite(child)


def parse_artifact(path: Path) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("missing or empty")
    suffix = path.suffix.casefold()
    if suffix == ".json":
        reject_nonfinite(read_json(path))
    elif suffix == ".jsonl":
        lines = [line for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        if not lines:
            raise ValueError("empty jsonl")
        for line in lines:
            reject_nonfinite(json.loads(line))
    elif suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            if not reader.fieldnames:
                raise ValueError("missing header")
            list(reader)
    elif suffix == ".png":
        if not valid_png(path):
            raise ValueError("invalid PNG")
    elif suffix == ".py":
        ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
    else:
        path.read_text(encoding="utf-8")


def valid_png(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 33:
        return False
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        return False
    width, height = struct.unpack(">II", data[16:24])
    return width > 0 and height > 0 and data[-12:] == b"\x00\x00\x00\x00IEND\xaeB`\x82"


def criterion(name: str, maximum: float, metric: float, detail: str = "") -> dict[str, Any]:
    metric = max(0.0, min(1.0, float(metric)))
    return {
        "name": name,
        "points": maximum * metric,
        "max_points": float(maximum),
        "metric": metric,
        "detail": detail,
    }


def exact(name: str, maximum: float, correct: int, total: int, detail: str = "") -> dict[str, Any]:
    metric = correct / total if total else 0.0
    return criterion(name, maximum, metric, detail or f"{correct}/{total}")


def set_f1(predicted: set[Any], gold: set[Any]) -> tuple[float, int, int, int]:
    tp = len(predicted & gold)
    denominator = len(predicted) + len(gold)
    return (2 * tp / denominator if denominator else 1.0), tp, len(predicted), len(gold)


def classification_metrics(gold: list[Any], pred: list[Any]) -> tuple[float, float]:
    labels = sorted(set(gold) | set(pred), key=str)
    recalls: list[float] = []
    f1s: list[float] = []
    for label in labels:
        tp = sum(g == label and p == label for g, p in zip(gold, pred))
        fp = sum(g != label and p == label for g, p in zip(gold, pred))
        fn = sum(g == label and p != label for g, p in zip(gold, pred))
        recalls.append(tp / (tp + fn) if tp + fn else 0.0)
        f1s.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
    return (sum(recalls) / len(recalls), sum(f1s) / len(f1s)) if labels else (0.0, 0.0)


def macro_f1(gold: list[Any], pred: list[Any]) -> float:
    return classification_metrics(gold, pred)[1]


def non_o_micro_f1(gold: list[str], pred: list[str]) -> float:
    tp = sum(g == p and g != "O" for g, p in zip(gold, pred))
    fp = sum(p != "O" and p != g for g, p in zip(gold, pred))
    fn = sum(g != "O" and p != g for g, p in zip(gold, pred))
    return 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0


def regression_metrics(gold: list[float], pred: list[float], baseline: float) -> dict[str, float]:
    mae = sum(abs(a - b) for a, b in zip(gold, pred)) / len(gold)
    rmse = math.sqrt(sum((a - b) ** 2 for a, b in zip(gold, pred)) / len(gold))
    baseline_mae = sum(abs(a - baseline) for a in gold) / len(gold)
    mean_gold = sum(gold) / len(gold)
    denominator = sum((a - mean_gold) ** 2 for a in gold)
    r2 = 1.0 - sum((a - b) ** 2 for a, b in zip(gold, pred)) / denominator if denominator else 0.0
    return {
        "mae": mae,
        "rmse": rmse,
        "baseline_mae": baseline_mae,
        "mae_improvement": max(0.0, min(1.0, 1.0 - mae / baseline_mae)) if baseline_mae else 0.0,
        "r2": r2,
        "r2_clipped": max(0.0, min(1.0, r2)),
    }


def linear_quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    low = int(math.floor(position))
    high = int(math.ceil(position))
    if low == high:
        return ordered[low]
    fraction = position - low
    return ordered[low] * (1 - fraction) + ordered[high] * fraction


def formula_counts(formula: str) -> dict[str, float] | None:
    counts: Counter[str] = Counter()
    for element, number in re.findall(r"([A-Z][a-z]?)([0-9.]*)", str(formula)):
        counts[element] += float(number) if number else 1.0
    if not counts:
        return None
    scale = min(value for value in counts.values() if value > 0)
    return {key: round(value / scale, 8) for key, value in sorted(counts.items())}


def report_criterion(output: Path, maximum: float = 5) -> dict[str, Any]:
    path = output / "report.md"
    if not path.is_file():
        return criterion("报告", maximum, 0, "report.md missing")
    text = path.read_text(encoding="utf-8-sig").strip()
    checks = [bool(text), len(text) <= 300]
    return exact("报告", maximum, sum(checks), len(checks), f"nonempty={checks[0]}, chars={len(text)}")


def script_criterion(output: Path, maximum: float) -> tuple[dict[str, Any], list[str]]:
    path = output / "analyze.py"
    checks: list[bool] = []
    failures: list[str] = []
    if not path.is_file():
        return criterion("复现", maximum, 0, "analyze.py missing"), ["SCRIPT_MISSING"]
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename="analyze.py")
        checks.append(True)
        literals = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
        forbidden = any(
            value.startswith(("C:\\", "/Users/", "/home/"))
            or re.search(r"(?:private|oracle|gold|answer|scoring_spec)", value, re.I)
            for value in literals
        )
        checks.append(not forbidden)
        if forbidden:
            failures.append("SCRIPT_FORBIDDEN_REFERENCE")
    except Exception as exc:
        checks.extend([False, False])
        failures.append(f"SCRIPT_SYNTAX:{type(exc).__name__}")
    log_path = output / "run_log.jsonl"
    try:
        parse_artifact(log_path)
        checks.append(True)
    except Exception:
        checks.append(False)
        failures.append("RUN_LOG_INVALID")
    return exact("复现", maximum, sum(checks), len(checks), "static syntax/path/log checks"), failures


def plot_criterion(output: Path, filename: str, maximum: float) -> dict[str, Any]:
    ok = valid_png(output / filename)
    return exact("科研图", maximum, int(ok), 1, f"valid PNG={ok}")


def verify_inputs(workspace: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for record in INPUT_MANIFEST["files"]:
        path = workspace / record["path"]
        if not path.is_file():
            failures.append(f"HG_INPUT_MISSING:{record['path']}")
        elif path.stat().st_size != int(record["bytes"]):
            failures.append(f"HG_INPUT_SIZE:{record['path']}")
        elif sha256_file(path) != record["sha256"].upper():
            failures.append(f"HG_INPUT_HASH:{record['path']}")
    return not failures, failures


def required_artifacts(output: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for name in REQUIRED_OUTPUTS:
        path = output / name
        if not path.is_file():
            failures.append(f"HG_DELIVERABLE_MISSING:{name}")
            continue
        try:
            parse_artifact(path)
        except Exception as exc:
            failures.append(f"HG_DELIVERABLE_INVALID:{name}:{type(exc).__name__}")
    return not failures, failures


def main_csv(workspace: Path) -> tuple[list[dict[str, str]], list[str]]:
    path = workspace / "output" / MAIN_FILE
    if not path.is_file():
        return [], [f"HG_MAIN_MISSING:{MAIN_FILE}"]
    try:
        header, rows = read_csv(path)
    except Exception as exc:
        return [], [f"HG_MAIN_INVALID:{type(exc).__name__}"]
    failures: list[str] = []
    if EXPECTED_COLUMNS and header != EXPECTED_COLUMNS:
        failures.append(f"HG_SCHEMA:{header!r}")
    return rows, failures


def anchor_variants(anchor: Any) -> list[str]:
    values = anchor if isinstance(anchor, list) else [anchor]
    return [norm(value) for value in values if norm(value)]


def anchor_match(anchor: Any, text: str) -> bool:
    normalized = norm(text)
    return any(value in normalized for value in anchor_variants(anchor))


def predicted_numbers(value: Any, parent_key: str = "") -> list[str]:
    if parent_key.casefold() in {"id", "step_id", "index", "order", "rank", "case_id"}:
        return []
    result: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            result.extend(predicted_numbers(child, str(key)))
    elif isinstance(value, list):
        for child in value:
            result.extend(predicted_numbers(child, parent_key))
    elif value is not None:
        result.extend(re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", str(value)))
    return result


def manual_material_items(payload: Any) -> list[str]:
    if isinstance(payload, dict):
        for key in ("materials", "raw_materials", "ingredients", "precursors"):
            if isinstance(payload.get(key), list):
                return [" ".join(flatten_strings(item)) for item in payload[key]]
    if isinstance(payload, list):
        return [" ".join(flatten_strings(item)) for item in payload]
    return []


def score_manual(workspace: Path) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    output = workspace / "output"
    payload = read_json(output / MAIN_FILE)
    reference = MANUAL_ANCHORS
    all_text = " ".join(flatten_strings(payload))
    public_text = " ".join(
        path.read_text(encoding="utf-8-sig", errors="replace")
        for path in (workspace / "inputs").iterdir()
        if path.is_file() and path.suffix.casefold() in {".json", ".txt", ".csv"}
    )
    criteria: list[dict[str, Any]] = []
    failures: list[str] = []
    metrics: dict[str, Any] = {}

    if reference["mode"] in {"materials", "materials_stage"}:
        items = manual_material_items(payload)
        predicted_hits = {i for i, anchor in enumerate(reference["entities"]) if anchor_match(anchor, all_text)}
        predicted_item_matches = sum(any(anchor_match(anchor, item) for anchor in reference["entities"]) for item in items)
        precision_denominator = max(len(items), len(predicted_hits))
        precision = predicted_item_matches / precision_denominator if precision_denominator else 0.0
        recall = len(predicted_hits) / len(reference["entities"])
        entity_f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        criteria.append(criterion("原料实体 F1", reference["weights"][0], entity_f1, f"precision={precision:.6f}, recall={recall:.6f}"))
        role_checks = []
        for entry in reference.get("roles", []):
            role_checks.append(any(anchor_match(entry["entity"], item) and anchor_match(entry["role"], item) for item in items))
        criteria.append(exact("角色 F1", reference["weights"][1], sum(role_checks), len(role_checks), "entity and role co-occur in one material item"))
        if reference["mode"] == "materials_stage":
            stage_checks = []
            for entry in reference.get("stages", []):
                stage_checks.append(any(anchor_match(entry["entity"], item) and anchor_match(entry["stage"], item) for item in items))
            criteria.append(exact("步骤归属", reference["weights"][2], sum(stage_checks), len(stage_checks)))
            restraint_weight = reference["weights"][3]
            format_weight = 0
        else:
            restraint_weight = reference["weights"][2]
            format_weight = reference["weights"][3]
        public_nums = set(predicted_numbers(public_text))
        output_nums = predicted_numbers(payload)
        unsupported = [value for value in output_nums if value not in public_nums]
        restraint = 1.0 - len(unsupported) / max(len(output_nums), 1)
        criteria.append(criterion("缺参克制", restraint_weight, restraint, f"unsupported_numbers={unsupported[:10]}"))
        if format_weight:
            case = read_json(workspace / "inputs" / "case.json")
            schema_checks = [isinstance(payload, dict), bool(items), str(payload.get("case_id", payload.get("id", ""))) in {"", str(case.get("id", ""))}]
            criteria.append(exact("格式与覆盖", format_weight, sum(schema_checks), len(schema_checks)))
        metrics.update({"entity_f1": entity_f1, "unsupported_number_count": len(unsupported)})

    elif reference["mode"] == "procedure":
        steps = payload.get("steps", []) if isinstance(payload, dict) else []
        step_texts = [" ".join(flatten_strings(step)) for step in steps]
        positions: list[int | None] = []
        for anchor in reference["actions"]:
            positions.append(next((index for index, text in enumerate(step_texts) if anchor_match(anchor, text)), None))
        recall = sum(position is not None for position in positions) / len(positions)
        action_weight, order_weight, entity_weight, restraint_weight, format_weight = reference["weights"]
        criteria.append(criterion("关键步骤覆盖", action_weight, recall, f"matched={sum(p is not None for p in positions)}/{len(positions)}"))
        pairs = [(a, b) for a in range(len(positions)) for b in range(a + 1, len(positions)) if positions[a] is not None and positions[b] is not None]
        order_ok = sum(positions[a] < positions[b] for a, b in pairs)
        criteria.append(exact("顺序一致性", order_weight, order_ok, len(pairs), "pairwise order among matched anchors"))
        entity_hits = sum(anchor_match(anchor, all_text) for anchor in reference["entities"])
        criteria.append(exact("材料/条件实体", entity_weight, entity_hits, len(reference["entities"])))
        public_nums = set(predicted_numbers(public_text))
        output_nums = predicted_numbers(payload)
        unsupported = [value for value in output_nums if value not in public_nums]
        restraint = 1.0 - len(unsupported) / max(len(output_nums), 1)
        criteria.append(criterion("缺参克制", restraint_weight, restraint, f"unsupported_numbers={unsupported[:10]}"))
        schema_checks = [isinstance(payload, dict), isinstance(steps, list), bool(steps), len(step_texts) == len(steps)]
        criteria.append(exact("复现与格式", format_weight, sum(schema_checks), len(schema_checks)))
        metrics.update({"action_recall": recall, "pairwise_order_accuracy": order_ok / len(pairs) if pairs else 0.0, "unsupported_number_count": len(unsupported)})

    else:  # characterization
        methods = sum(anchor_match(anchor, all_text) for anchor in reference["methods"])
        conclusions = sum(anchor_match(anchor, all_text) for anchor in reference["conclusions"])
        method_weight, conclusion_weight, separation_weight, format_weight = reference["weights"]
        criteria.append(exact("表征项目召回", method_weight, methods, len(reference["methods"])))
        criteria.append(exact("定性结论一致性", conclusion_weight, conclusions, len(reference["conclusions"])))
        lower = all_text.casefold()
        separation_terms = ["predict", "expected", "inferred", "hypothesis", "待验证", "预测", "推断"]
        separation = sum(term in lower for term in separation_terms)
        criteria.append(criterion("事实/预测分层", separation_weight, 1.0 if separation else 0.0, "prediction boundary markers"))
        criteria.append(criterion("覆盖与格式", format_weight, 1.0 if isinstance(payload, dict) and payload else 0.0))
        metrics.update({"method_recall": methods / len(reference["methods"]), "conclusion_recall": conclusions / len(reference["conclusions"])})

    criteria.append(report_criterion(output, 5))
    if sum(item["max_points"] for item in criteria) != 80:
        raise ValueError("manual criteria do not sum to 80")
    return criteria, failures, metrics


def ie_entity_signature(entity: dict[str, Any]) -> tuple[int, int, str]:
    return int(entity["start"]), int(entity["end"]), norm(entity["type"])


def extract_bio_entities(rows: list[dict[str, Any]], label_key: str) -> set[tuple[str, int, int, str]]:
    result: set[tuple[str, int, int, str]] = set()
    current: tuple[str, int, int, str] | None = None
    for row in rows:
        sid = str(row["sentence_id"])
        tid = int(row["token_id"])
        label = str(row.get(label_key, ""))
        if label == "O" or not label:
            if current:
                result.add(current)
                current = None
            continue
        prefix, kind = label.split("-", 1) if "-" in label else ("B", label)
        if prefix == "B" or current is None or current[0] != sid or current[3] != norm(kind) or tid != current[2] + 1:
            if current:
                result.add(current)
            current = (sid, tid, tid, norm(kind))
        else:
            current = (current[0], current[1], tid, current[3])
    if current:
        result.add(current)
    return result


def score_task(workspace: Path) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    output = workspace / "output"
    qid = TASK_ID
    failures: list[str] = []
    metrics: dict[str, Any] = {}

    if qid in MANUAL_TASKS:
        return score_manual(workspace)

    rows, schema_failures = main_csv(workspace) if MAIN_FILE.endswith(".csv") else ([], [])
    failures.extend(schema_failures)

    if qid == "MS01-Q1":
        gold = set(ORACLE["eligible_ids"])
        candidates = read_csv(workspace / "inputs" / "candidates.csv")[1]
        expected_ids = [row["material_id"] for row in candidates]
        by_id = {row.get("material_id", ""): row for row in rows}
        correct = sum(mid in by_id and truthy(by_id[mid].get("eligible")) == (mid in gold) for mid in expected_ids)
        ranked = sorted((row for row in rows if str(row.get("rank", "")).strip()), key=lambda row: int(float(row["rank"])))
        top = [row["material_id"] for row in ranked[:20]]
        rank_correct = sum(a == b for a, b in zip(top, ORACLE["top20"]))
        format_checks = [set(by_id) == set(expected_ids), len(by_id) == len(rows), not schema_failures]
        script, script_failures = script_criterion(output, 5)
        failures.extend(script_failures)
        criteria = [exact("硬约束判定", 40, correct, len(expected_ids)), exact("Top-k 排序", 20, rank_correct, 20), exact("格式与覆盖", 10, sum(format_checks), len(format_checks)), script, report_criterion(output)]
        if correct != len(expected_ids): failures.append("HG_HARD_CONSTRAINT_MISMATCH")
        if not all(format_checks): failures.append("HG_ID_COVERAGE")
        metrics.update({"eligibility_accuracy": correct / len(expected_ids), "top20_position_accuracy": rank_correct / 20})

    elif qid == "MS01-Q2":
        gold_rows = {row["jid"]: row for row in ORACLE["rows"]}
        pred = {row.get("jid", ""): row for row in rows}
        class_ok = sum(pred.get(jid, {}).get("stability_class") == gold["stability_class"] for jid, gold in gold_rows.items())
        ranked = [row["jid"] for row in sorted(rows, key=lambda row: int(float(row["rank"]))) if row.get("rank")]
        rank_ok = sum(a == b for a, b in zip(ranked, ORACLE["ranked_ids"]))
        summary = read_json(output / "summary.json")
        expected_counts = Counter(row["stability_class"] for row in ORACLE["rows"])
        flat_summary = flatten_strings(summary)
        count_ok = sum(str(value) in flat_summary for value in expected_counts.values())
        script, sf = script_criterion(output, 5); failures.extend(sf)
        criteria = [exact("稳定性分级", 35, class_ok, len(gold_rows)), exact("全量排名", 25, rank_ok, len(ORACLE["ranked_ids"])), exact("汇总", 10, count_ok, len(expected_counts)), script, report_criterion(output)]
        if set(pred) != set(gold_rows): failures.append("HG_ID_COVERAGE")
        metrics.update({"classification_accuracy": class_ok / len(gold_rows), "rank_position_accuracy": rank_ok / len(ORACLE["ranked_ids"])})

    elif qid == "MS01-Q3":
        pred = {str(row.get("sample_id", "")): row for row in rows}
        gold_rows = ORACLE["test_labels"]
        ids = [str(row["sample_id"]) for row in gold_rows]
        gold = [int(row["gfa"]) for row in gold_rows]
        predicted = [int(float(pred.get(sid, {}).get("gfa_pred", -99))) for sid in ids]
        ba, mf1 = classification_metrics(gold, predicted)
        coverage = sum(sid in pred and finite(pred[sid].get("gfa_probability")) and 0 <= float(pred[sid]["gfa_probability"]) <= 1 for sid in ids)
        cv = read_json(output / "cv_metrics.json")
        protocol = [int(cv.get("n_splits", 0)) == 5, cv.get("seed") is not None, "strat" in str(cv.get("splitter", "")).casefold()]
        script, sf = script_criterion(output, 5); failures.extend(sf)
        criteria = [criterion("隐藏测试 balanced accuracy", 30, ba), criterion("隐藏测试 macro-F1", 20, mf1), exact("概率与覆盖", 10, coverage, len(ids)), exact("交叉验证协议", 10, sum(protocol), len(protocol)), script, report_criterion(output)]
        if coverage != len(ids) or len(rows) != len(ids) or len(pred) != len(ids): failures.append("HG_ID_OR_PROBABILITY")
        metrics.update({"balanced_accuracy": ba, "macro_f1": mf1})

    elif qid == "MS02-Q3":
        payload = read_json(output / "extraction.json")
        gold_entities = {(int(ORACLE["t_span_dict"][key][0]), int(ORACLE["t_span_dict"][key][1]), norm(ORACLE["t_type_dict"][key])) for key in ORACLE["t_type_dict"]}
        pred_entities = {ie_entity_signature(entity) for entity in payload.get("entities", [])}
        ef1, etp, ep, eg = set_f1(pred_entities, gold_entities)
        pred_by_id = {entity["id"]: ie_entity_signature(entity) for entity in payload.get("entities", [])}
        gold_t = {key: (int(ORACLE["t_span_dict"][key][0]), int(ORACLE["t_span_dict"][key][1]), norm(ORACLE["t_type_dict"][key])) for key in ORACLE["t_type_dict"]}
        gold_event_node = {key: ("event", norm(ORACLE["e_type_dict"][key]), gold_t[ORACLE["e_trig_dict"][key]]) for key in ORACLE["e_type_dict"]}
        def gold_node(node: str) -> Any:
            return gold_t[node] if node.startswith("T") else gold_event_node.get(node, ("unknown", node))
        gold_rel = {(norm(ORACLE["r_type_dict"][key]), gold_node(ORACLE["r_args_dict"][key][0]), gold_node(ORACLE["r_args_dict"][key][1])) for key in ORACLE["r_type_dict"]}
        pred_rel = {(norm(rel["type"]), pred_by_id.get(rel["head"], ("missing", rel["head"])), pred_by_id.get(rel["tail"], ("missing", rel["tail"]))) for rel in payload.get("relations", [])}
        rf1, rtp, rp, rg = set_f1(pred_rel, gold_rel)
        gold_events = set()
        for key in ORACLE["e_type_dict"]:
            args = tuple(sorted((norm(role), gold_t[target]) for role, target in ORACLE["e_args_dict"][key]))
            gold_events.add((norm(ORACLE["e_type_dict"][key]), gold_t[ORACLE["e_trig_dict"][key]], args))
        pred_events = set()
        for event in payload.get("events", []):
            args = tuple(sorted((norm(arg["role"]), pred_by_id.get(arg["entity_id"], ("missing", arg["entity_id"]))) for arg in event.get("arguments", [])))
            pred_events.add((norm(event["type"]), pred_by_id.get(event["trigger"], ("missing", event["trigger"])), args))
        vf1, vtp, vp, vg = set_f1(pred_events, gold_events)
        text = (workspace / "inputs" / "procedure.txt").read_text(encoding="utf-8")
        entities = payload.get("entities", [])
        valid = sum(0 <= int(entity["start"]) < int(entity["end"]) <= len(text) and text[int(entity["start"]):int(entity["end"])] == entity.get("text") for entity in entities)
        schema = [valid == len(entities), len(pred_by_id) == len(entities), all(rel.get("head") in pred_by_id and rel.get("tail") in pred_by_id for rel in payload.get("relations", [])), all(event.get("trigger") in pred_by_id and all(arg.get("entity_id") in pred_by_id for arg in event.get("arguments", [])) for event in payload.get("events", []))]
        criteria = [criterion("实体 span/type F1", 30, ef1), criterion("关系 F1", 15, rf1), criterion("事件 trigger/argument F1", 20, vf1), exact("offset 与 schema", 10, sum(schema), len(schema)), report_criterion(output)]
        if not all(schema): failures.append("HG_OFFSET_OR_SCHEMA")
        metrics.update({"entity_f1": ef1, "relation_f1": rf1, "event_f1": vf1, "entity_tp": etp, "relation_tp": rtp, "event_tp": vtp})

    elif qid == "MS03-Q1":
        pred = {row.get("sample_id", ""): row for row in rows}
        labels = ORACLE["test_labels"]
        correct = sum(str(pred.get(row["sample_id"], {}).get("space_group_number")) == str(row["space_group_number"]) and pred.get(row["sample_id"], {}).get("space_group_symbol") == row["space_group_symbol"] for row in labels)
        peaks_header, peaks_rows = read_csv(output / "peaks.csv")
        expected = {(row["sample_id"], str(row["point_id"])): row for row in DERIVED_GOLD["peaks"]}
        actual = {(row.get("sample_id", ""), str(int(float(row.get("point_id", -1))))): row for row in peaks_rows}
        union = set(expected) | set(actual)
        peak_ok = 0
        for key in union:
            if key in expected and key in actual:
                peak_ok += all(finite(actual[key].get(field)) and abs(float(actual[key][field]) - float(expected[key][field])) <= 1e-6 for field in ("x", "intensity", "relative_intensity"))
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("空间群准确率", 35, correct, len(labels)), exact("峰位与强度", 20, peak_ok, len(union)), plot_criterion(output, "patterns.png", 10), script, report_criterion(output)]
        if set(pred) != {row["sample_id"] for row in labels}: failures.append("HG_ID_COVERAGE")
        metrics.update({"space_group_accuracy": correct / len(labels), "peak_exact_accuracy": peak_ok / len(union) if union else 0})

    elif qid == "MS03-Q2":
        pred = {(str(row.get("sentence_id", "")), str(row.get("token_id", ""))): row.get("tag", "") for row in rows}
        gold_rows = ORACLE["test_tags"]
        keys = [(str(row["sentence_id"]), str(row["token_id"])) for row in gold_rows]
        gold = [row["tag"] for row in gold_rows]
        predicted = [pred.get(key, "__MISSING__") for key in keys]
        mf1 = macro_f1(gold, predicted); nono = non_o_micro_f1(gold, predicted)
        coverage = sum(key in pred for key in keys)
        cv = read_json(output / "cv_metrics.json")
        protocol = [int(cv.get("n_splits", 0)) == 5, "groupkfold" in str(cv.get("splitter", "")).casefold(), "sentence" in str(cv.get("splitter", "")).casefold()]
        criteria = [criterion("token macro-F1", 35, mf1), criterion("非 O micro-F1", 20, nono), exact("覆盖与对齐", 10, coverage, len(keys)), exact("验证协议", 10, sum(protocol), len(protocol)), report_criterion(output)]
        if coverage != len(keys) or len(pred) != len(keys): failures.append("HG_TOKEN_ALIGNMENT")
        metrics.update({"macro_f1": mf1, "non_o_micro_f1": nono})

    elif qid == "MS03-Q3":
        by = {row.get("feature", ""): row for row in rows}
        features = ["n_sites", "volume_a3"]
        corr = sum(feature in by and finite(by[feature].get("pearson_r")) and abs(float(by[feature]["pearson_r"]) - float(ORACLE[f"pearson_{'volume' if feature == 'volume_a3' else 'n_sites'}"])) <= 1e-6 for feature in features)
        ci_ok = 0
        for feature in features:
            expected = DERIVED_GOLD["bootstrap_ci"][feature]
            row = by.get(feature, {})
            ci_ok += finite(row.get("ci_low")) and abs(float(row["ci_low"]) - expected[0]) <= 1e-6
            ci_ok += finite(row.get("ci_high")) and abs(float(row["ci_high"]) - expected[1]) <= 1e-6
        summary = read_json(output / "summary.json")
        audit = [all(feature in by for feature in features), all(int(float(by[feature].get("n", -1))) == int(ORACLE["n"]) for feature in features if feature in by), bool(summary), all(finite(by[feature].get(field)) for feature in features if feature in by for field in ("pearson_r", "spearman_rho", "ci_low", "ci_high"))]
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("相关系数", 30, corr, 2), exact("bootstrap 区间", 15, ci_ok, 4), exact("数据审计", 10, sum(audit), len(audit)), plot_criterion(output, "association.png", 10), script, report_criterion(output)]
        if not all(audit): failures.append("HG_DATA_AUDIT")
        metrics.update({"pearson_checks": corr, "bootstrap_ci_checks": ci_ok})

    elif qid == "MS04-Q1":
        pred = {row.get("structure", "").replace("_pred.cif", ""): row for row in rows}
        fields = ["wyckoff_rmse", "wyckoff_mae", "sinkhorn_dist", "chamfer_dist", "hausdorff_dist", "superpose_rmsd", "edit_graph_distance", "fingerPrint", "XRD_dist", "OFM_dist"]
        correct = 0
        for gold in ORACLE["distance_rows"]:
            key = gold["structure"].replace("_pred.cif", "")
            row = pred.get(key, {})
            try:
                status_map = json.loads(row.get("status", "{}"))
            except (TypeError, ValueError, json.JSONDecodeError):
                status_map = {}
            for field in fields:
                gv, pv = gold.get(field), row.get(field)
                if finite(gv):
                    correct += finite(pv) and abs(float(gv) - float(pv)) <= 1e-4
                else:
                    # Official CSPBenchMetrics may mark dependency-bound metrics
                    # unavailable. A blank value with an explicit per-field status
                    # is the exact expected representation; fabricated zero is not.
                    correct += not finite(pv) and bool(str(status_map.get(field, "")).strip())
        coverage = []
        for key in ("SrTiO3", "GdB2"):
            row = pred.get(key, {})
            try:
                status_map = json.loads(row.get("status", "{}"))
            except (TypeError, ValueError, json.JSONDecodeError):
                status_map = {}
            coverage.append(key in pred and all(field in row for field in fields) and all(field in status_map for field in fields))
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("官方距离复现", 55, correct, len(fields) * 2), exact("状态与覆盖", 10, sum(coverage), len(coverage)), script, report_criterion(output)]
        if not all(coverage): failures.append("HG_DISTANCE_STATUS_OR_COVERAGE")
        metrics.update({"distance_field_accuracy": correct / (len(fields) * 2)})

    elif qid == "MS04-Q2":
        pred = {(row.get("algorithm", ""), row.get("formula", "")): row for row in rows}
        coverage_gold = ORACLE["coverage"]
        coverage_ok = sum((gold["algorithm"], gold["formula"]) in pred and truthy(pred[(gold["algorithm"], gold["formula"])].get("present")) == bool(gold["file_present"]) for gold in coverage_gold)
        audit_checks: list[bool] = []
        for gold in coverage_gold:
            row = pred.get((gold["algorithm"], gold["formula"]), {})
            audit_checks.extend([bool(row.get("path")), str(row.get("parseable", "")).casefold() in {"true", "false"}, str(row.get("formula_match", "")).casefold() in {"true", "false"}])
        _, summaries = read_csv(output / "algorithm_summary.csv")
        sum_checks: list[bool] = []
        for summary in summaries:
            group = [row for row in rows if row.get("algorithm") == summary.get("algorithm")]
            sum_checks.extend([int(float(summary.get("denominator", -1))) == 23, int(float(summary.get("present_count", summary.get("present", -1)))) == sum(truthy(row.get("present")) for row in group), int(float(summary.get("parseable_count", summary.get("parseable", -1)))) == sum(truthy(row.get("parseable")) for row in group), int(float(summary.get("formula_match_count", summary.get("formula_match", -1)))) == sum(truthy(row.get("formula_match")) for row in group)])
        script, sf = script_criterion(output, 5); failures.extend(sf)
        criteria = [exact("覆盖矩阵", 30, coverage_ok, int(ORACLE["expected_rows"])), exact("CIF 质检", 25, sum(audit_checks), len(audit_checks)), exact("算法汇总", 15, sum(sum_checks), len(sum_checks)), script, report_criterion(output)]
        if coverage_ok != int(ORACLE["expected_rows"]) or len(rows) != int(ORACLE["expected_rows"]): failures.append("HG_FIXED_DENOMINATOR_OR_COVERAGE")
        metrics.update({"coverage_accuracy": coverage_ok / int(ORACLE["expected_rows"])})

    elif qid == "MS04-Q3":
        pred = {row.get("material_id", ""): row for row in rows}
        parse_checks: list[bool] = []; error_checks: list[bool] = []; cif_checks: list[bool] = []
        for gold in ORACLE["rows"]:
            row = pred.get(gold["material_id"], {})
            parse_checks.extend([formula_counts(row.get("formula_from_sites", "")) == formula_counts(gold["formula_from_sites"]), str(row.get("n_sites")) == str(gold["n_sites"]), finite(row.get("structure_volume_a3")) and abs(float(row["structure_volume_a3"]) - float(gold["volume_a3"])) <= 1e-6])
            error_checks.extend([finite(row.get("record_volume_a3")) and abs(float(row["record_volume_a3"]) - float(gold["record_volume"])) <= 1e-6, finite(row.get("volume_abs_error")) and abs(float(row["volume_abs_error"]) - float(gold["volume_abs_error"])) <= 1e-6])
            cif_checks.extend([truthy(row.get("cif_parseable")), not str(row.get("issue_codes", "")).strip()])
        script, sf = script_criterion(output, 5); failures.extend(sf)
        coverage = [set(pred) == {row["material_id"] for row in ORACLE["rows"]}, len(rows) == len(ORACLE["rows"]), not schema_failures]
        criteria = [exact("结构解析", 30, sum(parse_checks), len(parse_checks)), exact("一致性误差", 20, sum(error_checks), len(error_checks)), exact("CIF 质检", 15, sum(cif_checks), len(cif_checks)), exact("覆盖与格式", 5, sum(coverage), len(coverage)), script, report_criterion(output)]
        if not all(coverage): failures.append("HG_ID_COVERAGE")
        metrics.update({"structure_parse_accuracy": sum(parse_checks) / len(parse_checks)})

    elif qid == "MS05-Q3":
        pred = {(str(row.get("sentence_id", "")), str(row.get("token_id", ""))): row for row in rows}
        gold_rows = ORACLE["test_labels"]
        keys = [(str(row["sentence_id"]), str(row["token_id"])) for row in gold_rows]
        gt = [row["token_label"] for row in gold_rows]; pt = [pred.get(key, {}).get("token_label", "__MISSING__") for key in keys]
        gs = [row["slot_label"] for row in gold_rows]; ps = [pred.get(key, {}).get("slot_label", "__MISSING__") for key in keys]
        token_f1 = macro_f1(gt, pt); slot_f1 = macro_f1(gs, ps)
        gold_entities = extract_bio_entities(gold_rows, "slot_label"); pred_entities = extract_bio_entities(rows, "slot_label")
        entity_f1, tp, npred, ngold = set_f1(pred_entities, gold_entities)
        coverage = sum(key in pred for key in keys)
        criteria = [criterion("token label F1", 25, token_f1), criterion("slot label F1", 30, slot_f1), criterion("实体 span F1", 10, entity_f1, f"TP={tp}, pred={npred}, gold={ngold}"), exact("覆盖与对齐", 10, coverage, len(keys)), report_criterion(output)]
        if coverage != len(keys) or len(pred) != len(keys): failures.append("HG_TOKEN_ALIGNMENT")
        metrics.update({"token_macro_f1": token_f1, "slot_macro_f1": slot_f1, "entity_f1": entity_f1})

    elif qid in {"MS06-Q1", "MS08-Q1", "MS09-Q1", "MS09-Q3"}:
        config = REGRESSION_CONFIG[qid]
        pred = {str(row.get(config["id_key"], "")): row for row in rows}
        gold_rows = ORACLE["test_labels"]
        ids = [str(row[config["id_key"]]) for row in gold_rows]
        gold = [float(row[config["gold_col"]]) for row in gold_rows]
        values: list[float] = []
        valid = 0
        for sid in ids:
            value = pred.get(sid, {}).get(config["pred_col"])
            if finite(value) and float(value) >= 0:
                values.append(float(value)); valid += 1
            else:
                values.append(float("nan"))
        if valid == len(ids):
            train_rows = read_csv(workspace / "inputs" / "train.csv")[1]
            baseline = statistics.median(float(row[config["train_col"]]) for row in train_rows)
            reg = regression_metrics(gold, values, baseline)
        else:
            reg = {"mae": float("inf"), "rmse": float("inf"), "baseline_mae": 0.0, "mae_improvement": 0.0, "r2": float("-inf"), "r2_clipped": 0.0}
        criteria = [criterion(config["mae_name"], config["mae_weight"], reg["mae_improvement"], f"MAE={reg['mae']}, baseline_MAE={reg['baseline_mae']}")]
        if config["r2_weight"]:
            criteria.append(criterion("隐藏测试 R²", config["r2_weight"], reg["r2_clipped"], f"R2={reg['r2']}"))
        criteria.append(exact(config["coverage_name"], config["coverage_weight"], valid, len(ids)))
        if qid == "MS09-Q3":
            protocol = read_json(output / "ood_protocol.json")
            checks = [str(protocol.get("preprocessing_fit_scope", protocol.get("preprocessing_fit", ""))).replace("_", " ").casefold() == "train only", str(protocol.get("model_fit_scope", "train only" if protocol.get("test_used_for_tuning") is False else "")).replace("_", " ").casefold() == "train only", protocol.get("ood_test_used_for_tuning", protocol.get("test_used_for_tuning")) is False, int(protocol.get("train_rows", -1)) == 700, int(protocol.get("ood_test_rows", protocol.get("ood_rows", -1))) == 180]
            criteria.append(exact("OOD 协议", 15, sum(checks), len(checks)))
            cv_weight = 10
        else:
            cv_weight = config["protocol_weight"]
        cv = read_json(output / "cv_metrics.json") if (output / "cv_metrics.json").is_file() else {}
        cv_checks = [int(cv.get("n_splits", 0)) == 5, cv.get("seed") is not None, "fold" in str(cv.get("splitter", "")).casefold()]
        criteria.append(exact("训练 CV" if qid == "MS09-Q3" else "验证协议", cv_weight, sum(cv_checks), len(cv_checks)))
        if config["plot_weight"]:
            criteria.append(plot_criterion(output, "parity.png", config["plot_weight"]))
        if config["repro_weight"]:
            script, sf = script_criterion(output, config["repro_weight"]); criteria.append(script); failures.extend(sf)
        criteria.append(report_criterion(output))
        if valid != len(ids) or len(pred) != len(ids): failures.append("HG_ID_OR_NUMERIC_RANGE")
        metrics.update(reg)

    elif qid == "MS06-Q2":
        pred = {str(row.get("sample_id", "")): row for row in rows}
        numeric: list[bool] = []; classes: list[bool] = []
        for gold in ORACLE["rows"]:
            row = pred.get(str(gold["sample_id"]), {})
            numeric.extend([finite(row.get("k_gpa")) and abs(float(row["k_gpa"]) - gold["k_gpa"]) <= 1e-6 * max(abs(gold["k_gpa"]), 1), finite(row.get("g_gpa")) and abs(float(row["g_gpa"]) - gold["g_gpa"]) <= 1e-6 * max(abs(gold["g_gpa"]), 1), finite(row.get("pugh_k_over_g")) and abs(float(row["pugh_k_over_g"]) - gold["pugh_k_over_g"]) <= 1e-6 * max(abs(gold["pugh_k_over_g"]), 1)])
            classes.append(row.get("class") == gold["class"])
        expected = [str(row["sample_id"]) for row in sorted(ORACLE["rows"], key=lambda row: (-row["pugh_k_over_g"], str(row["sample_id"])))]
        actual = [row["sample_id"] for row in sorted(rows, key=lambda row: int(float(row["rank"]))) if row.get("rank")]
        rank = sum(a == b for a, b in zip(actual, expected))
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("K/G 数值", 40, sum(numeric), len(numeric)), exact("类别", 15, sum(classes), len(classes)), exact("排名", 10, rank, len(expected)), script, report_criterion(output)]
        if set(pred) != {str(row["sample_id"]) for row in ORACLE["rows"]}: failures.append("HG_ID_COVERAGE")
        metrics.update({"numeric_accuracy": sum(numeric) / len(numeric), "class_accuracy": sum(classes) / len(classes)})

    elif qid == "MS06-Q3":
        pred = {row.get("jid", ""): row for row in rows}
        status: list[bool] = []; ratio: list[bool] = []; classes: list[bool] = []
        for gold in ORACLE["rows"]:
            row = pred.get(gold["jid"], {})
            valid = gold["status"] == "ok"
            status.append((row.get("status") == "valid") if valid else row.get("status") == gold["status"])
            if valid:
                ratio.append(finite(row.get("pugh_k_over_g")) and abs(float(row["pugh_k_over_g"]) - gold["pugh_k_over_g"]) <= 1e-8 * max(abs(gold["pugh_k_over_g"]), 1))
                classes.append(row.get("proxy_class") == ("ductile_proxy" if gold["pugh_k_over_g"] >= 1.75 else "brittle_proxy"))
        valid_gold = [row for row in ORACLE["rows"] if row["status"] == "ok"]
        expected = [row["jid"] for row in sorted(valid_gold, key=lambda row: (-row["pugh_k_over_g"], row["jid"]))]
        actual = [row["jid"] for row in sorted((row for row in rows if row.get("rank")), key=lambda row: int(float(row["rank"])))]
        rank = sum(a == b for a, b in zip(actual, expected))
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("物理有效性", 25, sum(status), len(status)), exact("K/G 与类别", 30, sum(ratio) + sum(classes), len(ratio) + len(classes)), exact("稳定排名", 10, rank, len(expected)), script, report_criterion(output)]
        if not all(status): failures.append("HG_PHYSICS_GATE")
        metrics.update({"status_accuracy": sum(status) / len(status), "valid_rank_accuracy": rank / len(expected)})

    elif qid == "MS08-Q2":
        pred = {row.get("material_id", ""): row for row in rows}
        gold_rows = ORACLE["test_labels"]
        ids = [row["material_id"] for row in gold_rows]
        gold = [float(row["band_gap"]) for row in gold_rows]
        a = [float(pred[sid]["pred_formula_only_ev"]) for sid in ids]
        b = [float(pred[sid]["pred_formula_description_ev"]) for sid in ids]
        train = read_csv(workspace / "inputs" / "train.csv")[1]
        baseline = statistics.median(float(row["band_gap"]) for row in train)
        ma = regression_metrics(gold, a, baseline); mb = regression_metrics(gold, b, baseline)
        summary = read_json(output / "summary.json")
        stated = summary.get("mean_abs_A_B_difference")
        actual_diff = sum(abs(x - y) for x, y in zip(a, b)) / len(a)
        checks = [set(pred) == set(ids), len(rows) == len(ids), all(finite(value) and value >= 0 for value in a + b), stated is not None and abs(float(stated) - actual_diff) <= 1e-12]
        cv = read_json(output / "cv_metrics.json")
        protocol = [cv.get("same_folds", cv.get("same_split")) is True, cv.get("seed") is not None, cv.get("model_b_oof_mae") is not None]
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [criterion("B 模型隐藏 MAE", 25, mb["mae_improvement"]), criterion("A 模型隐藏 MAE", 15, ma["mae_improvement"]), exact("A/B 差异与覆盖", 10, sum(checks), len(checks)), exact("消融协议", 15, sum(protocol), len(protocol)), script, report_criterion(output)]
        if not all(checks[:3]): failures.append("HG_PAIRED_ID_OR_RANGE")
        metrics.update({"mae_a": ma["mae"], "mae_b": mb["mae"], "delta_mae_b_minus_a": mb["mae"] - ma["mae"]})

    elif qid == "MS08-Q3":
        pred = {row.get("jid", ""): row for row in rows}
        fields = ["n_points", "peak_point_id", "peak_value", "mean", "std", "auc"]
        checks: list[bool] = []
        for gold in DERIVED_GOLD["rows"]:
            row = pred.get(gold["jid"], {})
            for field in fields:
                if field in {"n_points", "peak_point_id"}:
                    checks.append(str(int(float(row.get(field, -1)))) == str(int(gold[field])))
                else:
                    checks.append(finite(row.get(field)) and abs(float(row[field]) - float(gold[field])) <= 1e-8)
        expected = [row["jid"] for row in sorted(DERIVED_GOLD["rows"], key=lambda row: (-row["peak_value"], row["jid"]))]
        actual = [row["jid"] for row in sorted(rows, key=lambda row: int(float(row["rank"]))) if row.get("rank")]
        rank = sum(a == b for a, b in zip(actual, expected))
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("谱统计", 40, sum(checks), len(checks)), exact("峰值与排名", 15, rank, len(expected)), plot_criterion(output, "dielectric_spectra.png", 10), script, report_criterion(output)]
        if set(pred) != set(expected): failures.append("HG_SPECTRUM_COVERAGE")
        metrics.update({"spectral_field_accuracy": sum(checks) / len(checks), "rank_accuracy": rank / len(expected)})

    elif qid == "MS09-Q2":
        pred = {row.get("jid", ""): row for row in rows}
        gold = ORACLE["valid_ranked"]
        audit = sum(gold_row["jid"] in pred and pred[gold_row["jid"]].get("status") == "valid" and finite(pred[gold_row["jid"]].get("heat_capacity")) and abs(float(pred[gold_row["jid"]]["heat_capacity"]) - gold_row["heat_capacity"]) <= 1e-10 for gold_row in gold)
        expected = [row["jid"] for row in gold]
        actual = [row["jid"] for row in sorted(rows, key=lambda row: int(float(row["rank"]))) if row.get("rank")]
        rank = sum(a == b for a, b in zip(actual, expected))
        summary = read_json(output / "summary.json")
        quantile_checks = 0
        for key, value in DERIVED_GOLD["quantiles"].items():
            actual_value = summary.get("quantiles", {}).get(key)
            quantile_checks += actual_value is not None and abs(float(actual_value) - value) <= 1e-10
        script, sf = script_criterion(output, 5); failures.extend(sf)
        criteria = [exact("物理审计", 25, audit, len(gold)), exact("排名", 30, rank, len(expected)), exact("统计汇总", 15, quantile_checks, len(DERIVED_GOLD["quantiles"])), script, report_criterion(output)]
        if audit != len(gold): failures.append("HG_INVALID_INCLUDED_OR_VALUE_CHANGED")
        metrics.update({"valid_value_accuracy": audit / len(gold), "rank_accuracy": rank / len(expected)})

    elif qid.startswith("MS10-"):
        audit = read_json(output / "safety_audit.json")
        predicted_flags = {flag.get("code", ""): flag for flag in audit.get("flags", [])}
        gold_flags = {flag["code"]: flag for flag in ORACLE["flags"]}
        code_tp = len(set(predicted_flags) & set(gold_flags))
        code_f1, _, _, _ = set_f1(set(predicted_flags), set(gold_flags))
        procedure = (workspace / "inputs" / "procedure.txt").read_text(encoding="utf-8")
        evidence_total = 0; evidence_ok = 0
        all_evidence: list[str] = []
        for flag in audit.get("flags", []):
            all_evidence.extend(flatten_strings(flag))
        for code, gold_flag in gold_flags.items():
            predicted_text = " ".join(flatten_strings(predicted_flags.get(code, {})))
            for hit in gold_flag["hits"]:
                evidence_total += 1
                positions = [match.start() for match in re.finditer(re.escape(str(hit)), procedure, re.I)]
                text_match = norm(hit) in norm(predicted_text)
                offset_values = [int(value) for value in re.findall(r"\b\d+\b", predicted_text)]
                offset_match = not positions or any(position in offset_values for position in positions)
                evidence_ok += text_match and offset_match
        severity_ok = audit.get("severity") == ORACLE["severity"]
        anchor_ok = sum(any(norm(hit) in norm(text) for text in all_evidence) for flag in ORACLE["flags"] for hit in flag["hits"])
        anchor_total = sum(len(flag["hits"]) for flag in ORACLE["flags"])
        criteria = [criterion("规则触发", 35, code_f1, f"TP={code_tp}, pred={len(predicted_flags)}, gold={len(gold_flags)}"), exact("证据 offset", 20, evidence_ok, evidence_total), exact("severity", 10, int(severity_ok), 1), exact("实体与条件覆盖", 10, anchor_ok, anchor_total), report_criterion(output)]
        if set(predicted_flags) != set(gold_flags) or evidence_ok != evidence_total or not severity_ok: failures.append("HG_SAFETY_RULE_EVIDENCE")
        metrics.update({"flag_f1": code_f1, "evidence_accuracy": evidence_ok / evidence_total if evidence_total else 1.0, "severity_exact": severity_ok})

    else:
        raise KeyError(f"No scorer for {qid}")

    if abs(sum(item["max_points"] for item in criteria) - 80.0) > 1e-9:
        raise ValueError(f"criteria max does not sum to 80: {sum(item['max_points'] for item in criteria)}")
    return criteria, failures, metrics


def zero_criteria() -> list[dict[str, Any]]:
    return [criterion(name, maximum, 0.0, "not scoreable") for name, maximum in CRITERIA_LAYOUT]


def grade(workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    output = workspace / "output"
    input_ok, input_failures = verify_inputs(workspace)
    if not input_ok:
        return {
            "task_id": TASK_ID,
            "grader_version": GRADER_VERSION,
            "grader_status": "invalid",
            "hardgate_pass": False,
            "deterministic_score": 0.0,
            "max_score": 80.0,
            "criteria": zero_criteria(),
            "failure_codes": sorted(input_failures),
            "metrics": {},
            "oracle_sha256": EMBEDDED_ORACLE_SHA256,
            "scoring_spec": SCORING_SPEC,
        }

    deliverables_ok, failures = required_artifacts(output)
    try:
        criteria, science_failures, metrics = score_task(workspace)
        failures.extend(science_failures)
    except Exception as exc:
        criteria = zero_criteria()
        metrics = {}
        failures.append(f"HG_GRADER_EXCEPTION:{type(exc).__name__}:{exc}")

    if not deliverables_ok:
        failures.append("HG_DELIVERABLE_SET")
    failures = list(dict.fromkeys(failures))
    hardgate_failures = [code for code in failures if code.startswith("HG_")]
    score = sum(float(item["points"]) for item in criteria)
    return {
        "task_id": TASK_ID,
        "grader_version": GRADER_VERSION,
        "grader_status": "scored",
        "hardgate_pass": not hardgate_failures,
        "deterministic_score": score,
        "max_score": 80.0,
        "criteria": criteria,
        "failure_codes": sorted(failures),
        "metrics": metrics,
        "oracle_sha256": EMBEDDED_ORACLE_SHA256,
        "scoring_spec": SCORING_SPEC,
    }


def json_safe(value: Any) -> Any:
    """Replace diagnostic non-finite floats with JSON null."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: json_safe(child) for key, child in value.items()}
    if isinstance(value, list):
        return [json_safe(child) for child in value]
    if isinstance(value, tuple):
        return [json_safe(child) for child in value]
    return value


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True, help="Task workspace containing inputs/ and output/")
    parser.add_argument("--json-out", type=Path, help="Optional path for the JSON result")
    args = parser.parse_args()
    result = json_safe(grade(args.workspace))
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    if result["grader_status"] == "invalid":
        return 2
    return 0 if result["hardgate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
