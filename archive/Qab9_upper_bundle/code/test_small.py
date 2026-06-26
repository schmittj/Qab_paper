#!/usr/bin/env python3
"""Small independent regression tests for the search code."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import math
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Sequence

import sympy as sp
from sympy.utilities.exceptions import SymPyDeprecationWarning
import warnings

warnings.filterwarnings("ignore", category=SymPyDeprecationWarning)


def radical(n: int) -> int:
    out = 1
    x = n
    p = 2
    while p * p <= x:
        if x % p == 0:
            out *= p
            while x % p == 0:
                x //= p
        p = 3 if p == 2 else p + 2
    if x > 1:
        out *= x
    return out


def load_postfilter(path: Path):
    spec = importlib.util.spec_from_file_location("postfilter_upper", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_enumerator(exe: Path) -> None:
    limit, cap = 400, 250
    expected = set()
    for n in range(3, limit + 1):
        for a in range(1, (n - 1) // 2 + 1):
            b = n - a
            if a == b or math.gcd(a, b) != 1:
                continue
            if radical(a) * radical(b) * radical(n) <= cap:
                expected.add((a, b, n))
    with tempfile.TemporaryDirectory() as td:
        output = Path(td) / "shapes.csv"
        subprocess.run(
            [
                str(exe),
                "--limit",
                str(limit),
                "--rad-cap",
                str(cap),
                "--threads",
                "2",
                "--output",
                str(output),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        with output.open(newline="") as f:
            actual = {(int(r["a"]), int(r["b"]), int(r["n"])) for r in csv.DictReader(f)}
    assert actual == expected, (len(actual), len(expected), sorted(actual ^ expected)[:10])


def test_factor_degree_reachability(postfilter_path: Path) -> None:
    mod = load_postfilter(postfilter_path)
    x = sp.symbols("x")
    for p in (2, 3, 5, 7):
        for g in range(1, 36):
            coeff, factors = sp.factor_list(x**g - 1, modulus=p)
            degrees: list[int] = []
            for factor, multiplicity in factors:
                degrees.extend([sp.Poly(factor, x, modulus=p).degree()] * multiplicity)
            reachable = {0}
            for degree in degrees:
                reachable |= {z + degree for z in list(reachable)}
            for d in range(g + 1):
                assert mod.degree_reachable(p, g, d) == (d in reachable), (p, g, d)


def test_exact_degree_upper() -> None:
    for D in (1, 2, 10, 6_816_242, 175_394_637):
        target = 64 * D * D
        lo, hi = 0, 2_000_000
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if mid**3 < target:
                lo = mid
            else:
                hi = mid - 1
        assert lo**3 < target <= (lo + 1) ** 3


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--enumerator", type=Path, required=True)
    args = ap.parse_args(argv)
    code_dir = Path(__file__).resolve().parent
    test_enumerator(args.enumerator.resolve())
    test_factor_degree_reachability(code_dir / "postfilter_upper.py")
    test_exact_degree_upper()
    subprocess.run(["python3", str(code_dir / "certify_constants.py")], check=True, capture_output=True)
    print("small_enumerator_vs_bruteforce=PASS")
    print("factor_degree_reachability_vs_sympy=PASS")
    print("exact_degree_upper=PASS")
    print("constant_certificates=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
