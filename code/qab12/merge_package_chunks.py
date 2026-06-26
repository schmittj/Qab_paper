#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,glob,hashlib
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--U',type=int,required=True);ap.add_argument('--chunk-dir',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 fields=['U','d','sigma1','sigma2','sigma3','r','t','e','a','b','n']
 rows=set()
 files=sorted(a.chunk_dir.glob(f'U{a.U}_e*.csv'))
 if not files:raise SystemExit('no chunks')
 for p in files:
  with p.open(newline='') as f:
   rd=csv.DictReader(f)
   if rd.fieldnames!=fields:raise SystemExit(f'bad header {p}: {rd.fieldnames}')
   for row in rd:
    vals=tuple(int(row[k]) for k in fields)
    if vals[0]!=a.U:raise SystemExit(f'bad U in {p}')
    rows.add(vals)
 ordered=sorted(rows,key=lambda z:(z[0],z[1],z[2],z[3],z[4],z[5],z[6],z[7],z[10],z[8],z[9]))
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('w',newline='') as f:
  wr=csv.writer(f);wr.writerow(fields);wr.writerows(ordered)
 h=hashlib.sha256(a.output.read_bytes()).hexdigest()
 print(f'U={a.U} chunks={len(files)} package_states={len(ordered)} sha256={h}')
if __name__=='__main__':main()
