#!/usr/bin/env python3
"""Independent row verifier for the Qab12 both-nonunit package catalogue."""
from __future__ import annotations
import argparse,csv,math
from pathlib import Path

def fail(msg):raise RuntimeError(msg)
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
def val(n,p):
 k=0
 while n%p==0:n//=p;k+=1
 return k
def supp(n):return {p for p,k in fac(n)}
def defects(r,t):return {p for p,A in fac(r) if val(t,p)<A}

def check_endpoint(endpoint,other,e,r,t,coeff,sigmas):
 ef=dict(fac(endpoint)); cf=fac(coeff)
 if coeff<=1 or any(p not in ef or A>ef[p] for p,A in cf):fail('coefficient does not divide endpoint')
 if len(cf)>5:fail('too many coefficient primes')
 expected=[]; selected={p for p,A in cf}; D=defects(r,t)
 for p,kappa in fac(endpoint):
  if p not in selected:
   if p in D:fail('deficient endpoint prime omitted from coefficient')
   if e%p not in (0,(p-2)%p):fail('unit endpoint degree signature')
   continue
  A=val(coeff,p)
  if (r*A)%t:fail('norm-transfer exponent is nonintegral')
  lam=r*A//t
  if not(1<=lam<=kappa) or (other*lam)%kappa:fail('packet occupancy integrality')
  w=other*lam//kappa
  if not(1<=w<=min(other,e)):fail('packet occupancy range')
  if (e-w)%p not in (0,(p-2)%p):fail('packet residual signature')
  if p in D and (p>7 or kappa<p or (e*kappa)%(p*other)):fail('deficient endpoint condition')
  expected.append(t*w)
 got=list(sigmas[:len(expected)])
 if got!=expected or any(sigmas[len(expected):]):fail(f'slope signature mismatch {got=} {expected=}')

def check_row(z):
 U,V,d,r,t,e,a,b,n=[z[k] for k in ('U','V','d','r','t','e','a','b','n')]
 if not(U>1 and V>1 and math.gcd(U,V)==1):fail('coefficient condition')
 if not(1<=t<=r<=139 and d==t*e and d<=224):fail('degree/core condition')
 if a+b!=n or math.gcd(a,b)!=1 or min(a,b)<2:fail('primitive shape')
 if not(n>=e+4 and n>=d+2 and r*n<=16583 and r*n<19*d):fail('size condition')
 if a>14*e or b>14*e:fail('endpoint bound')
 if not supp(n)<=supp(e*(e+2)):fail('total radical signature')
 su=tuple(z[f'su{i}'] for i in range(1,6));sv=tuple(z[f'sv{i}'] for i in range(1,6))
 check_endpoint(a,b,e,r,t,U,su);check_endpoint(b,a,e,r,t,V,sv)
 D=defects(r,t)
 for p in D:
  if n%p==0:fail('deficient total prime')
  if a%p!=0 and b%p!=0:
   if e>p-2:fail('deficient good prime')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--packages',type=Path,required=True);ap.add_argument('--state-pairs',type=Path,required=True);a=ap.parse_args()
 rows=[];last=None;keys=set()
 with a.packages.open(newline='') as f:
  for i,row in enumerate(csv.DictReader(f),2):
   try:z={k:int(v) for k,v in row.items()}
   except Exception as exc:fail(f'noninteger row {i}: {exc}')
   check_row(z)
   canonical=tuple(z[k] for k in ['U','V','d']+[f'su{i}' for i in range(1,6)]+[f'sv{i}' for i in range(1,6)]+['r','t','e','n','a','b'])
   if last is not None and canonical<=last:fail(f'catalogue not strictly sorted at {i}')
   last=canonical
   key=tuple(z[k] for k in ['U','V','d']+[f'su{i}' for i in range(1,6)]+[f'sv{i}' for i in range(1,6)])
   if key in keys:fail(f'duplicate common-factor key at row {i}')
   keys.add(key);rows.append(z)
 with a.state_pairs.open(newline='') as f:
  rd=csv.DictReader(f);extra=next(rd,None)
  if extra is not None:fail('state-pair file is not empty')
 print(f'verified_two_nonunit_package_states={len(rows)}')
 print(f'verified_unique_common_factor_keys={len(keys)}')
 print('verified_two_nonunit_state_pairs=0')
 print('status=PASS')
if __name__=='__main__':main()
