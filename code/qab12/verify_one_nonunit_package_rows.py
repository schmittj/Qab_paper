#!/usr/bin/env python3
"""Arithmetic verifier for emitted one-nonunit package rows."""
from __future__ import annotations
import argparse,csv,math
from pathlib import Path
D_CAP=[0,0,6816241,1230611,508652,286175,188395,136208,104733,84090,69701,59198,51249,45056,40115,36095,32767,29975,27601,25561,23792,22244,20880,19670,18589,17619,16743]
LINEAR=[0,0,48,27,20,17,15,13,12,11,11,10,10,9,9,9,8,8,8,8,8,8,7,7,7,7,7]
FIELDS=['U','d','sigma1','sigma2','sigma3','r','t','e','a','b','n']
def fail(msg): raise RuntimeError(msg)
def fac(n):
 out=[];p=2
 while p*p<=n:
  if n%p==0:
   k=0
   while n%p==0:n//=p;k+=1
   out.append((p,k))
  p=3 if p==2 else p+2
 if n>1:out.append((n,1))
 return out
def supp(n): return {p for p,k in fac(n)}
def val(n,p):
 k=0
 while n%p==0:n//=p;k+=1
 return k
def degree_upper(D):
 lo,hi=0,200000
 while lo<hi:
  m=(lo+hi+1)//2
  if m**3<64*D*D: lo=m
  else: hi=m-1
 return lo
def defects(r,t): return {p for p,A in fac(r) if val(t,p)<A}
def check(z,line):
 U,d,s1,s2,s3,r,t,e,a,b,n=[z[k] for k in FIELDS]
 if not (2<=U<=26): fail(f'bad U line {line}')
 if a+b!=n or math.gcd(a,b)!=1: fail(f'bad shape line {line}')
 if not (1<=t<=r<=139 and e>=2 and d==t*e and n>=e+4): fail(f'bad core line {line}')
 if d>degree_upper(D_CAP[U]) or LINEAR[U]*d<16584 or r*n>D_CAP[U] or r*n>LINEAR[U]*d: fail(f'bad size line {line}')
 if not supp(a*b*n) <= (supp(U)|supp(e)|supp(e+2)): fail(f'bad support line {line}')
 sig=[s1,s2,s3]; uf=fac(U); Df=defects(r,t)
 for i,(p,A) in enumerate(uf):
  if (r*A)%t: fail(f'norm integrality line {line}')
  lam=r*A//t; kap=val(a,p)
  if not(1<=lam<=kap): fail(f'endpoint exponent line {line}')
  if (b*lam)%kap: fail(f'occupancy integrality line {line}')
  w=b*lam//kap
  if not(1<=w<=min(b,e)): fail(f'occupancy range line {line}')
  if (e-w)%p not in (0,(p-2)%p): fail(f'residual signature line {line}')
  if sig[i]!=t*w: fail(f'sigma line {line}')
  if p in Df and (p>7 or kap<p or (e*kap)%(p*b)): fail(f'deficient endpoint line {line}')
 for i in range(len(uf),3):
  if sig[i]: fail(f'extra sigma line {line}')
 for p in Df:
  if p in supp(U): continue
  if a%p==0 or b%p==0 or n%p==0 or e>p-2: fail(f'deficient good line {line}')

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--data',type=Path,default=Path('data')); args=ap.parse_args(); total=0
 for U in range(2,27):
  path=args.data/f'one_nonunit_all_packages_U{U}.csv'; seen=set(); rows=0
  with path.open(newline='') as f:
   rd=csv.DictReader(f)
   if rd.fieldnames!=FIELDS: fail(f'bad header U={U}')
   for line,row in enumerate(rd,2):
    z={k:int(row[k]) for k in FIELDS}
    if z['U']!=U: fail(f'wrong U line {line}')
    key=tuple(z[k] for k in FIELDS)
    if key in seen: fail(f'duplicate row U={U} line {line}')
    seen.add(key); check(z,line); rows+=1
  total+=rows; print(f'one_nonunit_U={U} verified_package_rows={rows}')
 print(f'verified_one_nonunit_package_rows={total}')
 print('status=PASS')
if __name__=='__main__': main()
