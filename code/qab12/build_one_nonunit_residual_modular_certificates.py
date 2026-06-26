#!/usr/bin/env python3
"""Build modular gcd certificates for residual one-nonunit package pairs."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def trim(f: list[int]) -> list[int]:
    while len(f) > 1 and f[-1] == 0:
        f.pop()
    if not f:
        f.append(0)
    return f


def poly_mod(f: list[int], g: list[int], p: int) -> list[int]:
    f = f[:]
    g = trim(g[:])
    if g == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    inv = pow(g[-1], -1, p)
    while len(f) >= len(g) and f != [0]:
        coeff = f[-1] * inv % p
        shift = len(f) - len(g)
        if coeff:
            for i, gi in enumerate(g):
                f[shift + i] = (f[shift + i] - coeff * gi) % p
        trim(f)
    return f


def poly_gcd_degree(f: list[int], g: list[int], p: int) -> int:
    f = trim([x % p for x in f])
    g = trim([x % p for x in g])
    while g != [0]:
        f, g = g, poly_mod(f, g, p)
    return len(f) - 1


def make_poly(scale: int, low: int, total: int, p: int) -> list[int]:
    f = [0] * (scale * total + 1)
    f[scale * total] = low % p
    f[scale * low] = (-total) % p
    f[0] = (total - low) % p
    return trim(f)


def gcd_degree(r: int, low1: int, n: int, s: int, low2: int, m: int, p: int) -> int:
    return poly_gcd_degree(make_poly(r, low1, n, p), make_poly(s, low2, m, p), p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--prime", type=int, default=1009)
    args = ap.parse_args()

    rows = []
    with args.pairs.open(newline="") as f:
        for row in csv.DictReader(f):
            rows.append({k: int(v) for k, v in row.items()})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        fields = [
            "pair_index",
            "orientation",
            "U",
            "r",
            "a",
            "b",
            "n",
            "s",
            "c",
            "f",
            "m",
            "low1",
            "low2",
            "prime",
            "gcd_degree",
        ]
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        count = 0
        for i, row in enumerate(rows):
            p = args.prime
            if any(row[k] % p == 0 for k in ("r", "a", "b", "n", "s", "c", "f", "m")):
                raise RuntimeError(f"bad reduction prime for pair {i}")
            for orientation in range(4):
                low1 = (row["a"], row["b"])[orientation // 2]
                low2 = (row["c"], row["f"])[orientation % 2]
                deg = gcd_degree(row["r"], low1, row["n"], row["s"], low2, row["m"], p)
                wr.writerow({
                    "pair_index": i,
                    "orientation": orientation,
                    "U": row["U"],
                    "r": row["r"],
                    "a": row["a"],
                    "b": row["b"],
                    "n": row["n"],
                    "s": row["s"],
                    "c": row["c"],
                    "f": row["f"],
                    "m": row["m"],
                    "low1": low1,
                    "low2": low2,
                    "prime": p,
                    "gcd_degree": deg,
                })
                count += 1
    print(f"wrote={args.output}")
    print(f"package_pairs={len(rows)}")
    print(f"orientation_certificates={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
