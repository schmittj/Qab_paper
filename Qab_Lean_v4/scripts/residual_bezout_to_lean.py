#!/usr/bin/env python3
"""Generate Lean Bezout certificates for the residual ZMod 1009 rows."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

MODULUS = 1009
FORCED_FACTOR = [1, MODULUS - 2, 1]


def trim(poly: list[int]) -> list[int]:
    while len(poly) > 1 and poly[-1] % MODULUS == 0:
        poly.pop()
    if not poly:
        return [0]
    return [x % MODULUS for x in poly]


def add(left: list[int], right: list[int]) -> list[int]:
    size = max(len(left), len(right))
    out = [0] * size
    for idx in range(size):
        a = left[idx] if idx < len(left) else 0
        b = right[idx] if idx < len(right) else 0
        out[idx] = (a + b) % MODULUS
    return trim(out)


def sub(left: list[int], right: list[int]) -> list[int]:
    size = max(len(left), len(right))
    out = [0] * size
    for idx in range(size):
        a = left[idx] if idx < len(left) else 0
        b = right[idx] if idx < len(right) else 0
        out[idx] = (a - b) % MODULUS
    return trim(out)


def mul(left: list[int], right: list[int]) -> list[int]:
    if left == [0] or right == [0]:
        return [0]
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        if a == 0:
            continue
        for j, b in enumerate(right):
            if b != 0:
                out[i + j] = (out[i + j] + a * b) % MODULUS
    return trim(out)


def monomial(degree: int, coeff: int) -> list[int]:
    coeff %= MODULUS
    if coeff == 0:
        return [0]
    return [0] * degree + [coeff]


def divmod_poly(numerator: list[int], denominator: list[int]) -> tuple[list[int], list[int]]:
    numerator = trim(numerator[:])
    denominator = trim(denominator[:])
    if denominator == [0]:
        raise ZeroDivisionError("polynomial division by zero")

    quotient = [0]
    denominator_lc_inv = pow(denominator[-1], -1, MODULUS)
    while numerator != [0] and len(numerator) >= len(denominator):
        shift = len(numerator) - len(denominator)
        coeff = numerator[-1] * denominator_lc_inv % MODULUS
        term = monomial(shift, coeff)
        quotient = add(quotient, term)
        numerator = sub(numerator, mul(term, denominator))
    return trim(quotient), trim(numerator)


def egcd(left: list[int], right: list[int]) -> tuple[list[int], list[int], list[int]]:
    r0, r1 = trim(left[:]), trim(right[:])
    s0, s1 = [1], [0]
    t0, t1 = [0], [1]

    while r1 != [0]:
        quotient, r2 = divmod_poly(r0, r1)
        r0, r1 = r1, r2
        s0, s1 = s1, sub(s0, mul(quotient, s1))
        t0, t1 = t1, sub(t0, mul(quotient, t1))

    lc_inv = pow(r0[-1], -1, MODULUS)
    return mul([lc_inv], r0), mul([lc_inv], s0), mul([lc_inv], t0)


def collision_poly(scale: int, low: int, total: int) -> list[int]:
    poly = [0]
    poly = add(poly, monomial(scale * total, low))
    poly = add(poly, monomial(scale * low, -total))
    poly = add(poly, monomial(0, total - low))
    return poly


def read_rows(path: Path) -> list[dict[str, int]]:
    with path.open(newline="") as handle:
        return [{key: int(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def lean_nat_list(values: list[int], open_indent: str = "    ", item_indent: str = "      ") -> str:
    chunks = []
    for idx in range(0, len(values), 18):
        chunks.append(item_indent + ", ".join(str(value) for value in values[idx : idx + 18]))
    return open_indent + "[\n" + ",\n".join(chunks) + "\n" + open_indent + "]"


def certificate_name(index: int) -> str:
    return f"cert{index}"


def render_certificate(index: int, row: dict[str, int], u: list[int], v: list[int]) -> str:
    name = certificate_name(index)
    return f"""def {name} : CollisionBezoutCertificate where
  scale₁ := {row["r"]}
  low₁ := {row["low1"]}
  total₁ := {row["n"]}
  scale₂ := {row["s"]}
  low₂ := {row["low2"]}
  total₂ := {row["m"]}
  u :=
{lean_nat_list(u)}
  v :=
{lean_nat_list(v)}
"""


def render(rows: list[dict[str, int]], witnesses: list[tuple[list[int], list[int]]]) -> str:
    cert_defs = "\n".join(
        render_certificate(index, row, u, v)
        for index, (row, (u, v)) in enumerate(zip(rows, witnesses, strict=True))
    )
    cert_names = [certificate_name(index) for index in range(len(rows))]
    cert_list = ", ".join(cert_names)
    check_theorems = "\n".join(
        f"""theorem {name}_checks : {name}.checks := by
  native_decide
"""
        for name in cert_names
    )
    combined_terms = ", ".join(f"{name}_checks" for name in cert_names)
    combined_props = " ∧\n      ".join(f"{name}.checks" for name in cert_names)
    return f"""import Qab.Certificates.CollisionBezout
import Qab.Certificates.ResidualZMod1009

set_option maxRecDepth 200000

namespace Qab

namespace Certificates.ResidualBezout1009

open Certificates.CollisionBezout
open Certificates.ResidualZMod1009

/-!
Generated semantic Bezout certificates for the residual `ZMod 1009` rows.

Source artifact:

* `data/qab12/one_nonunit_residual_modular_certificates.csv`

Regenerate with:

```bash
python3 Qab_Lean_v4/scripts/residual_bezout_to_lean.py
```
-/

{cert_defs}
def residualBezoutCertificates : List CollisionBezoutCertificate :=
  [{cert_list}]

def certificateMatchesRow
    (cert : CollisionBezoutCertificate) (row : ResidualCertificateRow) : Bool :=
  cert.scale₁ = row.r &&
    cert.low₁ = row.low1 &&
    cert.total₁ = row.n &&
    cert.scale₂ = row.s &&
    cert.low₂ = row.low2 &&
    cert.total₂ = row.m &&
    row.prime = ZModGcd.modulus &&
    row.gcdDegree = ZModGcd.forcedDoubleRootDegree

def residualBezoutRowsMatch : Bool :=
  residualBezoutCertificates.length = residualCertificateRows.length &&
    (residualBezoutCertificates.zip residualCertificateRows).all fun pair =>
      certificateMatchesRow pair.1 pair.2

theorem residualBezoutRowsMatch_eq_true : residualBezoutRowsMatch = true := by
  native_decide

{check_theorems}
theorem residualBezout1009CertificateSetChecks :
    {combined_props} ∧
      residualBezoutRowsMatch = true := by
  exact ⟨{combined_terms}, residualBezoutRowsMatch_eq_true⟩

end Certificates.ResidualBezout1009

end Qab
"""


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=repo_root / "data/qab12/one_nonunit_residual_modular_certificates.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repo_root / "Qab_Lean_v4/Qab/Certificates/ResidualBezout1009.lean",
    )
    args = parser.parse_args()

    rows = read_rows(args.input)
    witnesses: list[tuple[list[int], list[int]]] = []
    for index, row in enumerate(rows):
        if row["prime"] != MODULUS:
            raise ValueError(f"row {index}: expected prime {MODULUS}, got {row['prime']}")
        left = collision_poly(row["r"], row["low1"], row["n"])
        right = collision_poly(row["s"], row["low2"], row["m"])
        gcd, u, v = egcd(left, right)
        lhs = add(mul(u, left), mul(v, right))
        if gcd != FORCED_FACTOR:
            raise ValueError(f"row {index}: gcd is {gcd}, not {FORCED_FACTOR}")
        if lhs != FORCED_FACTOR:
            raise ValueError(f"row {index}: Bezout identity failed")
        if row["gcd_degree"] != 2:
            raise ValueError(f"row {index}: expected gcd degree 2, got {row['gcd_degree']}")
        witnesses.append((trim(u), trim(v)))

    args.output.write_text(render(rows, witnesses))
    print(f"wrote {args.output} ({len(rows)} certificates)")


if __name__ == "__main__":
    main()
