#!/usr/bin/env python3
"""Independent row/count verifier for the Qab12 one-nonunit catalogues.

This script validates the arithmetic conditions implemented by
`enumerate_one_nonunit_packages.cpp` and checks that the pairing outputs for
U=2,...,26 have no surviving state pairs.  It is a row-and-count verifier,
not an independent production enumerator.
"""
from __future__ import annotations
import argparse,csv,math,re
from pathlib import Path

D_CAP={2:6816241,3:1230611,4:508652,5:286175,6:188395,7:136208,8:104733,9:84090,10:69701,11:59198,12:51249,13:45056,14:40115,15:36095,16:32767,17:29975,18:27601,19:25561,20:23792,21:22244,22:20880,23:19670,24:18589,25:17619,26:16743}
LINEAR={2:48,3:27,4:20,5:17,6:15,7:13,8:12,9:11,10:11,11:10,12:10,13:9,14:9,15:9,16:8,17:8,18:8,19:8,20:8,21:8,22:7,23:7,24:7,25:7,26:7}
FIELDS=['U','d','sigma1','sigma2','sigma3','r','t','e','a','b','n']
PAIR_FIELDS=['package_records','groups','raw_state_pairs','after_coprime_scales','after_range','after_extraction','after_disjoint','after_support','after_degree','after_role','after_correspondence','unique_state_pairs','unique_orientation_pairs']

def fail(msg:str)->None: raise RuntimeError(msg)

def fac(n:int):
    out=[];p=2
    while p*p<=n:
        if n%p==0:
            k=0
            while n%p==0:n//=p;k+=1
            out.append((p,k))
        p=3 if p==2 else p+2
    if n>1:out.append((n,1))
    return out

def val(n:int,p:int)->int:
    k=0
    while n%p==0:n//=p;k+=1
    return k

def supp(n:int)->set[int]: return {p for p,_ in fac(n)}

def degree_upper(D:int)->int:
    lo,hi=0,200000
    while lo<hi:
        m=(lo+hi+1)//2
        if m**3 < 64*D*D: lo=m
        else: hi=m-1
    return lo

def deficient(r:int,t:int)->set[int]: return {p for p,A in fac(r) if val(t,p)<A}

def check_row(row:dict[str,int], path:Path, line:int)->None:
    U,d,r,t,e,a,b,n=[row[k] for k in ('U','d','r','t','e','a','b','n')]
    if U not in D_CAP: fail(f'{path}:{line}: U outside certified range')
    if not(1<=t<=r<=139 and d==t*e): fail(f'{path}:{line}: extraction data')
    if not(2<=e<=degree_upper(D_CAP[U])): fail(f'{path}:{line}: primitive degree range')
    if not(a+b==n and math.gcd(a,b)==1 and a>=1 and b>=1): fail(f'{path}:{line}: primitive additive triple')
    if not(n>=e+4): fail(f'{path}:{line}: proper primitive-factor size')
    if not(r*n <= D_CAP[U] and r*n <= LINEAR[U]*d): fail(f'{path}:{line}: package D/coefficient envelope')
    if not supp(n) <= supp(e*(e+2)): fail(f'{path}:{line}: total radical signature')
    D=deficient(r,t); uf=fac(U)
    sigmas=[row['sigma1'],row['sigma2'],row['sigma3']]
    if len(uf)>3: fail(f'{path}:{line}: too many coefficient primes')
    for idx,(p,A) in enumerate(uf):
        if (r*A)%t: fail(f'{path}:{line}: norm-transfer integrality')
        lam=r*A//t
        kappa=val(a,p)
        if not(1<=lam<=kappa): fail(f'{path}:{line}: endpoint valuation packet')
        if (b*lam)%kappa: fail(f'{path}:{line}: packet occupancy integrality')
        w=b*lam//kappa
        if not(1<=w<=min(b,e)): fail(f'{path}:{line}: packet occupancy range')
        if (e-w)%p not in (0,(p-2)%p): fail(f'{path}:{line}: residual packet signature')
        if sigmas[idx] != t*w: fail(f'{path}:{line}: sigma mismatch')
        if p in D and (p>7 or kappa<p or (e*kappa)%(p*b)):
            fail(f'{path}:{line}: deficient endpoint condition')
    if any(sigmas[len(uf):]): fail(f'{path}:{line}: trailing sigma not zero')
    for q in D:
        if q in supp(U):
            continue
        if q in supp(a*b*n): fail(f'{path}:{line}: deficient unit endpoint/total prime not excluded')
        if e>q-2: fail(f'{path}:{line}: deficient good-prime degree bound')
    # All primitive-triple primes not in the nonunit coefficient support must
    # obey the usual factor-degree congruence.
    for p in supp(a*b*n)-supp(U):
        if e%p not in (0,(p-2)%p): fail(f'{path}:{line}: radical degree signature')

def parse_pair_output(path:Path)->dict[str,int]:
    text=path.read_text().strip()
    return {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',text)}

def count_csv(path:Path)->int:
    with path.open(newline='') as f:
        return sum(1 for _ in csv.DictReader(f))

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',type=Path,default=Path(__file__).resolve().parents[1]/'data');args=ap.parse_args()
    totals={k:0 for k in PAIR_FIELDS}; package_total=0
    for U in range(2,27):
        p=args.data_dir/f'one_nonunit_all_packages_U{U}.csv'
        if not p.exists(): fail(f'missing package file U={U}')
        with p.open(newline='') as f:
            rd=csv.DictReader(f)
            if rd.fieldnames!=FIELDS: fail(f'bad package header U={U}: {rd.fieldnames}')
            seen=set(); count=0
            for line,row in enumerate(rd,2):
                z={k:int(row[k]) for k in FIELDS}
                if z['U']!=U: fail(f'{p}:{line}: wrong U')
                check_row(z,p,line)
                key=tuple(z[k] for k in FIELDS)
                if key in seen: fail(f'{p}:{line}: duplicate package row')
                seen.add(key); count+=1
        package_total+=count
        sp=args.data_dir/f'one_nonunit_all_state_pairs_U{U}.csv'
        op=args.data_dir/f'one_nonunit_all_orientation_pairs_U{U}.csv'
        if count_csv(sp)!=0 or count_csv(op)!=0: fail(f'nonempty survivor file U={U}')
        po=parse_pair_output(args.data_dir/f'one_nonunit_all_pair_output_U{U}.txt')
        if po.get('package_records')!=count: fail(f'package count mismatch U={U}')
        for k in PAIR_FIELDS: totals[k]+=po.get(k,0)
        if po.get('unique_state_pairs') or po.get('unique_orientation_pairs') or po.get('after_role') or po.get('after_correspondence'):
            fail(f'nonzero post-role survivor U={U}: {po}')
    print(f'verified_one_nonunit_package_states={package_total}')
    for k in PAIR_FIELDS: print(f'aggregate_{k}={totals[k]}')
    print('verified_one_nonunit_survivors=0')
    print('status=PASS')
    return 0
if __name__=='__main__': raise SystemExit(main())
