#!/usr/bin/env python3
"""Independent exact verifier for the recorded upper-range CSV outputs.

This verifier does not trust floating-point arithmetic.  It checks every
recorded shape and every pre-final candidate against the integer conditions
used in Qab9.  Completeness of the shape list is supplied by rerunning the C++
enumerator; ``test_small.py`` compares that enumerator with brute force on
small boxes.
"""

from __future__ import annotations

import argparse
import csv
import functools
import math
from pathlib import Path
from typing import Iterable, Mapping, Sequence

D_MAX = 175_394_637
D_UNIT = 6_816_242
SCALE_MAX = 139
SUPPORT_CAP = 4_398_937


@functools.lru_cache(maxsize=None)
def factor_support(n: int) -> tuple[int, ...]:
    if n < 1:
        raise ValueError(n)
    out: list[int] = []
    x = n
    if x % 2 == 0:
        out.append(2)
        while x % 2 == 0:
            x //= 2
    p = 3
    while p * p <= x:
        if x % p == 0:
            out.append(p)
            while x % p == 0:
                x //= p
        p += 2
    if x > 1:
        out.append(x)
    return tuple(out)


def radical(n: int) -> int:
    out = 1
    for p in factor_support(n):
        out *= p
    return out


def degree_upper(D: int) -> int:
    target = 64 * D * D
    lo, hi = 0, 2_000_000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid**3 < target:
            lo = mid
        else:
            hi = mid - 1
    return lo


def role_value(p: int, triple: tuple[int, int, int]) -> int:
    hits = [v for v in triple if v % p == 0]
    if len(hits) != 1:
        raise AssertionError((p, triple, hits))
    return hits[0]


def interval_contains_residue(lo: int, hi: int, residue: int, modulus: int) -> bool:
    if lo > hi:
        return False
    return lo + ((residue - lo) % modulus) <= hi


def allowed_residues(p: int, coefficient: int) -> tuple[int, ...] | None:
    if coefficient % p == 0:
        return None
    z = (-2 * pow(coefficient, -1, p)) % p
    return (0,) if z == 0 else (0, z)


def congruence_exists(
    lo: int,
    hi: int,
    r: int,
    s: int,
    support1: Iterable[int],
    support2: Iterable[int],
) -> bool:
    s1, s2 = set(support1), set(support2)
    residues = [0]
    modulus = 1
    for p in sorted(s1 | s2):
        a = allowed_residues(p, s) if p in s1 else None
        b = allowed_residues(p, r) if p in s2 else None
        if a is None:
            allowed = b
        elif b is None:
            allowed = a
        else:
            allowed = tuple(x for x in a if x in set(b))
        if allowed is None:
            continue
        if not allowed:
            return False
        inv = pow(modulus, -1, p)
        new: list[int] = []
        for x in residues:
            for y in allowed:
                t = ((y - x) % p) * inv % p
                new.append(x + modulus * t)
        residues = new
        modulus *= p
    return any(interval_contains_residue(lo, hi, a, modulus) for a in residues)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def verify_shapes(path: Path) -> tuple[dict[tuple[int, int, int], tuple[int, int, int, int]], int]:
    rows = read_csv(path)
    seen: dict[tuple[int, int, int], tuple[int, int, int, int]] = {}
    previous: tuple[int, int, int] | None = None
    for row in rows:
        a, b, n = (int(row[k]) for k in ("a", "b", "n"))
        ra, rb, rn, rp = (int(row[k]) for k in ("rad_a", "rad_b", "rad_n", "rad_product"))
        key = (a, b, n)
        assert 1 <= a < b and n == a + b and n <= D_MAX and math.gcd(a, b) == 1
        assert (ra, rb, rn) == (radical(a), radical(b), radical(n))
        assert rp == ra * rb * rn <= SUPPORT_CAP
        assert key not in seen
        if previous is not None:
            assert (n, a, b) > (previous[2], previous[0], previous[1])
        previous = key
        seen[key] = (ra, rb, rn, rp)
    return seen, len(rows)


def verify_pairs(path: Path, shapes: Mapping[tuple[int, int, int], tuple[int, int, int, int]]) -> int:
    rows = read_csv(path)
    seen_pairs: set[tuple[int, ...]] = set()
    for row in rows:
        r, a, b, n, s, c, de, m = (
            int(row[k]) for k in ("r", "a", "b", "n", "s", "c", "d", "m")
        )
        D, klo, khi = (int(row[k]) for k in ("D", "k_lo", "k_hi"))
        sh1, sh2 = (a, b, n), (c, de, m)
        assert sh1 in shapes and sh2 in shapes
        assert 1 <= r <= s <= SCALE_MAX and math.gcd(r, s) == 1
        assert D == max(r * n, s * m) and D_UNIT <= D <= D_MAX
        scaled1 = {r * a, r * b, r * n}
        scaled2 = {s * c, s * de, s * m}
        assert scaled1.isdisjoint(scaled2)
        rp1, rp2 = shapes[sh1][3], shapes[sh2][3]
        assert rp1 * r <= SUPPORT_CAP and rp2 * s <= SUPPORT_CAP
        support5_1 = rp1 // (2 if rp1 % 2 == 0 else 1) // (3 if rp1 % 3 == 0 else 1)
        support5_2 = rp2 // (2 if rp2 % 2 == 0 else 1) // (3 if rp2 % 3 == 0 else 1)
        assert int(row["radprod1"]) == rp1 and int(row["radprod2"]) == rp2
        assert int(row["support1"]) == support5_1 and int(row["support2"]) == support5_2
        pair_key = (r, a, b, n, s, c, de, m, D, klo, khi)
        assert pair_key not in seen_pairs
        seen_pairs.add(pair_key)

        supp1, supp2 = set(factor_support(rp1)), set(factor_support(rp2))
        for p in (supp1 - supp2) - {2, 3}:
            assert s % p == 0
        for p in (supp2 - supp1) - {2, 3}:
            assert r % p == 0

        rs = r * s
        expected_lo = (D // 140 + 1 + rs - 1) // rs
        upper = min(degree_upper(D), min(n, m) - 2) // rs
        upper = min(upper, (n - 4) // s if n >= 4 else -1)
        upper = min(upper, (m - 4) // r if m >= 4 else -1)

        role_bound = min(n, m) - 2
        for p in sorted(supp1 | supp2):
            e1 = r * role_value(p, sh1) if p in supp1 else None
            e2 = s * role_value(p, sh2) if p in supp2 else None
            g = math.gcd(e1, e2) if e1 is not None and e2 is not None else (e1 or e2)
            assert g is not None
            role_bound = min(role_bound, g)
        upper = min(upper, role_bound // rs)

        assert klo == expected_lo and khi == upper and klo <= khi
        assert congruence_exists(klo, khi, r, s, supp1, supp2)

        # Final theorem check.
        assert sh1 == sh2
        assert D // 140 + 1 > 2 * r * s
    return len(rows)


def verify_residual(path: Path) -> int:
    rows = read_csv(path)
    assert not rows
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    args = ap.parse_args(argv)
    shapes, n_shapes = verify_shapes(args.data_dir / "upper_shapes.csv")
    n_pairs = verify_pairs(args.data_dir / "upper_pair_survivors.csv", shapes)
    verify_residual(args.data_dir / "upper_residual_candidates.csv")
    print(f"verified_shapes={n_shapes}")
    print(f"verified_prefinal_pairs={n_pairs}")
    print("verified_residual_candidates=0")
    print("status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
