#!/usr/bin/env python3
"""Exact post-filter for the unit-normalized Q_{a,b} search.

Input rows are primitive shape pairs produced by pair_upper.cpp under the
full-Kummer branch.  This script applies two further exact finite-field
constraints:

1. Role-binomial degree bounds.  If p divides one member R of the primitive
   additive triple (A,B,A+B), then, modulo p and away from x=0,
   H_{A,A+B}(x^r)=(x^r-1)^2Q_{A,B}(x^r) is a nonzero scalar
   times x^(rR)-1.  A common monic unit factor of degree delta therefore has delta <= rR.  At a prime shared by
   both primitive triples, delta <= gcd(rR,sS).

2. Factor-degree feasibility.  If a degree-delta monic polynomial divides
   x^g-1 over F_p, then delta must be a bounded subset sum of the degrees of
   the irreducible factors of x^g-1, with their exact multiplicities.  We test
   this without constructing x^g-1.

The script also expands the full-radical congruences exactly.  In the
unit/full-Kummer branch, if delta=r*s*k then the two primitive factor degrees
are s*k and r*k, and every prime in rad(A B (A+B)) imposes e == 0 or -2 mod p.
"""

from __future__ import annotations

import argparse
import csv
import functools
import math
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, MutableMapping, Sequence, Tuple

DMAX = 175_394_637


def primes_upto(n: int) -> List[int]:
    sieve = bytearray(b"\x01") * (n + 1)
    if n >= 0:
        sieve[0] = 0
    if n >= 1:
        sieve[1] = 0
    for p in range(2, math.isqrt(n) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : n + 1 : p] = b"\x00" * (((n - start) // p) + 1)
    return [i for i, flag in enumerate(sieve) if flag]


_SMALL_PRIMES = primes_upto(math.isqrt(DMAX) + 1)


@functools.lru_cache(maxsize=None)
def factor_tuple(n: int) -> Tuple[Tuple[int, int], ...]:
    """Return the prime factorization of a positive 32-bit integer."""
    if n < 1:
        raise ValueError(f"factorization requires n>=1, got {n}")
    x = n
    out: List[Tuple[int, int]] = []
    for p in _SMALL_PRIMES:
        if p * p > x:
            break
        if x % p == 0:
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            out.append((p, e))
        if x == 1:
            break
    if x > 1:
        out.append((x, 1))
    return tuple(out)


@functools.lru_cache(maxsize=None)
def prime_support(n: int) -> Tuple[int, ...]:
    return tuple(p for p, _ in factor_tuple(n))


def divisors_from_factorization(fac: Sequence[Tuple[int, int]]) -> List[int]:
    divs = [1]
    for p, e in fac:
        old = list(divs)
        mul = 1
        for _ in range(e):
            mul *= p
            divs.extend(d * mul for d in old)
    return divs


def euler_phi_from_divisor(d: int) -> int:
    result = d
    for p, _ in factor_tuple(d):
        result -= result // p
    return result


def multiplicative_order_mod(a: int, n: int) -> int:
    if n == 1:
        return 1
    if math.gcd(a, n) != 1:
        raise ValueError(f"order undefined: gcd({a},{n}) != 1")
    phi = euler_phi_from_divisor(n)
    order = phi
    for q, _ in factor_tuple(phi):
        while order % q == 0 and pow(a, order // q, n) == 1:
            order //= q
    return order


@functools.lru_cache(maxsize=None)
def factor_degree_capacities(p: int, g: int) -> Tuple[Tuple[int, int], ...]:
    """Degree -> multiplicity capacity for irreducible factors of x^g-1/F_p.

    Write g=p^a h with (h,p)=1.  Each irreducible factor of x^h-1 occurs
    with multiplicity p^a in x^g-1.  For each t|h, Phi_t contributes
    phi(t)/ord_t(p) distinct factors of degree ord_t(p).
    """
    if p < 2 or g < 1:
        raise ValueError("p must be prime and g positive")
    h = g
    mult = 1
    while h % p == 0:
        h //= p
        mult *= p
    caps: Dict[int, int] = defaultdict(int)
    for t in divisors_from_factorization(factor_tuple(h)):
        order = multiplicative_order_mod(p % t if t > 1 else 0, t)
        count = euler_phi_from_divisor(t) // order
        caps[order] += count * mult
    return tuple(sorted(caps.items()))


@functools.lru_cache(maxsize=None)
def degree_reachable(p: int, g: int, degree: int) -> bool:
    """Whether x^g-1 over F_p has a monic divisor of the given degree."""
    if degree < 0 or degree > g:
        return False
    if degree == 0 or degree == g:
        return True

    # Bit j is set iff degree j is reachable.  Truncate after every update.
    bits = 1
    mask = (1 << (degree + 1)) - 1
    for item_degree, capacity in factor_degree_capacities(p, g):
        capacity = min(capacity, degree // item_degree)
        # Binary decomposition of a bounded number of identical items.
        block = 1
        while capacity > 0:
            take = min(block, capacity)
            bits |= bits << (take * item_degree)
            bits &= mask
            if (bits >> degree) & 1:
                return True
            capacity -= take
            block <<= 1
    return bool((bits >> degree) & 1)


def role_value(p: int, a: int, b: int, n: int) -> int:
    hits = [v for v in (a, b, n) if v % p == 0]
    if len(hits) != 1:
        raise ValueError(
            f"primitive additive triple should have one p-role: p={p}, triple={(a,b,n)}, hits={hits}"
        )
    return hits[0]


def inv_mod(a: int, p: int) -> int:
    return pow(a % p, -1, p)


def side_residues(p: int, coefficient: int) -> Tuple[int, ...] | None:
    """k residues for coefficient*k == 0 or -2 (mod p).

    None means every residue is allowed.
    """
    if coefficient % p == 0:
        return None
    z = (-2 * inv_mod(coefficient, p)) % p
    return (0,) if z == 0 else (0, z)


def intersect_optional(a: Tuple[int, ...] | None, b: Tuple[int, ...] | None) -> Tuple[int, ...] | None:
    if a is None:
        return b
    if b is None:
        return a
    sb = set(b)
    return tuple(x for x in a if x in sb)


def crt_expand(
    current_residues: Sequence[int], current_modulus: int, p: int, allowed: Sequence[int]
) -> Tuple[List[int], int]:
    if current_modulus % p == 0:
        raise ValueError("CRT moduli are not coprime")
    inv = inv_mod(current_modulus, p)
    out: List[int] = []
    for x in current_residues:
        for y in allowed:
            t = ((y - x) % p) * inv % p
            out.append(x + current_modulus * t)
    return out, current_modulus * p


def values_in_interval(residue: int, modulus: int, lo: int, hi: int) -> Iterator[int]:
    first = lo + ((residue - lo) % modulus)
    if first > hi:
        return
    yield from range(first, hi + 1, modulus)


@dataclass(frozen=True)
class CandidateRow:
    r: int
    a: int
    b: int
    n: int
    s: int
    c: int
    d_endpoint: int
    m: int
    D: int
    k_lo: int
    k_hi: int
    radprod1: int
    radprod2: int

    @classmethod
    def from_csv(cls, row: Mapping[str, str]) -> "CandidateRow":
        return cls(
            r=int(row["r"]),
            a=int(row["a"]),
            b=int(row["b"]),
            n=int(row["n"]),
            s=int(row["s"]),
            c=int(row["c"]),
            d_endpoint=int(row["d"]),
            m=int(row["m"]),
            D=int(row["D"]),
            k_lo=int(row["k_lo"]),
            k_hi=int(row["k_hi"]),
            radprod1=int(row["radprod1"]),
            radprod2=int(row["radprod2"]),
        )

    @property
    def support1(self) -> Tuple[int, ...]:
        return prime_support(self.radprod1)

    @property
    def support2(self) -> Tuple[int, ...]:
        return prime_support(self.radprod2)

    def exponent_bound_and_binomials(self) -> Tuple[int, Tuple[Tuple[int, int], ...]]:
        """Return delta upper bound and all (p,g) binomial constraints."""
        p1 = set(self.support1)
        p2 = set(self.support2)
        bound = min(self.n, self.m) - 2
        constraints: List[Tuple[int, int]] = []
        for p in sorted(p1 | p2):
            e1 = self.r * role_value(p, self.a, self.b, self.n) if p in p1 else None
            e2 = self.s * role_value(p, self.c, self.d_endpoint, self.m) if p in p2 else None
            if e1 is not None and e2 is not None:
                g = math.gcd(e1, e2)
            else:
                g = e1 if e1 is not None else e2
            assert g is not None
            bound = min(bound, g)
            constraints.append((p, g))
        return bound, tuple(constraints)

    def exact_k_values(self, hi: int) -> List[int]:
        if self.k_lo > hi:
            return []
        residues: List[int] = [0]
        modulus = 1
        p1 = set(self.support1)
        p2 = set(self.support2)
        for p in sorted(p1 | p2):
            allow1 = side_residues(p, self.s) if p in p1 else None
            allow2 = side_residues(p, self.r) if p in p2 else None
            allowed = intersect_optional(allow1, allow2)
            if allowed is None:
                continue
            if not allowed:
                return []
            residues, modulus = crt_expand(residues, modulus, p, allowed)
        out: List[int] = []
        for residue in residues:
            out.extend(values_in_interval(residue, modulus, self.k_lo, hi))
        return sorted(set(out))


OUTPUT_FIELDS = [
    "r",
    "a",
    "b",
    "n",
    "s",
    "c",
    "d_endpoint",
    "m",
    "D",
    "k",
    "degree",
    "primitive_degree_1",
    "primitive_degree_2",
    "radprod1",
    "radprod2",
    "binomial_degree_bound",
]


def process(input_path: Path, output_path: Path, *, shared_only: bool = False) -> Dict[str, int | float]:
    t0 = time.perf_counter()
    with input_path.open(newline="") as f:
        input_rows = [CandidateRow.from_csv(row) for row in csv.DictReader(f)]

    after_interval = 0
    after_crt = 0
    after_factor_degree = 0
    output_rows: List[Dict[str, int]] = []
    surviving_pairs = set()

    for row in input_rows:
        degree_bound, binomial_constraints = row.exponent_bound_and_binomials()
        hi = min(row.k_hi, degree_bound // (row.r * row.s))
        if row.k_lo > hi:
            continue
        after_interval += 1

        exact_ks = row.exact_k_values(hi)
        after_crt += len(exact_ks)
        p1 = set(row.support1)
        p2 = set(row.support2)
        if shared_only:
            binomial_constraints = tuple((p, g) for p, g in binomial_constraints if p in p1 and p in p2)

        for k in exact_ks:
            degree = row.r * row.s * k
            if all(degree_reachable(p, g, degree) for p, g in binomial_constraints):
                after_factor_degree += 1
                key = (row.r, row.a, row.b, row.n, row.s, row.c, row.d_endpoint, row.m)
                surviving_pairs.add(key)
                output_rows.append(
                    {
                        "r": row.r,
                        "a": row.a,
                        "b": row.b,
                        "n": row.n,
                        "s": row.s,
                        "c": row.c,
                        "d_endpoint": row.d_endpoint,
                        "m": row.m,
                        "D": row.D,
                        "k": k,
                        "degree": degree,
                        "primitive_degree_1": row.s * k,
                        "primitive_degree_2": row.r * k,
                        "radprod1": row.radprod1,
                        "radprod2": row.radprod2,
                        "binomial_degree_bound": degree_bound,
                    }
                )

    output_rows.sort(key=lambda z: tuple(z[field] for field in OUTPUT_FIELDS))
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    elapsed = time.perf_counter() - t0
    return {
        "input_package_pairs": len(input_rows),
        "after_binomial_interval": after_interval,
        "exact_k_candidates_after_CRT": after_crt,
        "degree_candidates_after_factor_feasibility": after_factor_degree,
        "distinct_package_pairs_after_factor_feasibility": len(surviving_pairs),
        "seconds": elapsed,
        "factor_cache_entries": factor_tuple.cache_info().currsize,
        "degree_reachability_cache_entries": degree_reachable.cache_info().currsize,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "upper_pair_survivors.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "upper_exact_degree_candidates.csv",
    )
    parser.add_argument(
        "--shared-only",
        action="store_true",
        help="apply factor-degree feasibility only at primes shared by both triples",
    )
    args = parser.parse_args(argv)
    try:
        stats = process(args.input, args.output, shared_only=args.shared_only)
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for key, value in stats.items():
        print(f"{key}={value}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
