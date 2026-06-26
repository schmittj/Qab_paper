#!/usr/bin/env python3
from __future__ import annotations
import csv,itertools,math,subprocess,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ENUM=ROOT/'build/qab12_enumerate_one_nonunit_packages'
PAIR=ROOT/'build/qab12_pair_one_nonunit'
FIELDS=['U','d','sigma1','sigma2','sigma3','r','t','e','a','b','n']

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

def supp(n):return {p for p,_ in fac(n)}
def val(n,p):
 k=0
 while n%p==0:n//=p;k+=1
 return k

def degree_upper(D):
 return max(d for d in range(200) if d**3<64*D*D)

def cores(U,rmax):
 uf=fac(U);out=[]
 for r in range(1,rmax+1):
  rf=fac(r)
  for t in range(1,r+1):
   if any((r*k)%t for p,k in uf):continue
   lam=tuple(r*k//t for p,k in uf);good=[];end=[];ok=True
   for p,A in rf:
    if val(t,p)<A:
     if p in supp(U):
      if p>7:ok=False;break
      end.append(p)
     else:good.append(p)
   if ok:out.append((r,t,lam,tuple(good),tuple(end)))
 return out

def brute_packages(U,emin,emax,Dmin,Dcap,C,rmax):
 uf=fac(U);dcap=degree_upper(Dcap);out=set()
 for e in range(emin,emax+1):
  allowed=supp(U)|supp(e)|supp(e+2)
  for r,t,lams,good,end in cores(U,rmax):
   d=t*e
   if d>dcap or C*d<Dmin or any(e>q-2 for q in good):continue
   nlim=min(Dcap//r,C*d//r)
   if nlim<e+4:continue
   for n in range(e+4,nlim+1):
    for a in range(1,n):
     b=n-a
     if math.gcd(a,b)!=1:continue
     if not supp(a*b*n)<=allowed:continue
     kappas=[val(a,p) for p,k in uf]
     if any(k==0 for k in kappas):continue
     sig=[];ok=True
     for (p,_),lam,kap in zip(uf,lams,kappas):
      if lam>kap or (b*lam)%kap:ok=False;break
      w=b*lam//kap
      if not(1<=w<=min(b,e)):ok=False;break
      if (e-w)%p not in (0,(p-2)%p):ok=False;break
      sig.append(t*w)
     if not ok:continue
     if any(a%q==0 or b%q==0 or n%q==0 for q in good):continue
     for q in end:
      kap=val(a,q)
      if kap<q or (e*kap)%(q*b):ok=False;break
     if not ok:continue
     sig+=(3-len(sig))*[0]
     out.add((U,d,*sig,r,t,e,a,b,n))
 return out

def role_value(p,z):
 vals=[z[k] for k in ('a','b','n') if z[k]%p==0]
 assert len(vals)==1
 return vals[0]
def same_pkg(x,y):return sorted((x['r']*x['a'],x['r']*x['b']))==sorted((y['r']*y['a'],y['r']*y['b']))
def disjoint(x,y):return {x['r']*x[k] for k in ('a','b','n')}.isdisjoint({y['r']*y[k] for k in ('a','b','n')})
def corr(x,y):
 g0=math.gcd(x['r']*x['b'],y['r']*y['b']);g1=math.gcd(x['r']*x['a'],y['r']*y['a'])
 return (y['r']*y['b']//g0)*(x['r']*x['a']//g1)+(x['r']*x['b']//g0)*(y['r']*y['a']//g1)
def brute_pairs(rows,Dmin,Dcap,C):
 groups={}
 for z in rows:groups.setdefault((z['U'],z['d'],z['sigma1'],z['sigma2'],z['sigma3']),[]).append(z)
 out=set()
 for g in groups.values():
  for x,y in itertools.combinations(g,2):
   if math.gcd(x['r'],y['r'])!=1 or same_pkg(x,y):continue
   D=max(x['r']*x['n'],y['r']*y['n'])
   if D<Dmin or D>Dcap or D>=C*x['d']:continue
   if x['d']>x['e']*y['e'] or not disjoint(x,y):continue
   X=supp(x['a']*x['b']*x['n']);Y=supp(y['a']*y['b']*y['n']);CU=supp(x['U'])
   if any(p>=5 and p not in Y|CU and y['r']%p for p in X):continue
   if any(p>=5 and p not in X|CU and x['r']%p for p in Y):continue
   if x['d']**3>=64*D*D or x['d']>min(x['n'],y['n'])-2:continue
   rb=None
   for p in X|Y:
    if p in CU:continue
    if p in X and p in Y:v=math.gcd(x['r']*role_value(p,x),y['r']*role_value(p,y))
    elif p in X:v=x['r']*role_value(p,x)
    else:v=y['r']*role_value(p,y)
    rb=v if rb is None else min(rb,v)
   if rb is not None and x['d']>rb:continue
   cb=corr(x,y)
   if {x['a'],x['b']}=={y['a'],y['b']}:cb=min(cb,2*x['r']*y['r'])
   if x['d']>cb:continue
   A=(x['r'],x['t'],x['e'],x['a'],x['b'],x['n']);B=(y['r'],y['t'],y['e'],y['a'],y['b'],y['n'])
   if B<A:A,B=B,A
   out.add((x['U'],x['d'],x['sigma1'],x['sigma2'],x['sigma3'],*A,*B,D,cb,rb if rb is not None else 2**32-1))
 return out

def read_packages(path):
 with open(path,newline='') as f:return [{k:int(v) for k,v in row.items()} for row in csv.DictReader(f)]

def main():
 cases=[(2,2,14,1,90,100,5),(3,2,12,1,90,100,5),(6,2,10,1,90,100,5)]
 for U,emin,emax,Dmin,Dcap,C,rmax in cases:
  with tempfile.TemporaryDirectory() as td:
   td=Path(td);p=td/'p.csv';sp=td/'states.csv';op=td/'pairs.csv'
   subprocess.run([str(ENUM),'--U',str(U),'--e-start',str(emin),'--e-end',str(emax),'--threads','2','--output',str(p),'--D-min',str(Dmin),'--D-cap',str(Dcap),'--linear-factor',str(C),'--r-max',str(rmax),'--keep-known-irreducible'],check=True,capture_output=True,text=True)
   got={tuple(int(r[k]) for k in FIELDS) for r in read_packages(p)}
   exp=brute_packages(U,emin,emax,Dmin,Dcap,C,rmax)
   if got!=exp:raise RuntimeError(f'package mismatch U={U}: got={len(got)} exp={len(exp)} missing={list(exp-got)[:3]} extra={list(got-exp)[:3]}')
   subprocess.run([str(PAIR),'--input',str(p),'--output',str(sp),'--pairs-output',str(op),'--D-min',str(Dmin),'--D-cap',str(Dcap),'--linear-factor',str(C)],check=True,capture_output=True,text=True)
   rows=read_packages(p);expected=brute_pairs(rows,Dmin,Dcap,C)
   with open(sp,newline='') as f:
    gotp=set()
    for r in csv.DictReader(f):
     vals=tuple(int(r[k]) for k in ['U','d','sigma1','sigma2','sigma3','r','t','e1','a','b','n','s','u','e2','c','f','m','D','correspondence_bound','role_bound'])
     gotp.add(vals)
   if gotp!=expected:raise RuntimeError(f'pair mismatch U={U}: got={len(gotp)} exp={len(expected)}')
   print(f'U={U} package_states={len(got)} pair_states={len(gotp)} PASS')
 print('one_nonunit_small_oracle=PASS')
if __name__=='__main__':main()
