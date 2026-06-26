#!/usr/bin/env python3
"""One exact modular-GCD certificate attempt for a selected orientation.

The two input polynomials are
    A*x^(r(A+B)) - (A+B)*x^(rA) + B
and its analogue for the second package.  The smaller polynomial is built
explicitly over F_p.  The larger trinomial is reduced modulo it using two
modular powers, so memory is controlled by the smaller degree.
"""

from __future__ import annotations

import argparse
import json
import resource
import sys
import time

try:
    from flint import ctx, nmod_poly
except ImportError as exc:  # pragma: no cover - environment diagnostic
    print(json.dumps({"ok": False, "error": f"python-flint unavailable: {exc}"}))
    raise SystemExit(2)

ctx.threads = 1


def make_poly(scale: int, low: int, total: int, p: int) -> nmod_poly:
    if not (0 < low < total):
        raise ValueError("orientation endpoint must lie strictly between 0 and total")
    f = nmod_poly([], p)
    f[scale * total] = low % p
    f[scale * low] = (-total) % p
    f[0] = (total - low) % p
    return f


def sparse_remainder(scale: int, low: int, total: int, modulus: nmod_poly, p: int) -> nmod_poly:
    x = nmod_poly([0, 1], p)
    high_power = x.pow_mod(scale * total, modulus)
    middle_power = x.pow_mod(scale * low, modulus)
    return (low * high_power - total * middle_power + (total - low)) % modulus


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, required=True)
    ap.add_argument("--a", type=int, required=True, help="selected first orientation endpoint")
    ap.add_argument("--n", type=int, required=True, help="first primitive total")
    ap.add_argument("--s", type=int, required=True)
    ap.add_argument("--c", type=int, required=True, help="selected second orientation endpoint")
    ap.add_argument("--m", type=int, required=True, help="second primitive total")
    ap.add_argument("--prime", type=int, required=True)
    ap.add_argument("--backend", choices=("auto", "dense", "sparse"), default="auto")
    args = ap.parse_args()

    t0 = time.perf_counter()
    result = {
        "ok": False,
        "prime": args.prime,
        "r": args.r,
        "a": args.a,
        "n": args.n,
        "s": args.s,
        "c": args.c,
        "m": args.m,
        "degree1": args.r * args.n,
        "degree2": args.s * args.m,
    }
    try:
        p = args.prime
        if p <= 2:
            raise ValueError("use an odd auxiliary prime")
        # This good-reduction condition ensures that x=1 has exact
        # multiplicity two in both reductions and that neither trinomial
        # loses its displayed degree.
        bad_product = args.r * args.a * (args.n - args.a) * args.n
        bad_product *= args.s * args.c * (args.m - args.c) * args.m
        if bad_product % p == 0:
            raise ValueError("auxiliary prime divides a scale or additive-triple entry")

        degree1 = args.r * args.n
        degree2 = args.s * args.m
        small_degree = min(degree1, degree2)
        large_degree = max(degree1, degree2)
        ratio = large_degree / small_degree
        backend = args.backend
        if backend == "auto":
            # Dense FLINT gcd is excellent up to moderate displayed degree.
            # Sparse remainder avoids materializing a very large second
            # polynomial when the degree ratio is substantial.
            backend = "sparse" if (large_degree >= 20_000_000 or (large_degree >= 10_000_000 and small_degree <= 300_000)) else "dense"

        if backend == "dense":
            f = make_poly(args.r, args.a, args.n, p)
            g = make_poly(args.s, args.c, args.m, p)
            t1 = time.perf_counter()
            gcd_poly = f.gcd(g)
            t2 = time.perf_counter()
            t3 = t2
            rem_degree = -1
        else:
            if degree1 <= degree2:
                f = make_poly(args.r, args.a, args.n, p)
                t1 = time.perf_counter()
                rem = sparse_remainder(args.s, args.c, args.m, f, p)
                t2 = time.perf_counter()
            else:
                f = make_poly(args.s, args.c, args.m, p)
                t1 = time.perf_counter()
                rem = sparse_remainder(args.r, args.a, args.n, f, p)
                t2 = time.perf_counter()
            gcd_poly = f.gcd(rem)
            t3 = time.perf_counter()
            rem_degree = rem.degree()
        result.update(
            {
                "ok": True,
                "modulus_degree": f.degree(),
                "backend": backend,
                "remainder_degree": rem_degree,
                "gcd_degree": gcd_poly.degree(),
                "build_seconds": t1 - t0,
                "remainder_seconds": (t2 - t1) if backend == "sparse" else 0.0,
                "gcd_seconds": (t3 - t2) if backend == "sparse" else (t2 - t1),
                "total_seconds": t3 - t0,
                "max_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            }
        )
    except Exception as exc:  # return a machine-readable failure to parent
        result["error"] = f"{type(exc).__name__}: {exc}"
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
