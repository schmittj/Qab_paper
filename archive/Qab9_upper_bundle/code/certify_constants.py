#!/usr/bin/env python3
"""Exact rational certificates used by the upper-range search.

The assertions use only integer and Fraction arithmetic.  In particular, no
floating-point value is trusted by the search.  The script certifies:

* theta_0^70 > 2 D_MAX for the real root theta_0 of X^3-X-1;
* the uniform consequences d>D/140 and r,s<=139;
* monotonicity of the one-package support envelope on the unit range;
* its endpoint value is <4,398,937 by rational log/exp series bounds;
* d>D_UNIT/140 exceeds the maximal same-shape Bezout bound 2*139*138.
"""

from __future__ import annotations

from fractions import Fraction

D_MAX = 175_394_637
D_UNIT = 6_816_242
SCALE_MAX = 139
SUPPORT_PRODUCT_CAP = 4_398_937


def factorial(n: int) -> int:
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


def power_mod_plastic(n: int) -> tuple[int, int, int]:
    """Return c0,c1,c2 with X^n=c0+c1 X+c2 X^2 modulo X^3-X-1."""
    c0, c1, c2 = 1, 0, 0
    for _ in range(n):
        c0, c1, c2 = c2, c0 + c2, c1
    return c0, c1, c2


def log_interval(x: Fraction, terms: int = 50) -> tuple[Fraction, Fraction]:
    """Rigorous interval for log(x), using the atanh series after base-2 reduction."""
    if x <= 0:
        raise ValueError("log requires x>0")
    q = x
    k = 0
    while q >= 2:
        q /= 2
        k += 1
    while q < 1:
        q *= 2
        k -= 1

    def reduced_interval(z: Fraction) -> tuple[Fraction, Fraction]:
        y = (z - 1) / (z + 1)
        total = sum(
            Fraction(2) * y ** (2 * n + 1) / (2 * n + 1)
            for n in range(terms)
        )
        tail = (
            Fraction(2)
            * y ** (2 * terms + 1)
            / ((2 * terms + 1) * (1 - y * y))
        )
        return total, total + tail

    l2_lo, l2_hi = reduced_interval(Fraction(2))
    q_lo, q_hi = reduced_interval(q)
    if k >= 0:
        return k * l2_lo + q_lo, k * l2_hi + q_hi
    return k * l2_hi + q_lo, k * l2_lo + q_hi


def exp_upper(x: Fraction, terms: int = 50) -> Fraction:
    """Rigorous upper bound for exp(x), for the small positive x used here."""
    if x < 0:
        raise ValueError("this helper expects x>=0")
    term = Fraction(1)
    total = term
    for n in range(1, terms + 1):
        term *= x / n
        total += term
    first_omitted = term * x / (terms + 1)
    ratio_bound = x / (terms + 2)
    if ratio_bound >= 1:
        raise ValueError("increase the number of terms")
    return total + first_omitted / (1 - ratio_bound)


def main() -> int:
    # f(x)=x^3-x-1 is strictly increasing for x>=1.  Since f(33/25)<0,
    # theta_0>33/25.  Reduction modulo f gives an exact expression for
    # theta_0^70 with positive coefficients.
    t = Fraction(33, 25)
    assert t**3 - t - 1 < 0
    c0, c1, c2 = power_mod_plastic(70)
    theta70_lower = c0 + c1 * t + c2 * t * t
    assert theta70_lower > 2 * D_MAX

    # Hence log(theta_0)/(2 log(2D))>1/140 throughout D<=D_MAX.
    same_shape_max = 2 * SCALE_MAX * (SCALE_MAX - 1)
    degree_integer_min = D_UNIT // 140 + 1
    assert degree_integer_min > same_shape_max

    # The support envelope is
    # C(D)=8 D^(2/3) exp(16 log(2D)/D^(1/3)).
    # Put x=D^(1/3).  On the unit interval 189<x<560 and log(2D)<20.
    assert 189**3 < D_UNIT
    assert D_MAX < 560**3
    e_partial = sum(Fraction(1, factorial(k)) for k in range(6))
    assert e_partial > Fraction(27, 10)
    assert Fraction(27, 10) ** 20 > 2 * D_MAX  # therefore log(2D)<20
    # d/dx log C = (2x+48-16 log(2x^3))/x^2 >0.
    assert 2 * 189 + 48 - 16 * 20 > 0

    # Tight rational cube-root bracket at D_MAX.
    x_lo = Fraction(559_764_608, 1_000_000)
    x_hi = Fraction(559_764_609, 1_000_000)
    assert x_lo**3 < D_MAX < x_hi**3
    _, log_hi = log_interval(Fraction(2 * D_MAX))
    exponent_hi = 16 * log_hi / x_lo
    envelope_hi = 8 * x_hi * x_hi * exp_upper(exponent_hi)
    assert envelope_hi < SUPPORT_PRODUCT_CAP

    print(f"plastic_power_coefficients={c0},{c1},{c2}")
    print(f"theta70_rational_lower={theta70_lower}")
    print(f"twice_D_max={2 * D_MAX}")
    print("uniform_degree_bound=d>D/140")
    print(f"scale_max={SCALE_MAX}")
    print(f"same_shape_max={same_shape_max}")
    print(f"unit_degree_integer_min={degree_integer_min}")
    print(f"support_endpoint_upper_floor={envelope_hi.numerator // envelope_hi.denominator}")
    print(f"support_product_cap={SUPPORT_PRODUCT_CAP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
