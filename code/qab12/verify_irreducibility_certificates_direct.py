#!/usr/bin/env python3
"""Single-process exact verifier for Qab12 modular irreducibility certificates."""
from __future__ import annotations
import argparse,csv,json,time
from pathlib import Path
from flint import nmod_poly,ctx
ctx.threads=1

def fail(msg): raise RuntimeError(msg)
def subset_mask(ds):
 m=1
 for d in ds:m|=m<<d
 return m
def qpoly(a,b,p):
 n=a+b
 return nmod_poly([(b*(k+1) if k<a else a*(n-k-1))%p for k in range(n-1)],p)
def degrees(a,b,p):
 f=qpoly(a,b,p)
 if f.degree()!=a+b-2:fail('degree drop')
 _,fs=f.factor();out=[]
 for q,m in fs:out.extend([q.degree()]*int(m))
 return sorted(out)
def shapes(path):
 out=set()
 with path.open(newline='') as f:
  for r in csv.DictReader(f):out.add((int(r['a']),int(r['b'])));out.add((int(r['c']),int(r['f'])))
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--states',type=Path,required=True);ap.add_argument('--certificates',type=Path,required=True);args=ap.parse_args()
 objs=[json.loads(l) for l in args.certificates.read_text().splitlines() if l.strip()];keys={(int(o['a']),int(o['b'])) for o in objs}
 if len(keys)!=len(objs) or keys!=shapes(args.states):fail('coverage mismatch')
 total=0;t0=time.perf_counter()
 for idx,o in enumerate(objs,1):
  a,b,deg=int(o['a']),int(o['b']),int(o['degree']);possible=(1<<(deg+1))-1
  for s in o['steps']:
   p=int(s['prime']);got=degrees(a,b,p);exp=sorted(map(int,s['factor_degrees']))
   if got!=exp:fail(f'factor degrees {(a,b,p)}')
   possible &= subset_mask(got);rem=[i for i in range(deg+1) if (possible>>i)&1]
   if rem!=list(map(int,s['remaining_degrees'])):fail(f'trace {(a,b,p)}')
   total+=1
  final=[i for i in range(deg+1) if (possible>>i)&1]
  if final!=[0,deg] or final!=list(map(int,o['final_degrees'])):fail(f'final {(a,b)}')
  print(f'[{idx}/{len(objs)}] verified_shape={a},{b} steps={len(o["steps"])}',flush=True)
 print(f'verified_shapes={len(objs)}')
 print(f'verified_modular_factorizations={total}')
 print(f'elapsed_seconds={time.perf_counter()-t0}')
 print('status=PASS')
if __name__=='__main__':main()
