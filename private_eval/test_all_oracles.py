#!/usr/bin/env python3
"""Compile and smoke/regression-test all standalone oracle.py files."""
import argparse, json, py_compile, shutil, subprocess, sys, tempfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--submission-root", type=Path, help="Optional root containing MSxx-Qx/output directories")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
failures = []
paths = sorted(root.glob("tasks/MS*/MS*-Q*/private_eval/oracle.py"))
with tempfile.TemporaryDirectory(prefix="v24-oracle-test-") as temp_name:
    temp = Path(temp_name)
    for path in paths:
        qroot = path.parents[1]
        try:
            py_compile.compile(str(path), doraise=True)
            workspace = qroot
            if args.submission_root:
                workspace = temp / qroot.name
                shutil.copytree(qroot / "inputs", workspace / "inputs")
                shutil.copytree(args.submission_root / qroot.name / "output", workspace / "output")
            proc = subprocess.run([sys.executable, str(path), "--workspace", str(workspace)], text=True, encoding="utf-8", capture_output=True)
            payload = json.loads(proc.stdout)
            if payload.get("task_id") != qroot.name or proc.returncode not in (0, 1, 2):
                raise ValueError("invalid oracle contract")
            if abs(sum(float(item["max_points"]) for item in payload["criteria"]) - 80) > 1e-9:
                raise ValueError("criterion maxima do not sum to 80")
            if any(str(code).startswith("HG_GRADER_EXCEPTION") for code in payload.get("failure_codes", [])):
                raise ValueError("grader exception: " + str(payload["failure_codes"]))
        except Exception as exc:
            failures.append(f"{path}: {type(exc).__name__}: {exc}")
print(json.dumps({"oracle_count": len(paths), "submission_root": str(args.submission_root) if args.submission_root else None, "failures": failures}, ensure_ascii=False, indent=2))
raise SystemExit(1 if failures else 0)
