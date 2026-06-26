#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import subprocess
import tempfile
from pathlib import Path

from verify_one_nonunit_residual import (
    ORIENTATION_FIELDS,
    PACKAGE_FIELDS,
    STATE_FIELDS,
    pair_sieve,
    read_tuple_csv,
)

ROOT = Path(__file__).resolve().parents[2]
ENUM = ROOT / "build/qab12_enumerate_one_nonunit_residual_packages"
PAIR = ROOT / "build/qab12_pair_one_nonunit_residual"


def fac(n: int) -> list[tuple[int, int]]:
    out = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            k = 0
            while n % p == 0:
                n //= p
                k += 1
            out.append((p, k))
        p = 3 if p == 2 else p + 2
    if n > 1:
        out.append((n, 1))
    return out


def val(n: int, p: int) -> int:
    k = 0
    while n % p == 0:
        n //= p
        k += 1
    return k


def supp(n: int) -> set[int]:
    return {p for p, _ in fac(n)}


def divisors_from_factorization(f: list[tuple[int, int]]) -> list[int]:
    out = [1]
    for p, k in f:
        old = out[:]
        q = 1
        for _ in range(k):
            q *= p
            out.extend(x * q for x in old)
    return sorted(out)


def defects(r: int, t: int) -> set[int]:
    return {p for p, a in fac(r) if val(t, p) < a}


def check_choice(U: int, r: int, t: int, e: int, a: int, b: int) -> tuple[int, ...] | None:
    D = defects(r, t)
    sigmas = []
    for p, kappa in fac(a):
        A = val(U, p)
        if A == 0:
            if p in D or e % p not in (0, (p - 2) % p):
                return None
            continue
        if (r * A) % t:
            return None
        lam = r * A // t
        if not (1 <= lam <= kappa) or (b * lam) % kappa:
            return None
        w = b * lam // kappa
        if not (1 <= w <= min(b, e)):
            return None
        if (e - w) % p not in (0, (p - 2) % p):
            return None
        if p in D and (p > 7 or kappa < p or (e * kappa) % (p * b)):
            return None
        sigmas.append(t * w)
    if len(sigmas) > 5:
        return None
    return tuple(sigmas + [0] * (5 - len(sigmas)))


def brute_packages(e_start: int, e_end: int, Dcap: int, dmax: int, rmax: int) -> set[tuple[int, ...]]:
    out = set()
    for e in range(e_start, e_end + 1):
        unit_support = supp(e) | supp(e + 2)
        for r in range(1, rmax + 1):
            for t in range(1, r + 1):
                d = t * e
                if d > dmax:
                    break
                D = defects(r, t)
                for n in range(e + 4, Dcap // r + 1):
                    if not supp(n) <= unit_support:
                        continue
                    for b in range(1, n):
                        a = n - b
                        if a < 2 or math.gcd(a, b) != 1 or not supp(b) <= unit_support:
                            continue
                        if any((b % q == 0 or n % q == 0 or (a % q != 0 and e > q - 2)) for q in D):
                            continue
                        for U in divisors_from_factorization(fac(a)):
                            if U <= 1:
                                continue
                            sigmas = check_choice(U, r, t, e, a, b)
                            if sigmas is None:
                                continue
                            out.add((U, d, *sigmas, r, t, e, a, b, n))
    return out


def read_packages(path: Path) -> list[dict[str, int]]:
    with path.open(newline="") as f:
        return [{k: int(v) for k, v in row.items()} for row in csv.DictReader(f)]


def main() -> int:
    cases = [
        (2, 9, 55, 40, 5),
        (3, 12, 75, 55, 6),
    ]
    for e_start, e_end, Dcap, dmax, rmax in cases:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            packages = tmp / "packages.csv"
            states = tmp / "states.csv"
            orients = tmp / "orients.csv"
            subprocess.run([
                str(ENUM),
                "--e-start", str(e_start),
                "--e-end", str(e_end),
                "--D-cap", str(Dcap),
                "--d-max", str(dmax),
                "--r-max", str(rmax),
                "--threads", "2",
                "--output", str(packages),
            ], check=True, capture_output=True, text=True)
            got = {tuple(int(row[k]) for k in PACKAGE_FIELDS) for row in read_packages(packages)}
            expected = brute_packages(e_start, e_end, Dcap, dmax, rmax)
            if got != expected:
                raise RuntimeError(
                    f"package mismatch D={Dcap}: got={len(got)} expected={len(expected)} "
                    f"missing={list(expected - got)[:3]} extra={list(got - expected)[:3]}"
                )
            subprocess.run([
                str(PAIR),
                "--input", str(packages),
                "--output", str(states),
                "--pairs-output", str(orients),
                "--D-cap", str(Dcap),
            ], check=True, capture_output=True, text=True)
            rows = read_packages(packages)
            _, expected_states, expected_orients = pair_sieve(rows, Dcap)
            got_states = read_tuple_csv(states, STATE_FIELDS)
            got_orients = read_tuple_csv(orients, ORIENTATION_FIELDS)
            if got_states != expected_states:
                raise RuntimeError(f"state mismatch D={Dcap}: got={len(got_states)} expected={len(expected_states)}")
            if got_orients != expected_orients:
                raise RuntimeError(f"orientation mismatch D={Dcap}: got={len(got_orients)} expected={len(expected_orients)}")
            print(f"residual_small_oracle D={Dcap} package_states={len(got)} pair_states={len(got_states)} PASS")
    print("one_nonunit_residual_small_oracle=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
