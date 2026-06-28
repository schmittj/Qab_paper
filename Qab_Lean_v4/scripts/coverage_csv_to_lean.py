#!/usr/bin/env python3
"""Emit Lean coverage terms from a CSV file of closed Nat intervals.

The generated Lean imports ``Qab.Certificates.Coverage`` and defines:

* ``<name>Intervals : List Qab.CoverageInterval``;
* ``<name>AuditId : String`` for metadata only;
* ``<name>Check`` proving the Boolean checker result;
* ``<name>Covers`` proving ``Qab.CoversClosedTarget`` from the pure coverage
  checker soundness theorem.

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
NAT_RE = re.compile(r"[0-9]+")


@dataclass(frozen=True, order=True)
class Interval:
    lo: int
    hi: int


def parse_nat(text: str, *, field: str) -> int:
    value = text.strip()
    if not NAT_RE.fullmatch(value):
        raise ValueError(f"{field}: expected an ASCII natural-number literal, got {text!r}")
    return int(value, 10)


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
        .replace("\r", "\\r")
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
            raw_lo = row.get(lo_column)
            raw_hi = row.get(hi_column)
            if raw_lo is None:
                raise ValueError(f"{path}:{row_number}:{lo_column}: missing value")
            if raw_hi is None:
                raise ValueError(f"{path}:{row_number}:{hi_column}: missing value")
            lo = parse_nat(raw_lo, field=f"{path}:{row_number}:{lo_column}")
            hi = parse_nat(raw_hi, field=f"{path}:{row_number}:{hi_column}")
            if not allow_empty_intervals and lo > hi:
                raise ValueError(
                    f"{path}:{row_number}: empty interval [{lo}, {hi}] "
                    "(pass --allow-empty-intervals to emit it anyway)"
                )
            intervals.append(Interval(lo=lo, hi=hi))
    return intervals


def advance_from(next_point: int, target_hi: int, intervals: list[Interval]) -> int | None:
    """Mirror ``Qab.advanceFrom`` for diagnostics and generated chunk seams."""
    for interval in intervals:
        if target_hi < next_point:
            return next_point
        if interval.hi < next_point:
            continue
        if next_point < interval.lo:
            return None
        next_point = interval.hi + 1
    return next_point


def first_coverage_gap(
    intervals: list[Interval], *, target_lo: int, target_hi: int
) -> int | None:
    """Return the first uncovered point, or ``None`` when the target is covered."""
    next_point = target_lo
    if target_hi < next_point:
        return None
    for interval in intervals:
        if target_hi < next_point:
            return None
        if interval.hi < next_point:
            continue
        if next_point < interval.lo:
            return next_point
        next_point = interval.hi + 1
    return None if target_hi < next_point else next_point


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


def emit_simp_list(handle: TextIO, names: list[str], *, indent: str = "  ") -> None:
    if not names:
        handle.write(f"{indent}simp\n")
        return
    handle.write(f"{indent}simp [\n")
    for item in names:
        handle.write(f"{indent}  {item},\n")
    handle.write(f"{indent}]\n")


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
    audit_name = f"{name}AuditId"
    check_name = f"{name}Check"
    theorem_name = f"{name}Covers"

    handle.write("import Qab.Certificates.Coverage\n\n")
    for part in namespace:
        handle.write(f"namespace {part}\n")
    if namespace:
        handle.write("\n")

    chunked = chunk_size > 0 and len(intervals) > chunk_size
    chunk_parts = list(chunks(intervals, chunk_size)) if chunked else []
    if chunked:
        chunk_names: list[str] = []
        for index, part in chunk_parts:
            chunk_name = f"{intervals_name}_{index}"
            chunk_names.append(chunk_name)
            emit_interval_list(handle, chunk_name, part)
        handle.write(f"def {intervals_name} : List Qab.CoverageInterval :=\n")
        handle.write("  " + " ++ ".join(chunk_names) + "\n\n")
    else:
        emit_interval_list(handle, intervals_name, intervals)

    handle.write("/-- Metadata only; coverage evidence is the theorem below. -/\n")
    handle.write(f"def {audit_name} : String := {lean_string(audit_id)}\n\n")

    if emit_theorem:
        if chunked:
            next_point = target_lo
            advance_names: list[str] = []
            for index, part in chunk_parts:
                chunk_name = f"{intervals_name}_{index}"
                advance_name = f"{chunk_name}Advance"
                next_out = advance_from(next_point, target_hi, part)
                if next_out is None:
                    raise ValueError(
                        f"internal error: chunk {index} does not advance from {next_point}"
                    )
                handle.write(
                    f"theorem {advance_name} : "
                    f"Qab.advanceFrom {next_point} {target_hi} {chunk_name} = some {next_out} := by\n"
                )
                handle.write("  native_decide\n\n")
                advance_names.append(advance_name)
                next_point = next_out

            handle.write(
                f"theorem {check_name} : "
                f"Qab.checkCoverageViaAdvance {intervals_name} {target_lo} {target_hi} = true := by\n"
            )
            simp_items = [
                "Qab.checkCoverageViaAdvance",
                "Qab.checkFromViaAdvance",
                intervals_name,
                "Qab.advanceFrom_append",
                *advance_names,
            ]
            emit_simp_list(handle, simp_items)
            handle.write("\n")
            handle.write(
                f"theorem {theorem_name} : "
                f"Qab.CoversClosedTarget {intervals_name} {target_lo} {target_hi} := by\n"
            )
            handle.write(f"  exact Qab.checkCoverageViaAdvance_sound {check_name}\n\n")
        else:
            handle.write(
                f"theorem {check_name} : "
                f"Qab.checkCoverage {intervals_name} {target_lo} {target_hi} = true := by\n"
            )
            handle.write("  native_decide\n\n")
            handle.write(
                f"theorem {theorem_name} : "
                f"Qab.CoversClosedTarget {intervals_name} {target_lo} {target_hi} := by\n"
            )
            handle.write(f"  exact Qab.checkCoverage_sound {check_name}\n\n")
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
    parser.add_argument("--audit-id", default="", help="metadata string emitted as <name>AuditId")
    parser.add_argument("--chunk-size", type=int, default=1000, help="rows per generated list chunk; 0 disables chunking")
    parser.add_argument("--preserve-order", action="store_true", help="emit rows in CSV order instead of sorting by (lo, hi)")
    parser.add_argument("--allow-empty-intervals", action="store_true", help="allow rows with lo > hi")
    parser.add_argument("--no-theorem", action="store_true", help="emit a #guard instead of a named coverage theorem")
    parser.add_argument("--skip-preflight", action="store_true", help="skip the non-trusted Python coverage diagnostic")
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
        if args.target_hi < args.target_lo:
            print(
                "coverage_csv_to_lean.py: warning: target interval is empty "
                f"[{args.target_lo}, {args.target_hi}]",
                file=sys.stderr,
            )
        if not args.skip_preflight:
            gap = first_coverage_gap(
                intervals, target_lo=args.target_lo, target_hi=args.target_hi
            )
            if gap is not None:
                raise ValueError(
                    f"intervals do not cover closed target "
                    f"[{args.target_lo}, {args.target_hi}]; first uncovered point is {gap}"
                )

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
