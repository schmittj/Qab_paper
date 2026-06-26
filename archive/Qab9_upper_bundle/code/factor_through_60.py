#!/usr/bin/env python3
"""Exact parallel SymPy check through total 60.

For every unordered unequal package ``{a,b}`` with ``a+b<=MAXN`` this script
factors one orientation over QQ, canonicalizes reciprocal factor orbits, and
checks that no orbit is shared by two packages.  Primitive-base
irreducibility is read from the same result table, avoiding duplicate work.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from math import gcd
from typing import Iterable, Sequence

import sympy as sp
from sympy import Poly, QQ


@dataclass(frozen=True)
class Result:
    a: int
    b: int
    irreducible: bool
    orbit_keys: tuple[tuple[sp.Rational, ...], ...]


def qpoly(a: int, b: int, x: sp.Symbol) -> Poly:
    g = gcd(a, b)
    num = Poly(a * x ** (a + b) - (a + b) * x**a + b, x, domain=QQ)
    den = Poly((x**g - 1) ** 2, x, domain=QQ)
    return num.exquo(den)


def reciprocal_orbit_key(f: sp.Expr, x: sp.Symbol) -> tuple[sp.Rational, ...]:
    p = Poly(f, x, domain=QQ).monic()
    rev = Poly.from_list(list(reversed(p.all_coeffs())), gens=x, domain=QQ).monic()
    return min(tuple(p.all_coeffs()), tuple(rev.all_coeffs()))


def factor_one(pair: tuple[int, int]) -> Result:
    a, b = pair
    x = sp.symbols("x")
    q = qpoly(a, b, x)
    _, factors = sp.factor_list(q.as_expr(), x, domain=QQ)
    irreducible = (
        len(factors) == 1
        and factors[0][1] == 1
        and Poly(factors[0][0], x, domain=QQ).degree() == q.degree()
    )
    keys: list[tuple[sp.Rational, ...]] = []
    for f, exponent in factors:
        key = reciprocal_orbit_key(f, x)
        keys.extend([key] * exponent)
    return Result(a, b, irreducible, tuple(keys))


def package_pairs(maxn: int) -> list[tuple[int, int]]:
    return [
        (a, n - a)
        for n in range(3, maxn + 1)
        for a in range(1, (n - 1) // 2 + 1)
    ]


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-total", type=int, default=60)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args(argv)

    pairs = package_pairs(args.max_total)
    if args.workers == 1:
        results = [factor_one(pair) for pair in pairs]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(factor_one, pairs, chunksize=1))

    results.sort(key=lambda z: (z.a + z.b, z.a, z.b))
    irreducible_by_pair = {(z.a, z.b): z.irreducible for z in results}
    reducible = [(z.a, z.b) for z in results if not z.irreducible]

    seen: dict[tuple[sp.Rational, ...], tuple[int, int]] = {}
    collisions: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for z in results:
        pair = (z.a, z.b)
        for key in z.orbit_keys:
            prior = seen.get(key)
            if prior is not None and prior != pair:
                collisions.append((prior, pair))
            else:
                seen[key] = pair

    globally_certified = 0
    for z in results:
        g = gcd(z.a, z.b)
        base = (z.a // g, z.b // g)
        if irreducible_by_pair[base]:
            globally_certified += 1

    summary = (len(results), reducible, collisions, globally_certified)
    print(*summary)
    if args.max_total == 60:
        assert summary == (870, [], [], 870)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
