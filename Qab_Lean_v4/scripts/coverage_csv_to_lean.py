#!/usr/bin/env python3
"""Emit Lean coverage terms from a CSV file of closed Nat intervals.

The generated Lean imports ``Qab.Certificates.Coverage`` and defines:

* ``<name>Intervals : List Qab.CoverageInterval``;
* ``<name>Cert : Qab.CoverageCert`` for metadata only;
* ``<name>Covers`` proving ``Qab.CoversClosedTarget`` by running the pure
  coverage checker.

By default rows are sorted by ``(lo, hi)`` before emission.  Use
``--preserve-order`` when auditing the exact CSV order; the Lean checker is
still the proof-relevant object and will reject gaps.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TextIO


IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_']*")


@dataclass(frozen=True, order=True)
class Interval:
    lo: int
    hi: int


def parse_nat(text: str, *, field: str) -> int:
    value = text.strip()
    if not value:
        raise ValueError(f"{field}: expected a natural number, got an empty string")
    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise ValueError(f"{field}: expected a natural number, got {text!r}") from exc
    if parsed < 0:
        raise ValueError(f"{field}: expected a natural number, got {parsed}")
    return parsed


def require_identifier(name: str, *, what: str) -> str:
    if not IDENT_RE.fullmatch(name):
        raise ValueError(f"{what}: expected a Lean identifier segment, got {name!r}")
    return name


def parse_namespace(namespace: str) -> list[str]:
    if not namespace:
        return []
    parts = namespace.split(".")
    for part in parts:
        require_identifier(part, what="namespace")
    return parts


def lean_string(text: str) -> str:
    escaped = (
        text.replace("\\", "\\\\")
        .replace("\"", "\\\"")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )
    return f"\"{escaped}\""


def read_intervals(
    path: Path,
    *,
    lo_column: str,
    hi_column: str,
    allow_empty_intervals: bool,
) -> list[Interval]:
    intervals: list[Interval] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: CSV file has no header row")
        missing = [name for name in (lo_column, hi_column) if name not in reader.fieldnames]
        if missing:
            fields = ", ".join(reader.fieldnames)
            raise ValueError(f"{path}: missing columns {missing}; available columns: {fields}")
        for row_number, row in enumerate(reader, start=2):
            lo = parse_nat(row[lo_column], field=f"{path}:{row_number}:{lo_column}")
            hi = parse_nat(row[hi_column], field=f"{path}:{row_number}:{hi_column}")
            if not allow_empty_intervals and lo > hi:
                raise ValueError(
                    f"{path}:{row_number}: empty interval [{lo}, {hi}] "
                    "(pass --allow-empty-intervals to emit it anyway)"
                )
            intervals.append(Interval(lo=lo, hi=hi))
    return intervals


def chunks(items: list[Interval], size: int) -> Iterable[tuple[int, list[Interval]]]:
    if size <= 0:
        yield 0, items
        return
    for index, start in enumerate(range(0, len(items), size)):
        yield index, items[start : start + size]


def emit_interval_list(handle: TextIO, name: str, intervals: list[Interval]) -> None:
    handle.write(f"def {name} : List Qab.CoverageInterval :=\n")
    if not intervals:
        handle.write("  []\n\n")
        return
    handle.write("  [\n")
    for interval in intervals:
        handle.write(f"    {{ lo := {interval.lo}, hi := {interval.hi} }},\n")
    handle.write("  ]\n\n")


def emit_lean(
    handle: TextIO,
    *,
    intervals: list[Interval],
    name: str,
    namespace: list[str],
    target_lo: int,
    target_hi: int,
    audit_id: str,
    chunk_size: int,
    emit_theorem: bool,
) -> None:
    intervals_name = f"{name}Intervals"
    cert_name = f"{name}Cert"
    theorem_name = f"{name}Covers"

    handle.write("import Qab.Certificates.Coverage\n\n")
    for part in namespace:
        handle.write(f"namespace {part}\n")
    if namespace:
        handle.write("\n")

    chunked = chunk_size > 0 and len(intervals) > chunk_size
    if chunked:
        chunk_names: list[str] = []
        for index, part in chunks(intervals, chunk_size):
            chunk_name = f"{intervals_name}_{index}"
            chunk_names.append(chunk_name)
            emit_interval_list(handle, chunk_name, part)
        handle.write(f"def {intervals_name} : List Qab.CoverageInterval :=\n")
        handle.write("  " + " ++ ".join(chunk_names) + "\n\n")
    else:
        emit_interval_list(handle, intervals_name, intervals)

    handle.write(f"def {cert_name} : Qab.CoverageCert where\n")
    handle.write(f"  name := {lean_string(name)}\n")
    handle.write(f"  intervals := {intervals_name}\n")
    handle.write(f"  auditId := {lean_string(audit_id)}\n\n")

    if emit_theorem:
        handle.write(
            f"theorem {theorem_name} : "
            f"Qab.CoversClosedTarget {intervals_name} {target_lo} {target_hi} := by\n"
        )
        handle.write("  exact Qab.checkCoverage_sound (by native_decide)\n\n")
    else:
        handle.write(f"#guard Qab.checkCoverage {intervals_name} {target_lo} {target_hi}\n\n")

    for part in reversed(namespace):
        handle.write(f"end {part}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="CSV file containing interval rows")
    parser.add_argument("--name", required=True, help="Lean identifier stem for generated terms")
    parser.add_argument("--target-lo", required=True, type=lambda s: parse_nat(s, field="target-lo"))
    parser.add_argument("--target-hi", required=True, type=lambda s: parse_nat(s, field="target-hi"))
    parser.add_argument("--lo-column", default="lo", help="CSV column holding closed lower endpoints")
    parser.add_argument("--hi-column", default="hi", help="CSV column holding closed upper endpoints")
    parser.add_argument("--namespace", default="Qab.GeneratedCoverage")
    parser.add_argument("--audit-id", default="", help="Metadata string for the generated CoverageCert")
    parser.add_argument("--chunk-size", type=int, default=1000, help="rows per generated list chunk; 0 disables chunking")
    parser.add_argument("--preserve-order", action="store_true", help="emit rows in CSV order instead of sorting by (lo, hi)")
    parser.add_argument("--allow-empty-intervals", action="store_true", help="allow rows with lo > hi")
    parser.add_argument("--no-theorem", action="store_true", help="emit a #guard instead of a named coverage theorem")
    parser.add_argument("--output", type=Path, help="write Lean output to this path instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        name = require_identifier(args.name, what="name")
        namespace = parse_namespace(args.namespace)
        if args.chunk_size < 0:
            raise ValueError("chunk-size: expected a nonnegative integer")
        intervals = read_intervals(
            args.csv_path,
            lo_column=args.lo_column,
            hi_column=args.hi_column,
            allow_empty_intervals=args.allow_empty_intervals,
        )
        if not args.preserve_order:
            intervals = sorted(intervals)

        if args.output is None:
            emit_lean(
                sys.stdout,
                intervals=intervals,
                name=name,
                namespace=namespace,
                target_lo=args.target_lo,
                target_hi=args.target_hi,
                audit_id=args.audit_id,
                chunk_size=args.chunk_size,
                emit_theorem=not args.no_theorem,
            )
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8", newline="\n") as handle:
                emit_lean(
                    handle,
                    intervals=intervals,
                    name=name,
                    namespace=namespace,
                    target_lo=args.target_lo,
                    target_hi=args.target_hi,
                    audit_id=args.audit_id,
                    chunk_size=args.chunk_size,
                    emit_theorem=not args.no_theorem,
                )
    except (OSError, ValueError) as exc:
        parser.exit(2, f"coverage_csv_to_lean.py: error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
