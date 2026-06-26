#!/usr/bin/env python3
"""Resumable adaptive modular-GCD screen for upper-range Q_ab candidates.

A package pair has four possible reciprocal orientations.  For each one we
search for a good auxiliary prime p at which the modular gcd has degree 2.
Because both collision trinomials contain (x-1)^2, and because an upper-range
common factor is monic, gcd degree 2 is a rigorous certificate that the chosen
orientation has no noncyclotomic common factor over Q.

Each expensive FLINT call runs in a subprocess.  This permits hard timeouts
and retries at fresh primes when a particular finite field is unlucky.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import math
import os
import signal
from pathlib import Path
import subprocess
import sys
import time
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
WORKER = SCRIPT_DIR / "gcd_orientation_worker.py"


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d = 41
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def prime_pool(start: int, count: int) -> List[int]:
    out: List[int] = []
    n = start if start % 2 else start - 1
    while n >= 3 and len(out) < count:
        if is_prime(n):
            out.append(n)
        n -= 2
    if len(out) < count:
        raise ValueError("not enough primes in requested range")
    return out


def package_key(row: Mapping[str, str]) -> Tuple[int, ...]:
    return tuple(int(row[k]) for k in ("r", "a", "b", "n", "s", "c", "d_endpoint", "m"))


def read_unique_pairs(path: Path) -> List[Tuple[int, ...]]:
    unique: Dict[Tuple[int, ...], None] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            unique.setdefault(package_key(row), None)
    return list(unique)


def task_key(pair_index: int, orientation: int) -> Tuple[int, int]:
    return pair_index, orientation


def orientation_endpoints(pair: Tuple[int, ...], orientation: int) -> Tuple[int, int]:
    _, a, b, _, _, c, d, _ = pair
    return (a, b)[orientation // 2], (c, d)[orientation % 2]


def run_worker(
    pair_index: int,
    pair: Tuple[int, ...],
    orientation: int,
    primes: Sequence[int],
    timeout: float,
    max_attempts: int,
    backend: str,
) -> Dict[str, object]:
    r, a, b, n, s, c, d, m = pair
    low1, low2 = orientation_endpoints(pair, orientation)
    attempts: List[Dict[str, object]] = []
    used = 0
    bad_product = r * a * b * n * s * c * d * m

    for p in primes:
        if bad_product % p == 0:
            continue
        if used >= max_attempts:
            break
        used += 1
        cmd = [
            sys.executable,
            str(WORKER),
            "--r",
            str(r),
            "--a",
            str(low1),
            "--n",
            str(n),
            "--s",
            str(s),
            "--c",
            str(low2),
            "--m",
            str(m),
            "--prime",
            str(p),
            "--backend",
            backend,
        ]
        started = time.perf_counter()
        proc = subprocess.Popen(
            cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            elapsed = time.perf_counter() - started
            payload: Dict[str, object]
            try:
                payload = json.loads(stdout.strip().splitlines()[-1])
            except (json.JSONDecodeError, IndexError):
                payload = {
                    "ok": False,
                    "error": "worker returned no valid JSON",
                    "stdout_tail": stdout[-1000:],
                    "stderr_tail": stderr[-1000:],
                }
            payload["wall_seconds_parent"] = elapsed
            payload["returncode"] = proc.returncode
            attempts.append(payload)
            if payload.get("ok") and int(payload.get("gcd_degree", -1)) == 2:
                return {
                    "pair_index": pair_index,
                    "orientation": orientation,
                    "status": "certified",
                    "prime": p,
                    "gcd_degree": 2,
                    "attempt_count": used,
                    "attempts": attempts,
                    "pair": pair,
                    "low1": low1,
                    "low2": low2,
                }
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            attempts.append(
                {
                    "ok": False,
                    "prime": p,
                    "backend": backend,
                    "error": f"timeout after {timeout} seconds",
                    "wall_seconds_parent": time.perf_counter() - started,
                    "stdout_tail": stdout[-1000:],
                    "stderr_tail": stderr[-1000:],
                }
            )

    return {
        "pair_index": pair_index,
        "orientation": orientation,
        "status": "unresolved",
        "attempt_count": used,
        "attempts": attempts,
        "pair": pair,
        "low1": low1,
        "low2": low2,
    }


CERT_FIELDS = [
    "pair_index",
    "orientation",
    "r",
    "a",
    "b",
    "n",
    "s",
    "c",
    "d_endpoint",
    "m",
    "low1",
    "low2",
    "prime",
    "gcd_degree",
    "attempt_count",
    "total_seconds",
    "max_rss_kb",
    "backend",
]


def load_completed(path: Path) -> set[Tuple[int, int]]:
    if not path.exists():
        return set()
    with path.open(newline="") as f:
        return {(int(r["pair_index"]), int(r["orientation"])) for r in csv.DictReader(f)}


def append_certificate(path: Path, result: Mapping[str, object]) -> None:
    pair = tuple(int(x) for x in result["pair"])  # type: ignore[arg-type]
    r, a, b, n, s, c, d, m = pair
    successful = next(
        attempt
        for attempt in result["attempts"]  # type: ignore[assignment]
        if attempt.get("ok") and int(attempt.get("gcd_degree", -1)) == 2
    )
    row = {
        "pair_index": result["pair_index"],
        "orientation": result["orientation"],
        "r": r,
        "a": a,
        "b": b,
        "n": n,
        "s": s,
        "c": c,
        "d_endpoint": d,
        "m": m,
        "low1": result["low1"],
        "low2": result["low2"],
        "prime": result["prime"],
        "gcd_degree": 2,
        "attempt_count": result["attempt_count"],
        "total_seconds": successful.get("total_seconds", successful.get("wall_seconds_parent", "")),
        "max_rss_kb": successful.get("max_rss_kb", ""),
        "backend": successful.get("backend", ""),
    }
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CERT_FIELDS)
        if not exists:
            w.writeheader()
        w.writerow(row)
        f.flush()
        os.fsync(f.fileno())


def write_unresolved(path: Path, results: Sequence[Mapping[str, object]]) -> None:
    with path.open("w") as f:
        for result in results:
            f.write(json.dumps(result, sort_keys=True) + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--input",
        type=Path,
        default=SCRIPT_DIR.parent / "data" / "upper_exact_degree_candidates.csv",
    )
    ap.add_argument("--certificates", type=Path, default=SCRIPT_DIR.parent / "data" / "upper_modular_certificates.csv")
    ap.add_argument("--unresolved", type=Path, default=SCRIPT_DIR.parent / "data" / "upper_modular_unresolved.jsonl")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--attempts", type=int, default=8)
    ap.add_argument("--prime-start", type=int, default=65_537)
    ap.add_argument("--backend", choices=("auto", "dense", "sparse"), default="auto")
    ap.add_argument("--prime-count", type=int, default=80)
    ap.add_argument("--start-pair", type=int, default=0)
    ap.add_argument("--pair-limit", type=int, default=None)
    args = ap.parse_args(argv)

    if args.workers < 1:
        ap.error("--workers must be positive")
    pairs = read_unique_pairs(args.input)
    stop = len(pairs) if args.pair_limit is None else min(len(pairs), args.start_pair + args.pair_limit)
    selected = list(enumerate(pairs))[args.start_pair:stop]
    completed = load_completed(args.certificates)
    tasks = [
        (i, pair, orientation)
        for i, pair in selected
        for orientation in range(4)
        if task_key(i, orientation) not in completed
    ]
    primes = prime_pool(args.prime_start, args.prime_count)
    print(
        f"unique_pairs={len(pairs)} selected_pairs={len(selected)} pending_orientations={len(tasks)} "
        f"workers={args.workers}",
        flush=True,
    )

    unresolved: List[Mapping[str, object]] = []
    certified = 0
    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(run_worker, i, pair, orientation, primes, args.timeout, args.attempts, args.backend): (i, orientation)
            for i, pair, orientation in tasks
        }
        for future in concurrent.futures.as_completed(futures):
            i, orientation = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {
                    "pair_index": i,
                    "orientation": orientation,
                    "status": "driver_error",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            if result.get("status") == "certified":
                append_certificate(args.certificates, result)
                certified += 1
                print(
                    f"certified pair={i} orientation={orientation} prime={result['prime']} "
                    f"attempts={result['attempt_count']}",
                    flush=True,
                )
            else:
                unresolved.append(result)
                print(f"unresolved pair={i} orientation={orientation}", flush=True)

    write_unresolved(args.unresolved, unresolved)
    elapsed = time.perf_counter() - t0
    print(f"certified_orientations={certified}")
    print(f"unresolved_orientations={len(unresolved)}")
    print(f"elapsed_seconds={elapsed}")
    print(f"certificates={args.certificates}")
    print(f"unresolved={args.unresolved}")
    return 0 if not unresolved else 3


if __name__ == "__main__":
    raise SystemExit(main())
