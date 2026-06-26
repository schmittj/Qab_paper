#!/usr/bin/env python3
"""Independent verifier for Qab12 modular collision-gcd certificates.

The verifier does not trust the search driver's completed-task index.  It
reconstructs every selected collision trinomial over F_p and recomputes the
modular gcd.  Exactly four orientation certificates must occur for every
input package pair.
"""
from __future__ import annotations
import argparse,csv,math
from pathlib import Path
from flint import nmod_poly,ctx
ctx.threads=1

def fail(msg): raise RuntimeError(msg)

def make_poly(scale:int,low:int,total:int,p:int)->nmod_poly:
    f=nmod_poly([],p)
    f[scale*total]=low%p
    f[scale*low]=(-total)%p
    f[0]=(total-low)%p
    return f

def sparse_rem(scale:int,low:int,total:int,mod:nmod_poly,p:int)->nmod_poly:
    x=nmod_poly([0,1],p)
    return (low*x.pow_mod(scale*total,mod)-total*x.pow_mod(scale*low,mod)+(total-low))%mod

def gcd_degree(r,low1,n,s,low2,m,p):
    d1=r*n; d2=s*m
    # Dense FLINT gcd is substantially faster for the certificate degrees in
    # this bundle.  The sparse branch is retained for future very asymmetric
    # inputs.
    if max(d1,d2) < 2_000_000 or max(d1,d2) < 5*min(d1,d2):
        return make_poly(r,low1,n,p).gcd(make_poly(s,low2,m,p)).degree()
    if d1<=d2:
        f=make_poly(r,low1,n,p); g=sparse_rem(s,low2,m,f,p)
    else:
        f=make_poly(s,low2,m,p); g=sparse_rem(r,low1,n,f,p)
    return f.gcd(g).degree()

def read_pairs(path:Path):
    out=[]
    with path.open(newline='') as f:
        for row in csv.DictReader(f):
            key='d_endpoint' if 'd_endpoint' in row else 'f'
            out.append(tuple(int(row[k]) for k in ('r','a','b','n','s','c'))+(int(row[key]),int(row['m'])))
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pairs',type=Path,required=True);ap.add_argument('--certificates',type=Path,required=True);args=ap.parse_args()
    pairs=read_pairs(args.pairs); seen=set();count=0
    with args.certificates.open(newline='') as f:
        for line,row in enumerate(csv.DictReader(f),2):
            vals={k:int(row[k]) for k in ('pair_index','orientation','r','a','b','n','s','c','d_endpoint','m','low1','low2','prime','gcd_degree')}
            i,o=vals['pair_index'],vals['orientation']
            if not(0<=i<len(pairs) and 0<=o<4):fail(f'bad task index at line {line}')
            if (i,o) in seen:fail(f'duplicate task {(i,o)}')
            seen.add((i,o));pair=(vals['r'],vals['a'],vals['b'],vals['n'],vals['s'],vals['c'],vals['d_endpoint'],vals['m'])
            if pair!=pairs[i]:fail(f'pair mismatch at line {line}')
            r,a,b,n,s,c,d,m=pair
            if a+b!=n or c+d!=m:fail(f'additive triple mismatch at line {line}')
            low1=(a,b)[o//2];low2=(c,d)[o%2]
            if (low1,low2)!=(vals['low1'],vals['low2']):fail(f'orientation mismatch at line {line}')
            p=vals['prime']
            if p<=2 or any(x%p==0 for x in (r,a,b,n,s,c,d,m)):fail(f'bad reduction prime at line {line}')
            got=gcd_degree(r,low1,n,s,low2,m,p)
            if vals['gcd_degree']!=2 or got!=2:fail(f'gcd degree mismatch at line {line}: {got}')
            count+=1
    expected={(i,o) for i in range(len(pairs)) for o in range(4)}
    if seen!=expected:fail(f'certificate coverage mismatch: missing={sorted(expected-seen)} extra={sorted(seen-expected)}')
    print(f'verified_package_pairs={len(pairs)}')
    print(f'verified_orientation_certificates={count}')
    print('status=PASS')
if __name__=='__main__':main()
