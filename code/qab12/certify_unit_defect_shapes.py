#!/usr/bin/env python3
"""Generate modular subset-degree irreducibility certificates for all
primitive shapes appearing in the Qab12 unit-defect residual table."""
from __future__ import annotations
import argparse, csv, json, math, time
from pathlib import Path
from flint import nmod_poly, ctx
ctx.threads = 1


def primes(limit: int = 1000):
    out=[]
    for n in range(2,limit+1):
        if all(n%p for p in out if p*p<=n): out.append(n)
    return out


def qab_poly(a:int,b:int,p:int)->nmod_poly:
    n=a+b
    coeff=[]
    for k in range(n-1):
        coeff.append((b*(k+1) if k<a else a*(n-k-1))%p)
    return nmod_poly(coeff,p)


def factor_degrees(a:int,b:int,p:int)->list[int]:
    f=qab_poly(a,b,p)
    if f.degree()!=a+b-2:
        raise ValueError('degree drop')
    unit, fs=f.factor()
    out=[]
    for q,m in fs: out.extend([q.degree()]*int(m))
    if sum(out)!=f.degree(): raise ValueError('factor degree sum mismatch')
    return sorted(out)


def subset_mask(degrees:list[int])->int:
    mask=1
    for d in degrees: mask |= mask<<d
    return mask


def set_bits(mask:int):
    out=[]
    while mask:
        bit=mask & -mask
        out.append(bit.bit_length()-1)
        mask-=bit
    return out


def read_shapes(path:Path):
    shapes=set()
    with path.open(newline='') as f:
        for row in csv.DictReader(f):
            shapes.add((int(row['a']),int(row['b'])))
            shapes.add((int(row['c']),int(row['f'])))
    return sorted(shapes,key=lambda z:(sum(z),z))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--prime-limit',type=int,default=1000)
    args=ap.parse_args()
    ps=primes(args.prime_limit)
    shapes=read_shapes(args.input)
    started=time.perf_counter(); total_factorings=0
    completed=set()
    if args.output.exists():
        with args.output.open() as prev:
            for line in prev:
                if line.strip():
                    obj=json.loads(line); completed.add((int(obj['a']),int(obj['b'])))
    mode='a' if completed else 'w'
    with args.output.open(mode) as out:
        for idx,(a,b) in enumerate(shapes):
            if (a,b) in completed:
                print(f'[{idx+1}/{len(shapes)}] shape={a},{b} already certified',flush=True)
                continue
            deg=a+b-2
            possible=(1<<(deg+1))-1
            steps=[]
            for p in ps:
                if a%p==0: continue
                ds=factor_degrees(a,b,p); total_factorings+=1
                possible &= subset_mask(ds)
                remain=set_bits(possible)
                steps.append({'prime':p,'factor_degrees':ds,'remaining_degrees':remain})
                if remain==[0,deg]: break
            remain=set_bits(possible)
            if remain!=[0,deg]:
                raise RuntimeError(f'unresolved shape {(a,b)} remaining={remain[:100]} count={len(remain)}')
            rec={'schema':'qab12-subset-degree-v1','a':a,'b':b,'degree':deg,'steps':steps,'final_degrees':remain}
            out.write(json.dumps(rec,separators=(',',':'),sort_keys=True)+'\n')
            print(f'[{idx+1}/{len(shapes)}] shape={a},{b} degree={deg} primes={len(steps)} last={steps[-1]["prime"]}',flush=True)
    print(f'target_shapes={len(shapes)} preexisting_shapes={len(completed)} new_modular_factorizations={total_factorings} elapsed_seconds={time.perf_counter()-started}')

if __name__=='__main__': main()
