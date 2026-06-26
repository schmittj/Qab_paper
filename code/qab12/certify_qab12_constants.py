#!/usr/bin/env python3
"""Exact rational interval certificates for the Qab12 one-nonunit constants.

The only transcendental operation is logarithm.  It is enclosed by the
positive atanh series with an explicit geometric tail.  Cube roots are
bracketed by rational numbers using integer arithmetic.
"""
from __future__ import annotations
from fractions import Fraction
import hashlib

D_MIN = 16_584
D_MAX = 6_816_241
D_CAP = [0,0,6816241,1230611,508652,286175,188395,136208,104733,84090,69701,59198,51249,45056,40115,36095,32767,29975,27601,25561,23792,22244,20880,19670,18589,17619,16743]
LINEAR = [0,0,48,27,20,17,15,13,12,11,11,10,10,9,9,9,8,8,8,8,8,8,7,7,7,7,7]
TERMS = 120
ROOT_DEN = 10**8
EXP_TERMS = 160

def integer_cuberoot(n: int) -> int:
    lo, hi = 0, 1
    while hi**3 <= n:
        hi *= 2
    while lo + 1 < hi:
        m = (lo + hi)//2
        if m**3 <= n: lo = m
        else: hi = m
    return lo

def cbrt_interval(n: int) -> tuple[Fraction,Fraction]:
    scaled = n * ROOT_DEN**3
    lo = integer_cuberoot(scaled)
    if lo**3 == scaled:
        q = Fraction(lo,ROOT_DEN)
        return q,q
    return Fraction(lo,ROOT_DEN), Fraction(lo+1,ROOT_DEN)

def reduced_log_interval(z: Fraction) -> tuple[Fraction,Fraction]:
    if not (1 <= z <= 2): raise ValueError(z)
    y=(z-1)/(z+1)
    total=sum(Fraction(2)*y**(2*j+1)/(2*j+1) for j in range(TERMS))
    tail=Fraction(2)*y**(2*TERMS+1)/((2*TERMS+1)*(1-y*y))
    return total,total+tail

def log_interval(x: Fraction) -> tuple[Fraction,Fraction]:
    if x <= 0: raise ValueError(x)
    q=x;k=0
    while q>=2:q/=2;k+=1
    while q<1:q*=2;k-=1
    l2lo,l2hi=reduced_log_interval(Fraction(2))
    qlo,qhi=reduced_log_interval(q)
    if k>=0:return k*l2lo+qlo,k*l2hi+qhi
    return k*l2hi+qlo,k*l2lo+qhi

def envelope_interval(D:int)->tuple[Fraction,Fraction]:
    llo,lhi=log_interval(Fraction(2*D))
    rlo,rhi=cbrt_interval(D)
    return Fraction(8)*llo/rhi, Fraction(8)*lhi/rlo

def exp_upper(x: Fraction) -> Fraction:
    term = Fraction(1)
    total = term
    for k in range(1, EXP_TERMS + 1):
        term *= x
        term /= k
        total += term
    next_term = term * x / (EXP_TERMS + 1)
    ratio = x / (EXP_TERMS + 2)
    if ratio >= 1:
        raise RuntimeError("exp tail bound not applicable")
    return total + next_term / (1 - ratio)

def support_cap_upper(D: int) -> Fraction:
    _, log_hi = log_interval(Fraction(2 * D))
    root_lo, root_hi = cbrt_interval(D)
    exponent_hi = Fraction(16) * log_hi / root_lo
    return Fraction(8) * root_hi * root_hi * exp_upper(exponent_hi)

def degree_upper(D:int)->int:
    lo,hi=0,200_000
    while lo<hi:
        m=(lo+hi+1)//2
        if m**3 < 64*D*D:lo=m
        else:hi=m-1
    return lo

def check_two_nonunit_constants() -> None:
    # theta_0 > 1324717/10^6 because x^3-x-1 is negative there.
    theta = Fraction(1324717, 10**6)
    if not theta**3 - theta - 1 < 0:
        raise RuntimeError("plastic lower bound failed")
    logtheta_lo, _ = log_interval(theta)
    # On every interval where floor(log_2 D) and floor(log_3 D) are
    # constant, D/log(2D) is increasing.  Check its left endpoint.
    points={16_584,D_MAX+1}
    for base in (2,3):
        q=1
        while q<=D_MAX:
            if q>=16_584: points.add(q)
            q*=base
    pts=sorted(points)
    for left,right in zip(pts,pts[1:]):
        if left>D_MAX: break
        _,den_hi=log_interval(Fraction(2*left))
        lower=Fraction(left)*logtheta_lo/(2*den_hi)
        upper=2*((left.bit_length()-1))*floor_log(left,3)
        if not lower >= upper:
            raise RuntimeError(f"two-nonunit cutoff failed at {left}: {lower} < {upper}")
    # At D=16583 the coarse lower bound is still below 224; this pins
    # the advertised transition for this comparison.
    _,den_hi=log_interval(Fraction(2*16_583))
    if Fraction(16_583)*logtheta_lo/(2*den_hi) >= 224:
        raise RuntimeError("two-nonunit transition sharpness check failed")
    # max(U,V)>=3 in the both-nonunit branch.  Hence D<19d.
    _,log2D_hi=log_interval(Fraction(2*16_583))
    log3_lo,_=log_interval(Fraction(3))
    if not Fraction(2)*log2D_hi/log3_lo < 19:
        raise RuntimeError("D<19d certificate failed")
    if not (2**14 <= 16_583 < 2**15):
        raise RuntimeError("endpoint valuation bound failed")

def floor_log(n:int,base:int)->int:
    k=0;q=1
    while q<=n//base:q*=base;k+=1
    return k

def main()->int:
    check_two_nonunit_constants()
    if not support_cap_upper(50_000) < 1_612_000:
        raise RuntimeError("unit-large support cap certificate failed")
    if not support_cap_upper(175_394_637) < 4_398_937:
        raise RuntimeError("global support cap certificate failed")
    rows=[]
    for U in range(2,27):
        cap=D_CAP[U]
        flo,_=envelope_interval(cap)
        _,fhi_next=envelope_interval(cap+1)
        lulo,luhi=log_interval(Fraction(U))
        if not flo>luhi:
            raise RuntimeError(f'lower transition sign failed U={U}')
        if U == 16 and cap + 1 == 32768:
            # 32768=32^3 and 2*32768=2^16, so F=8*16*log(2)/32=log(16).
            pass
        elif not fhi_next<lulo:
            raise RuntimeError(f'upper transition sign failed U={U}')
        # 2 log(2D)/log(U) is increasing in D, so the endpoint suffices.
        _,ln2D_hi=log_interval(Fraction(2*cap))
        if not Fraction(2)*ln2D_hi/lulo < LINEAR[U]:
            raise RuntimeError(f'linear factor failed U={U}')
        emax=degree_upper(cap)
        rows.append((U,cap,LINEAR[U],emax))
    print('two_nonunit_cutoff_max_D=16583')
    print('two_nonunit_degree_max=224')
    print('two_nonunit_linear_bound=D<19d')
    print('two_nonunit_endpoint_valuation_max=14')
    print('coefficient_transition_table=PASS')
    print('envelope_monotone_for_D>=11=calculus')
    print('unit_large_support_cap_D_ge_50000=1612000')
    print('global_support_cap_D_le_175394637=4398937')
    print('columns=U,D_cap,linear_D_over_d_bound,max_degree')
    for row in rows:print(','.join(map(str,row)))
    digest=hashlib.sha256(('\n'.join(','.join(map(str,r)) for r in rows)+'\n').encode()).hexdigest()
    print('table_sha256='+digest)
    return 0
if __name__=='__main__':raise SystemExit(main())
