#!/usr/bin/env python3
from __future__ import annotations
import csv,itertools,math,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EXE=ROOT/'build/qab12_enumerate_two_nonunit_packages'
FIELDS=['U','V','d','su1','su2','su3','su4','su5','sv1','sv2','sv3','sv4','sv5','r','t','e','a','b','n']

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
def deficient(r,t):return {p for p,A in fac(r) if val(t,p)<A}

def endpoint_choices(endpoint,other,e,r,t):
 fs=fac(endpoint);D=deficient(r,t);out=[]
 def rec(i,coeff,sigs):
  if i==len(fs):
   if coeff>1:out.append((coeff,tuple(sigs+[0]*(5-len(sigs)))))
   return
  p,kappa=fs[i]
  if p not in D and e%p in (0,(p-2)%p):rec(i+1,coeff,sigs)
  for lam in range(1,kappa+1):
   if (t*lam)%r:continue
   A=t*lam//r
   if not(1<=A<=kappa) or (other*lam)%kappa:continue
   w=other*lam//kappa
   if not(1<=w<=min(other,e)):continue
   if (e-w)%p not in (0,(p-2)%p):continue
   if p in D and (p>7 or kappa<p or (e*kappa)%(p*other)):continue
   rec(i+1,coeff*p**A,sigs+[t*w])
 rec(0,1,[])
 return set(out)

def brute(emin,emax,rmax):
 out=set()
 for e in range(emin,emax+1):
  allowed=supp(e)|supp(e+2)
  totals=[n for n in range(e+4,28*e+1) if supp(n)<=allowed]
  for r in range(1,rmax+1):
   for t in range(1,r+1):
    d=t*e
    if d>224:break
    Df=deficient(r,t)
    for n in totals:
     if n<d+2 or r*n>16583 or r*n>=19*d:continue
     for a in range(2,n-1):
      b=n-a
      if b<2 or a>14*e or b>14*e or math.gcd(a,b)!=1:continue
      ok=True
      for p in Df:
       if n%p==0:ok=False;break
       if a%p==0 or b%p==0:continue
       if e>p-2:ok=False;break
      if not ok:continue
      L=endpoint_choices(a,b,e,r,t);R=endpoint_choices(b,a,e,r,t)
      for (U,su),(V,sv) in itertools.product(L,R):
       if math.gcd(U,V)!=1:continue
       out.add((U,V,d,*su,*sv,r,t,e,a,b,n))
 return out

def read(path):
 with open(path,newline='') as f:return {tuple(int(row[k]) for k in FIELDS) for row in csv.DictReader(f)}

def main():
 for emin,emax,rmax in [(2,10,5),(11,18,4)]:
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'out.csv'
   subprocess.run([str(EXE),'--e-start',str(emin),'--e-end',str(emax),'--r-max',str(rmax),'--threads','2','--output',str(p),'--keep-known-irreducible'],check=True,capture_output=True,text=True)
   got=read(p);exp=brute(emin,emax,rmax)
   if got!=exp:raise RuntimeError(f'mismatch {emin}-{emax}: got={len(got)} exp={len(exp)} missing={list(exp-got)[:2]} extra={list(got-exp)[:2]}')
   print(f'e={emin}-{emax} rmax={rmax} states={len(got)} PASS')
 print('two_nonunit_small_oracle=PASS')
if __name__=='__main__':main()
