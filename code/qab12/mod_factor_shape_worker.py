#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time,resource
from flint import nmod_poly,ctx
ctx.threads=1
ap=argparse.ArgumentParser();ap.add_argument('--a',type=int,required=True);ap.add_argument('--b',type=int,required=True);ap.add_argument('--prime',type=int,required=True);args=ap.parse_args()
a,b,p=args.a,args.b,args.prime;n=a+b
try:
 if a%p==0: raise ValueError('leading coefficient vanishes')
 coeff=[(b*(k+1) if k<a else a*(n-k-1))%p for k in range(n-1)]
 f=nmod_poly(coeff,p)
 t=time.perf_counter();unit,fac=f.factor();elapsed=time.perf_counter()-t
 ds=[]
 for q,m in fac:ds += [q.degree()]*int(m)
 print(json.dumps({'ok':True,'a':a,'b':b,'prime':p,'degree':n-2,'factor_degrees':sorted(ds),'elapsed':elapsed,'max_rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},separators=(',',':')))
except Exception as e:
 print(json.dumps({'ok':False,'error':f'{type(e).__name__}: {e}','a':a,'b':b,'prime':p}))
 raise SystemExit(1)
