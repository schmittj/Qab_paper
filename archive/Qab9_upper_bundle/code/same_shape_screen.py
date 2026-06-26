#!/usr/bin/env python3
"""Final exact screen for the upper unit range.

For two coprime scales r,s applied to the same primitive shape, the two
power-correspondence curves on P^1 x P^1 have intersection number 2*r*s and
no common component unless the packages coincide.  A common irreducible
factor therefore has degree at most 2*r*s.

The input may contain exact degrees (field ``degree``) or only k-ranges from
``pair_upper``.  In the latter case the exact algebraic certificate
``theta_0^70 > 2*D_MAX`` supplies the integer lower bound d >= floor(D/140)+1.
No floating-point arithmetic is used.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "upper_pair_survivors.csv",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "upper_residual_candidates.csv",
    )
    args = ap.parse_args(argv)

    with args.input.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise SystemExit("input has no CSV header")
        rows = list(reader)
        fields = reader.fieldnames + ["degree_lower_used", "same_shape_bound"]
        second_endpoint_key = "d_endpoint" if "d_endpoint" in reader.fieldnames else "d"

    residual = []
    same_shape = 0
    bounded = 0
    margins: list[int] = []
    for row in rows:
        shape1 = (int(row["a"]), int(row["b"]), int(row["n"]))
        shape2 = (int(row["c"]), int(row[second_endpoint_key]), int(row["m"]))
        r, s = int(row["r"]), int(row["s"])
        degree_lower = int(row["degree"]) if "degree" in row else int(row["D"]) // 140 + 1
        bound = 2 * r * s
        row["degree_lower_used"] = str(degree_lower)
        row["same_shape_bound"] = str(bound)
        if shape1 == shape2:
            same_shape += 1
            margins.append(degree_lower - bound)
            if degree_lower > bound:
                bounded += 1
                continue
        residual.append(row)

    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(residual)

    distinct_pairs = {
        tuple(row[k] for k in ("r", "a", "b", "n", "s", "c", second_endpoint_key, "m"))
        for row in rows
    }
    print(f"input_rows={len(rows)}")
    print(f"input_distinct_package_pairs={len(distinct_pairs)}")
    print(f"same_shape_rows={same_shape}")
    print(f"eliminated_by_degree_lower_gt_2rs={bounded}")
    print(f"residual_candidates={len(residual)}")
    if margins:
        print(f"minimum_uniform_degree_margin={min(margins)}")
    print(f"output={args.output}")
    return 0 if not residual else 3


if __name__ == "__main__":
    raise SystemExit(main())
