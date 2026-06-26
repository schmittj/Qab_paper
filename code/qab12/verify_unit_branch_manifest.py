#!/usr/bin/env python3
"""Manifest verifier for the stored unit-branch proof artifacts.

This checker is intentionally lightweight and non-FLINT-dependent.  It verifies
the public certificate contract for the unit branch: file hashes, row counts,
stage counters, terminal modular-certificate coverage, and recorded PASS logs.
The expensive modular gcd and factor-degree arithmetic is replayed by the
separate FLINT-dependent verifiers.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("data/qab12")

UNIT_FILES = {
    "large_pair_log": ROOT / "unit_large_pair_output.txt",
    "large_prefinal": ROOT / "unit_large_prefinal.csv",
    "large_terminal_pairs": ROOT / "unit_large_residual.csv",
    "large_modular_input": ROOT / "unit_large_modular_input.csv",
    "large_modular_certificates": ROOT / "unit_large_modular_certificates.csv",
    "large_modular_verification_log": ROOT / "unit_large_modular_verification_output.txt",
    "small_generator_log": ROOT / "unit_small_generator_output.txt",
    "small_packages": ROOT / "unit_small_packages.csv",
    "small_pair_log": ROOT / "unit_small_pair_output.txt",
    "small_state_pairs": ROOT / "unit_small_state_pairs.csv",
    "small_orientation_pairs": ROOT / "unit_small_orientation_pairs.csv",
    "small_modular_input": ROOT / "unit_small_modular_input.csv",
    "small_modular_certificates": ROOT / "unit_small_modular_certificates.csv",
    "small_modular_verification_log": ROOT / "unit_small_modular_verification_output.txt",
    "defect_counterpart_log": ROOT / "unit_defect_counterpart_output.txt",
    "defect_packages": ROOT / "unit_defect_all_packages.csv",
    "defect_pair_log": ROOT / "unit_defect_pair_output.txt",
    "defect_state_pairs": ROOT / "unit_defect_state_pairs.csv",
    "defect_orientation_pairs": ROOT / "unit_defect_orientation_pairs.csv",
    "defect_irreducibility_certificates": ROOT / "unit_defect_irreducibility_certificates.jsonl",
    "defect_irreducibility_verification_log": ROOT / "unit_defect_irreducibility_direct_verification_output.txt",
}

SCRIPT_FILES = {
    "pair_unit_large": Path("code/qab12/pair_unit_large.cpp"),
    "enumerate_unit_small": Path("code/qab12/enumerate_unit_small_packages.cpp"),
    "pair_unit_small": Path("code/qab12/pair_unit_small.cpp"),
    "enumerate_unit_defect_counterparts": Path("code/qab12/enumerate_unit_defect_counterparts.cpp"),
    "pair_unit_defect": Path("code/qab12/pair_unit_defect.cpp"),
    "verify_modular_gcd_certificates": Path("code/qab12/verify_modular_gcd_certificates.py"),
    "verify_irreducibility_certificates_direct": Path("code/qab12/verify_irreducibility_certificates_direct.py"),
}


def fail(msg: str) -> None:
    raise RuntimeError(msg)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse_key_values(path: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    for key, value in re.findall(r"(\w+)=(\d+)", path.read_text()):
        out[key] = int(value)
    return out


def csv_rows(path: Path) -> dict[str, Any]:
    with path.open(newline="") as f:
        rd = csv.reader(f)
        header = next(rd, None)
        rows = sum(1 for _ in rd)
    return {"rows": rows, "header": header}


def jsonl_rows(path: Path) -> int:
    count = 0
    with path.open() as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("schema") != "qab12-subset-degree-v1":
                fail(f"{path}:{line_no}: bad schema")
            degree = rec.get("degree")
            if rec.get("final_degrees") != [0, degree]:
                fail(f"{path}:{line_no}: irreducibility certificate does not end at [0, degree]")
            if not rec.get("steps"):
                fail(f"{path}:{line_no}: empty irreducibility certificate")
            count += 1
    return count


def require_status_pass(path: Path) -> dict[str, int]:
    text = path.read_text()
    if "status=PASS" not in text:
        fail(f"{path}: missing status=PASS")
    return parse_key_values(path)


def read_modular_pairs(path: Path) -> list[tuple[int, ...]]:
    with path.open(newline="") as f:
        rd = csv.DictReader(f)
        expected = ["r", "a", "b", "n", "s", "c", "d_endpoint", "m"]
        if rd.fieldnames != expected:
            fail(f"{path}: bad modular input header {rd.fieldnames}")
        return [tuple(int(row[k]) for k in expected) for row in rd]


def check_modular_certificates(input_path: Path, cert_path: Path) -> dict[str, int]:
    pairs = read_modular_pairs(input_path)
    expected_fields = [
        "pair_index", "orientation", "r", "a", "b", "n", "s", "c",
        "d_endpoint", "m", "low1", "low2", "prime", "gcd_degree",
        "attempt_count", "total_seconds", "max_rss_kb", "backend",
    ]
    seen: set[tuple[int, int]] = set()
    with cert_path.open(newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != expected_fields:
            fail(f"{cert_path}: bad certificate header {rd.fieldnames}")
        for line_no, row in enumerate(rd, 2):
            i = int(row["pair_index"])
            orientation = int(row["orientation"])
            if not (0 <= i < len(pairs) and 0 <= orientation < 4):
                fail(f"{cert_path}:{line_no}: bad pair/orientation index")
            if (i, orientation) in seen:
                fail(f"{cert_path}:{line_no}: duplicate certificate")
            seen.add((i, orientation))
            pair = pairs[i]
            keys = ["r", "a", "b", "n", "s", "c", "d_endpoint", "m"]
            if tuple(int(row[k]) for k in keys) != pair:
                fail(f"{cert_path}:{line_no}: pair mismatch")
            r, a, b, n, s, c, d_endpoint, m = pair
            if a + b != n or c + d_endpoint != m:
                fail(f"{cert_path}:{line_no}: additive triple mismatch")
            low1 = (a, b)[orientation // 2]
            low2 = (c, d_endpoint)[orientation % 2]
            if (int(row["low1"]), int(row["low2"])) != (low1, low2):
                fail(f"{cert_path}:{line_no}: orientation mismatch")
            if int(row["gcd_degree"]) != 2:
                fail(f"{cert_path}:{line_no}: certificate gcd degree is not 2")
    expected = {(i, o) for i in range(len(pairs)) for o in range(4)}
    if seen != expected:
        fail(f"{cert_path}: certificate coverage mismatch")
    return {"package_pairs": len(pairs), "orientation_certificates": len(seen)}


def build_manifest() -> dict[str, Any]:
    for path in list(UNIT_FILES.values()) + list(SCRIPT_FILES.values()):
        if not path.exists():
            fail(f"missing required file: {path}")

    large_counts = parse_key_values(UNIT_FILES["large_pair_log"])
    small_generator_counts = parse_key_values(UNIT_FILES["small_generator_log"])
    small_pair_counts = parse_key_values(UNIT_FILES["small_pair_log"])
    defect_generator_counts = parse_key_values(UNIT_FILES["defect_counterpart_log"])
    defect_pair_counts = parse_key_values(UNIT_FILES["defect_pair_log"])
    large_modular_log = require_status_pass(UNIT_FILES["large_modular_verification_log"])
    small_modular_log = require_status_pass(UNIT_FILES["small_modular_verification_log"])
    defect_irred_log = require_status_pass(UNIT_FILES["defect_irreducibility_verification_log"])

    row_counts = {name: csv_rows(path) for name, path in UNIT_FILES.items() if path.suffix == ".csv"}
    row_counts["defect_irreducibility_certificates"] = {
        "rows": jsonl_rows(UNIT_FILES["defect_irreducibility_certificates"]),
        "header": None,
    }

    large_cert = check_modular_certificates(
        UNIT_FILES["large_modular_input"], UNIT_FILES["large_modular_certificates"]
    )
    small_cert = check_modular_certificates(
        UNIT_FILES["small_modular_input"], UNIT_FILES["small_modular_certificates"]
    )

    checks = [
        (row_counts["large_prefinal"]["rows"], large_counts.get("after_full_radical_CRT"), "large prefinal"),
        (row_counts["large_terminal_pairs"]["rows"], row_counts["large_modular_input"]["rows"], "large terminal/input"),
        (large_cert["package_pairs"], large_modular_log.get("verified_package_pairs"), "large modular pair count"),
        (large_cert["orientation_certificates"], large_modular_log.get("verified_orientation_certificates"), "large modular cert count"),
        (row_counts["small_packages"]["rows"], small_generator_counts.get("unique_records"), "small packages"),
        (row_counts["small_state_pairs"]["rows"], small_pair_counts.get("unique_state_pairs"), "small state pairs"),
        (row_counts["small_orientation_pairs"]["rows"], small_pair_counts.get("unique_orientation_pairs"), "small orientation pairs"),
        (row_counts["small_orientation_pairs"]["rows"], row_counts["small_modular_input"]["rows"], "small terminal/input"),
        (small_cert["package_pairs"], small_modular_log.get("verified_package_pairs"), "small modular pair count"),
        (small_cert["orientation_certificates"], small_modular_log.get("verified_orientation_certificates"), "small modular cert count"),
        (row_counts["defect_packages"]["rows"], defect_generator_counts.get("unique_records"), "defect packages"),
        (row_counts["defect_state_pairs"]["rows"], defect_pair_counts.get("unique_state_pairs"), "defect state pairs"),
        (row_counts["defect_orientation_pairs"]["rows"], defect_pair_counts.get("unique_orientation_pairs"), "defect orientation pairs"),
        (row_counts["defect_irreducibility_certificates"]["rows"], defect_irred_log.get("verified_shapes"), "defect irreducibility shapes"),
    ]
    for left, right, label in checks:
        if left != right:
            fail(f"{label} mismatch: {left} != {right}")

    return {
        "schema": "qab-unit-branch-manifest-v1",
        "status": "PASS",
        "contract": {
            "scope": "stored unit-branch artifacts and terminal certificates",
            "non_flint_checks": [
                "file hashes",
                "CSV headers and row counts",
                "generator and pair-sieve stage counters",
                "terminal modular-certificate coverage",
                "recorded PASS logs for FLINT-dependent arithmetic replays",
            ],
            "separate_flint_replays": [
                "make verify-modular",
                "make verify-irreducibility-direct",
            ],
        },
        "branches": {
            "large_full_kummer": {
                "range": {"D_min": 50000, "D_max": 6816241},
                "pair_counts": large_counts,
                "prefinal_rows": row_counts["large_prefinal"]["rows"],
                "terminal_package_pairs": row_counts["large_terminal_pairs"]["rows"],
                "modular_certificates": large_cert,
            },
            "small_full_kummer": {
                "range": {"D_max": 49999},
                "generator_counts": small_generator_counts,
                "pair_counts": small_pair_counts,
                "package_rows": row_counts["small_packages"]["rows"],
                "terminal_state_pairs": row_counts["small_state_pairs"]["rows"],
                "terminal_package_pairs": row_counts["small_orientation_pairs"]["rows"],
                "modular_certificates": small_cert,
            },
            "deficient_scale_prime": {
                "generator_counts": defect_generator_counts,
                "pair_counts": defect_pair_counts,
                "package_rows": row_counts["defect_packages"]["rows"],
                "terminal_state_pairs": row_counts["defect_state_pairs"]["rows"],
                "terminal_orientation_pairs": row_counts["defect_orientation_pairs"]["rows"],
                "irreducibility_certificates": {
                    "shapes": row_counts["defect_irreducibility_certificates"]["rows"],
                    "verified_modular_factorizations": defect_irred_log.get("verified_modular_factorizations"),
                },
            },
        },
        "files": {
            name: {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for name, path in UNIT_FILES.items()
        },
        "scripts": {
            name: {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for name, path in SCRIPT_FILES.items()
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=ROOT / "unit_branch_manifest.json")
    ap.add_argument("--write-manifest", type=Path, help="Regenerate the manifest intentionally.")
    args = ap.parse_args()

    expected = build_manifest()
    if args.write_manifest:
        args.write_manifest.parent.mkdir(parents=True, exist_ok=True)
        args.write_manifest.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n")
        manifest_path = args.write_manifest
    else:
        manifest_path = args.manifest
        try:
            got = json.loads(manifest_path.read_text())
        except FileNotFoundError:
            fail(f"missing manifest: {manifest_path}")
        if got != expected:
            fail(f"manifest mismatch for {manifest_path}")

    print(f"unit_manifest={manifest_path}")
    print(f"large_terminal_package_pairs={expected['branches']['large_full_kummer']['terminal_package_pairs']}")
    print(f"small_terminal_package_pairs={expected['branches']['small_full_kummer']['terminal_package_pairs']}")
    print(f"defect_irreducibility_shapes={expected['branches']['deficient_scale_prime']['irreducibility_certificates']['shapes']}")
    print("status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
