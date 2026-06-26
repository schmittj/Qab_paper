#!/usr/bin/env python3
"""Verifier for the corrected residual one-nonunit Qab12 branch."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from itertools import combinations
from pathlib import Path

UINT32_MAX = 2**32 - 1
PACKAGE_FIELDS = ["U", "d", "sigma1", "sigma2", "sigma3", "sigma4", "sigma5", "r", "t", "e", "a", "b", "n"]
STATE_FIELDS = [
    "U", "d", "sigma1", "sigma2", "sigma3", "sigma4", "sigma5",
    "r", "t", "e1", "a", "b", "n", "s", "u", "e2", "c", "f", "m",
    "D", "correspondence_bound", "role_bound",
]
ORIENTATION_FIELDS = ["U", "r", "a", "b", "n", "s", "c", "f", "m"]
STAGES = [
    "package_records", "groups", "raw_state_pairs", "after_coprime_scales",
    "after_range", "after_extraction", "after_disjoint", "after_support",
    "after_degree", "after_role", "after_correspondence",
    "unique_state_pairs", "unique_orientation_pairs",
]


def fail(msg: str) -> None:
    raise RuntimeError(msg)


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


def defects(r: int, t: int) -> set[int]:
    return {p for p, a in fac(r) if val(t, p) < a}


def degree_upper(D: int) -> int:
    lo, hi = 0, 200000
    while lo < hi:
        m = (lo + hi + 1) // 2
        if m**3 < 64 * D * D:
            lo = m
        else:
            hi = m - 1
    return lo


def check_endpoint(row: dict[str, int], path: Path, line: int) -> None:
    U, r, t, e, a, b = (row[k] for k in ("U", "r", "t", "e", "a", "b"))
    uf = fac(U)
    af = dict(fac(a))
    if U <= 1 or len(uf) > 5:
        fail(f"{path}:{line}: invalid coefficient support")
    for p, A in uf:
        if p not in af or A > af[p]:
            fail(f"{path}:{line}: coefficient does not divide leading endpoint")

    sigmas = [row[f"sigma{i}"] for i in range(1, 6)]
    expected = []
    D = defects(r, t)
    for p, kappa in fac(a):
        A = val(U, p)
        if A == 0:
            if p in D:
                fail(f"{path}:{line}: deficient endpoint prime omitted from coefficient")
            if e % p not in (0, (p - 2) % p):
                fail(f"{path}:{line}: omitted endpoint prime has bad unit signature")
            continue
        if (r * A) % t:
            fail(f"{path}:{line}: nonintegral norm-transfer exponent")
        lam = r * A // t
        if not (1 <= lam <= kappa) or (b * lam) % kappa:
            fail(f"{path}:{line}: packet occupancy integrality")
        w = b * lam // kappa
        if not (1 <= w <= min(b, e)):
            fail(f"{path}:{line}: packet occupancy range")
        if (e - w) % p not in (0, (p - 2) % p):
            fail(f"{path}:{line}: packet residual signature")
        if p in D and (p > 7 or kappa < p or (e * kappa) % (p * b)):
            fail(f"{path}:{line}: deficient endpoint condition")
        expected.append(t * w)
    if sigmas[:len(expected)] != expected or any(sigmas[len(expected):]):
        fail(f"{path}:{line}: sigma mismatch got={sigmas} expected={expected}")


def check_package_row(row: dict[str, int], path: Path, line: int, Dcap: int, dmax: int, rmax: int) -> None:
    U, d, r, t, e, a, b, n = (row[k] for k in ("U", "d", "r", "t", "e", "a", "b", "n"))
    if not (2 <= U <= Dcap):
        fail(f"{path}:{line}: U outside residual range")
    if not (1 <= t <= r <= rmax and d == t * e and 2 <= e and d <= dmax):
        fail(f"{path}:{line}: extraction data")
    if a + b != n or math.gcd(a, b) != 1 or a < 2 or b < 1:
        fail(f"{path}:{line}: primitive additive triple")
    if not (n >= e + 4 and r * n <= Dcap):
        fail(f"{path}:{line}: package size condition")
    unit_support = supp(e) | supp(e + 2)
    if not supp(b) <= unit_support:
        fail(f"{path}:{line}: unit constant endpoint support")
    if not supp(n) <= unit_support:
        fail(f"{path}:{line}: total endpoint support")
    check_endpoint(row, path, line)
    U_support = supp(U)
    for q in defects(r, t):
        if q in U_support:
            continue
        if a % q == 0 or b % q == 0 or n % q == 0:
            fail(f"{path}:{line}: deficient noncoefficient prime appears in shape")
        if e > q - 2:
            fail(f"{path}:{line}: deficient good-prime degree bound")


def read_package_rows(path: Path, Dcap: int, dmax: int, rmax: int) -> list[dict[str, int]]:
    rows = []
    seen = set()
    last = None
    with path.open(newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != PACKAGE_FIELDS:
            fail(f"{path}: bad header {rd.fieldnames}")
        for line, row in enumerate(rd, 2):
            z = {k: int(row[k]) for k in PACKAGE_FIELDS}
            check_package_row(z, path, line, Dcap, dmax, rmax)
            key = tuple(z[k] for k in PACKAGE_FIELDS)
            if key in seen:
                fail(f"{path}:{line}: duplicate package row")
            seen.add(key)
            canonical = tuple(z[k] for k in ["U", "d", "sigma1", "sigma2", "sigma3", "sigma4", "sigma5", "r", "t", "e", "n", "a", "b"])
            if last is not None and canonical <= last:
                fail(f"{path}:{line}: package rows are not strictly sorted")
            last = canonical
            rows.append(z)
    return rows


def shape_support(z: dict[str, int], names: tuple[str, str, str] = ("a", "b", "n")) -> set[int]:
    out: set[int] = set()
    for k in names:
        out |= supp(z[k])
    return out


def role_value(p: int, z: dict[str, int], names: tuple[str, str, str] = ("a", "b", "n")) -> int:
    vals = [z[k] for k in names if z[k] % p == 0]
    if len(vals) != 1:
        fail("primitive role invariant failed")
    return vals[0]


def same_package(x: dict[str, int], y: dict[str, int]) -> bool:
    return sorted((x["r"] * x["a"], x["r"] * x["b"])) == sorted((y["r"] * y["a"], y["r"] * y["b"]))


def disjoint(x: dict[str, int], y: dict[str, int]) -> bool:
    X = {x["r"] * x[k] for k in ("a", "b", "n")}
    Y = {y["r"] * y[k] for k in ("a", "b", "n")}
    return X.isdisjoint(Y)


def support_compatible(x: dict[str, int], y: dict[str, int]) -> bool:
    X = shape_support(x)
    Y = shape_support(y)
    C = supp(x["U"])
    for p in X:
        if p >= 5 and p not in Y and p not in C and y["r"] % p != 0:
            return False
    for p in Y:
        if p >= 5 and p not in X and p not in C and x["r"] % p != 0:
            return False
    return True


def correspondence_bound(x: dict[str, int], y: dict[str, int]) -> int:
    g0 = math.gcd(x["r"] * x["b"], y["r"] * y["b"])
    g1 = math.gcd(x["r"] * x["a"], y["r"] * y["a"])
    return (y["r"] * y["b"] // g0) * (x["r"] * x["a"] // g1) + (x["r"] * x["b"] // g0) * (y["r"] * y["a"] // g1)


def role_bound(x: dict[str, int], y: dict[str, int]) -> int:
    X = shape_support(x)
    Y = shape_support(y)
    C = supp(x["U"])
    best = UINT32_MAX
    used = False
    for p in X | Y:
        if p in C:
            continue
        if p in X and p in Y:
            v = math.gcd(x["r"] * role_value(p, x), y["r"] * role_value(p, y))
        elif p in X:
            v = x["r"] * role_value(p, x)
        else:
            v = y["r"] * role_value(p, y)
        best = min(best, v)
        used = True
    return best if used else UINT32_MAX


def same_shape(x: dict[str, int], y: dict[str, int]) -> bool:
    return (x["a"] == y["a"] and x["b"] == y["b"]) or (x["a"] == y["b"] and x["b"] == y["a"])


def state_tuple(x: dict[str, int], y: dict[str, int], D: int, cb: int, rb: int) -> tuple[int, ...]:
    return tuple(
        [x["U"], x["d"]]
        + [x[f"sigma{i}"] for i in range(1, 6)]
        + [x["r"], x["t"], x["e"], x["a"], x["b"], x["n"], y["r"], y["t"], y["e"], y["a"], y["b"], y["n"], D, cb, rb]
    )


def pair_sieve(rows: list[dict[str, int]], Dcap: int) -> tuple[dict[str, int], set[tuple[int, ...]], set[tuple[int, ...]]]:
    groups: dict[tuple[int, ...], list[dict[str, int]]] = {}
    for z in rows:
        key = tuple([z["U"], z["d"]] + [z[f"sigma{i}"] for i in range(1, 6)])
        groups.setdefault(key, []).append(z)

    counts = {k: 0 for k in STAGES}
    counts["package_records"] = len(rows)
    counts["groups"] = len(groups)
    states: set[tuple[int, ...]] = set()
    orientations: set[tuple[int, ...]] = set()

    for g in groups.values():
        for x0, y0 in combinations(g, 2):
            counts["raw_state_pairs"] += 1
            x = dict(x0)
            y = dict(y0)
            if math.gcd(x["r"], y["r"]) != 1:
                continue
            counts["after_coprime_scales"] += 1
            if same_package(x, y):
                continue
            D = max(x["r"] * x["n"], y["r"] * y["n"])
            if D > Dcap:
                continue
            counts["after_range"] += 1
            if x["d"] > x["e"] * y["e"]:
                continue
            counts["after_extraction"] += 1
            if not disjoint(x, y):
                continue
            counts["after_disjoint"] += 1
            if not support_compatible(x, y):
                continue
            counts["after_support"] += 1
            if x["d"] ** 3 >= 64 * D * D or x["d"] > min(x["n"], y["n"]) - 2:
                continue
            counts["after_degree"] += 1
            rb = role_bound(x, y)
            if rb != UINT32_MAX and x["d"] > rb:
                continue
            counts["after_role"] += 1
            cb = correspondence_bound(x, y)
            if same_shape(x, y):
                cb = min(cb, 2 * x["r"] * y["r"])
            if x["d"] > cb:
                continue
            counts["after_correspondence"] += 1
            if (y["r"], y["a"], y["b"], y["t"], y["e"]) < (x["r"], x["a"], x["b"], x["t"], x["e"]):
                x, y = y, x
            states.add(state_tuple(x, y, D, min(cb, UINT32_MAX), rb))
            orientations.add((x["U"], x["r"], x["a"], x["b"], x["n"], y["r"], y["a"], y["b"], y["n"]))

    counts["unique_state_pairs"] = len(states)
    counts["unique_orientation_pairs"] = len(orientations)
    return counts, states, orientations


def parse_pair_log(path: Path) -> dict[str, int]:
    vals = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", path.read_text())}
    missing = [k for k in STAGES if k not in vals]
    if missing:
        fail(f"{path}: missing counters {missing}")
    return {k: vals[k] for k in STAGES}


def read_tuple_csv(path: Path, fields: list[str]) -> set[tuple[int, ...]]:
    with path.open(newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != fields:
            fail(f"{path}: bad header {rd.fieldnames}")
        return {tuple(int(row[k]) for k in fields) for row in rd}


def trim(f: list[int]) -> list[int]:
    while len(f) > 1 and f[-1] == 0:
        f.pop()
    if not f:
        f.append(0)
    return f


def poly_mod(f: list[int], g: list[int], p: int) -> list[int]:
    f = f[:]
    g = trim(g[:])
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


def verify_modular_certificates(pairs_path: Path, cert_path: Path) -> tuple[int, int]:
    pairs = []
    with pairs_path.open(newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != ORIENTATION_FIELDS:
            fail(f"{pairs_path}: bad orientation header")
        for row in rd:
            pairs.append({k: int(row[k]) for k in ORIENTATION_FIELDS})

    seen = set()
    with cert_path.open(newline="") as f:
        rd = csv.DictReader(f)
        expected_fields = [
            "pair_index", "orientation", "U", "r", "a", "b", "n", "s", "c", "f", "m",
            "low1", "low2", "prime", "gcd_degree",
        ]
        if rd.fieldnames != expected_fields:
            fail(f"{cert_path}: bad certificate header")
        for line, row in enumerate(rd, 2):
            z = {k: int(row[k]) for k in expected_fields}
            i, orientation = z["pair_index"], z["orientation"]
            if not (0 <= i < len(pairs) and 0 <= orientation < 4):
                fail(f"{cert_path}:{line}: bad task index")
            if (i, orientation) in seen:
                fail(f"{cert_path}:{line}: duplicate task")
            seen.add((i, orientation))
            pair = pairs[i]
            for k in ORIENTATION_FIELDS:
                if z[k] != pair[k]:
                    fail(f"{cert_path}:{line}: package pair mismatch")
            if pair["a"] + pair["b"] != pair["n"] or pair["c"] + pair["f"] != pair["m"]:
                fail(f"{cert_path}:{line}: additive triple mismatch")
            low1 = (pair["a"], pair["b"])[orientation // 2]
            low2 = (pair["c"], pair["f"])[orientation % 2]
            if (z["low1"], z["low2"]) != (low1, low2):
                fail(f"{cert_path}:{line}: orientation mismatch")
            p = z["prime"]
            if p <= 2 or any(pair[k] % p == 0 for k in ("r", "a", "b", "n", "s", "c", "f", "m")):
                fail(f"{cert_path}:{line}: bad reduction prime")
            got = gcd_degree(pair["r"], low1, pair["n"], pair["s"], low2, pair["m"], p)
            if z["gcd_degree"] != 2 or got != 2:
                fail(f"{cert_path}:{line}: gcd degree mismatch got={got} cert={z['gcd_degree']}")
    expected = {(i, o) for i in range(len(pairs)) for o in range(4)}
    if seen != expected:
        fail(f"{cert_path}: certificate coverage mismatch")
    return len(pairs), len(seen)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packages", type=Path, default=Path("data/qab12/one_nonunit_residual_packages.csv"))
    ap.add_argument("--state-pairs", type=Path, default=Path("data/qab12/one_nonunit_residual_state_pairs.csv"))
    ap.add_argument("--orientation-pairs", type=Path, default=Path("data/qab12/one_nonunit_residual_orientation_pairs.csv"))
    ap.add_argument("--pair-log", type=Path, default=Path("data/qab12/one_nonunit_residual_pair_output.txt"))
    ap.add_argument("--certificates", type=Path, default=Path("data/qab12/one_nonunit_residual_modular_certificates.csv"))
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--D-cap", type=int, default=16583)
    ap.add_argument("--d-max", type=int)
    ap.add_argument("--r-max", type=int, default=139)
    args = ap.parse_args()

    dmax = args.d_max if args.d_max is not None else degree_upper(args.D_cap)
    rows = read_package_rows(args.packages, args.D_cap, dmax, args.r_max)
    expected_counts, expected_states, expected_orientations = pair_sieve(rows, args.D_cap)
    logged_counts = parse_pair_log(args.pair_log)
    if logged_counts != expected_counts:
        fail(f"pair counter mismatch: logged={logged_counts} expected={expected_counts}")

    got_states = read_tuple_csv(args.state_pairs, STATE_FIELDS)
    got_orientations = read_tuple_csv(args.orientation_pairs, ORIENTATION_FIELDS)
    if got_states != expected_states:
        fail(f"state-pair CSV mismatch got={len(got_states)} expected={len(expected_states)}")
    if got_orientations != expected_orientations:
        fail(f"orientation-pair CSV mismatch got={len(got_orientations)} expected={len(expected_orientations)}")

    package_pairs, orientation_certs = verify_modular_certificates(args.orientation_pairs, args.certificates)

    manifest = {
        "schema": "qab12-one-nonunit-residual-v1",
        "status": "PASS",
        "range": {"D_max": args.D_cap, "d_max": dmax, "U_min": 2, "U_max": args.D_cap},
        "pair_counts": expected_counts,
        "modular_certificates": {
            "package_pairs": package_pairs,
            "orientation_certificates": orientation_certs,
            "required_gcd_degree": 2,
        },
        "sha256": {
            "packages": sha256(args.packages),
            "state_pairs": sha256(args.state_pairs),
            "orientation_pairs": sha256(args.orientation_pairs),
            "pair_log": sha256(args.pair_log),
            "certificates": sha256(args.certificates),
        },
    }
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    print(f"verified_one_nonunit_residual_package_states={len(rows)}")
    for k in STAGES:
        print(f"residual_{k}={expected_counts[k]}")
    print(f"verified_residual_package_pairs={package_pairs}")
    print(f"verified_residual_orientation_certificates={orientation_certs}")
    print("status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
