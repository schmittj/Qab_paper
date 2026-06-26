#!/usr/bin/env python3
"""Exact catalogue of endpoint primes that can support internal p-th powers
below the remaining normalized bound in Qab9.

The endpoint theorem requires v_p(endpoint) >= p, hence p^p <= D_LOWER.
"""
D_LOWER = 6_816_241

def primes_upto(n: int):
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[:2] = b"\x00\x00"
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            sieve[p*p:n+1:p] = b"\x00" * (((n-p*p)//p)+1)
    return [p for p in range(2, n+1) if sieve[p]]

allowed = [p for p in primes_upto(100) if p**p <= D_LOWER]
print("lower_endpoint_power_primes=" + ",".join(map(str, allowed)))
for p in allowed:
    kmax = 0
    power = 1
    while power * p <= D_LOWER:
        power *= p
        kmax += 1
    print(f"p={p} kappa_range={p}..{kmax} minimum_endpoint={p**p}")
assert allowed == [2, 3, 5, 7]
