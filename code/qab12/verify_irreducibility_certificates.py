#!/usr/bin/env python3
"""Recompute every modular factorization in the Qab12 subset-degree
irreducibility certificates and verify complete residual-shape coverage."""
from __future__ import annotations
import argparse,concurrent.futures,csv,json,subprocess,sys
from pathlib import Path

def fail(msg): raise RuntimeError(msg)

def subset_mask(ds):
    m=1
    for d in ds:m|=m<<d
    return m

def state_shapes(path:Path):
    s=set()
    with path.open(newline='') as f:
        for r in csv.DictReader(f):
            s.add((int(r['a']),int(r['b'])))
            s.add((int(r['c']),int(r['f'])))
    return s

def verify_one(obj,worker:Path,timeout:float):
    if obj.get('schema')!='qab12-subset-degree-v1':fail('bad certificate schema')
    a,b,deg=int(obj['a']),int(obj['b']),int(obj['degree'])
    if deg!=a+b-2:fail(f'bad degree {(a,b)}')
    possible=(1<<(deg+1))-1
    for index,step in enumerate(obj['steps']):
        p=int(step['prime'])
        cp=subprocess.run([sys.executable,str(worker),'--a',str(a),'--b',str(b),'--prime',str(p)],capture_output=True,text=True,timeout=timeout)
        if cp.returncode!=0:fail(f'factor worker failed {(a,b,p)}: {cp.stderr[-500:]} {cp.stdout[-500:]}')
        got=json.loads(cp.stdout.strip().splitlines()[-1])
        ds=sorted(map(int,got['factor_degrees']))
        expected=sorted(map(int,step['factor_degrees']))
        if ds!=expected:fail(f'factor degree mismatch {(a,b,p)}')
        possible &= subset_mask(ds)
        rem=[i for i in range(deg+1) if (possible>>i)&1]
        if rem!=list(map(int,step['remaining_degrees'])):fail(f'subset trace mismatch {(a,b,p)}')
    final=[i for i in range(deg+1) if (possible>>i)&1]
    if final!=[0,deg] or final!=list(map(int,obj['final_degrees'])):fail(f'nonterminal certificate {(a,b)}: {final}')
    return a,b,len(obj['steps'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--states',type=Path,required=True);ap.add_argument('--certificates',type=Path,required=True);ap.add_argument('--worker',type=Path,default=Path(__file__).with_name('mod_factor_shape_worker.py'));ap.add_argument('--workers',type=int,default=4);ap.add_argument('--timeout',type=float,default=900);args=ap.parse_args()
    objs=[json.loads(l) for l in args.certificates.read_text().splitlines() if l.strip()]
    keys=[(int(o['a']),int(o['b'])) for o in objs]
    if len(keys)!=len(set(keys)):fail('duplicate shape certificate')
    needed=state_shapes(args.states)
    if set(keys)!=needed:fail(f'coverage mismatch missing={sorted(needed-set(keys))} extra={sorted(set(keys)-needed)}')
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        fs=[pool.submit(verify_one,o,args.worker,args.timeout) for o in objs]
        for f in concurrent.futures.as_completed(fs):
            z=f.result();results.append(z);print(f'verified_shape={z[0]},{z[1]} steps={z[2]}',flush=True)
    print(f'verified_shapes={len(results)}')
    print(f'verified_modular_factorizations={sum(z[2] for z in results)}')
    print('status=PASS')
if __name__=='__main__':main()
