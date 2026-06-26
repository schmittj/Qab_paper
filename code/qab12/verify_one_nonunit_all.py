#!/usr/bin/env python3
"""Verifier/manifest builder for the Qab12 conservative one-nonunit run.

It checks that every U=2..26 has a package catalogue, pair-output log, and
empty terminal state-pair/orientation-pair CSV. It recomputes the aggregate
stage counts directly from the pair-output logs and hashes the package and
state-pair families.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from pathlib import Path

STAGES=[
 'package_records','groups','raw_state_pairs','after_coprime_scales','after_range',
 'after_extraction','after_disjoint','after_support','after_degree','after_role',
 'after_correspondence','unique_state_pairs','unique_orientation_pairs']
PAT=re.compile(r'package_records=(\d+) groups=(\d+) raw_state_pairs=(\d+) after_coprime_scales=(\d+) after_range=(\d+) after_extraction=(\d+) after_disjoint=(\d+) after_support=(\d+) after_degree=(\d+) after_role=(\d+) after_correspondence=(\d+) unique_state_pairs=(\d+) unique_orientation_pairs=(\d+)')

def sha_file(path:Path)->str:
 h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def csv_rows(path:Path)->int:
 with path.open(newline='') as f:
  return max(0, sum(1 for _ in f)-1)

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--data',type=Path,default=Path('data')); ap.add_argument('--json',type=Path); args=ap.parse_args()
 data=args.data
 aggregate={s:0 for s in STAGES}; per=[]
 fam_packages=hashlib.sha256(); fam_states=hashlib.sha256(); fam_logs=hashlib.sha256()
 for U in range(2,27):
  p=data/f'one_nonunit_all_packages_U{U}.csv'
  out=data/f'one_nonunit_all_pair_output_U{U}.txt'
  states=data/f'one_nonunit_all_state_pairs_U{U}.csv'
  orients=data/f'one_nonunit_all_orientation_pairs_U{U}.csv'
  for q in (p,out,states,orients):
   if not q.exists(): raise SystemExit(f'missing {q}')
  text=out.read_text()
  m=PAT.search(text)
  if not m: raise SystemExit(f'cannot parse {out}')
  vals=list(map(int,m.groups()))
  row={'U':U, **dict(zip(STAGES,vals)),
       'package_rows':csv_rows(p), 'state_pair_rows':csv_rows(states), 'orientation_pair_rows':csv_rows(orients),
       'package_sha256':sha_file(p), 'state_pair_sha256':sha_file(states), 'orientation_pair_sha256':sha_file(orients), 'log_sha256':sha_file(out)}
  if row['package_rows']!=row['package_records']: raise SystemExit(f'package row mismatch U={U}')
  if row['state_pair_rows'] or row['orientation_pair_rows'] or row['unique_state_pairs'] or row['unique_orientation_pairs']:
   raise SystemExit(f'terminal survivor in U={U}')
  for s,v in zip(STAGES,vals): aggregate[s]+=v
  for q,h in ((p,fam_packages),(states,fam_states),(orients,fam_states),(out,fam_logs)):
   h.update(q.name.encode()+b'\0'+q.read_bytes()+b'\0')
  per.append(row)
 manifest={
  'schema':'qab12-one-nonunit-all-v1',
  'range':{'U_min':2,'U_max':26},
  'aggregate':aggregate,
  'family_hashes':{
   'packages':fam_packages.hexdigest(),
   'terminal_state_and_orientation_pairs':fam_states.hexdigest(),
   'pair_output_logs':fam_logs.hexdigest(),
  },
  'per_U':per,
  'status':'PASS',
 }
 if args.json:
  args.json.parent.mkdir(parents=True,exist_ok=True)
  args.json.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print('verified_one_nonunit_package_states=',aggregate['package_records'],sep='')
 for name in STAGES:
  print(f'aggregate_{name}={aggregate[name]}')
 print('verified_one_nonunit_survivors=0')
 print('status=PASS')
 return 0
if __name__=='__main__': raise SystemExit(main())
