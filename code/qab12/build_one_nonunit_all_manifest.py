#!/usr/bin/env python3
"""Build the Qab12 all-shapes one-nonunit manifest from the CSV/log files."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

COUNTER_KEYS = [
    'package_records','groups','raw_state_pairs','after_coprime_scales',
    'after_range','after_extraction','after_disjoint','after_support',
    'after_degree','after_role','after_correspondence','unique_state_pairs',
    'unique_orientation_pairs'
]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def count_rows(path: Path) -> int:
    with path.open(newline='') as f:
        return max(0, sum(1 for _ in f) - 1)

def parse_log(path: Path) -> dict[str, int]:
    out = {}
    for part in path.read_text().strip().split():
        if '=' in part:
            k, v = part.split('=', 1)
            out[k] = int(v)
    missing = [k for k in COUNTER_KEYS if k not in out]
    if missing:
        raise RuntimeError(f'{path}: missing {missing}')
    return out

def file_family_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in paths:
        h.update(p.name.encode() + b'\0' + p.read_bytes() + b'\0')
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=Path('.'))
    ap.add_argument('--data-dir', type=Path, default=Path('data/qab12'))
    ap.add_argument('--output', type=Path, default=Path('data/qab12/one_nonunit_all_manifest.json'))
    args = ap.parse_args()
    root = args.root
    data = args.data_dir if args.data_dir.is_absolute() else root / args.data_dir
    aggregate = {k: 0 for k in COUNTER_KEYS}
    per = []
    pkg_paths = []
    log_paths = []
    term_paths = []
    for U in range(2, 27):
        pkg = data / f'one_nonunit_all_packages_U{U}.csv'
        st = data / f'one_nonunit_all_state_pairs_U{U}.csv'
        op = data / f'one_nonunit_all_orientation_pairs_U{U}.csv'
        log = data / f'one_nonunit_all_pair_output_U{U}.txt'
        counters = parse_log(log)
        for k in COUNTER_KEYS:
            aggregate[k] += counters[k]
        row = {'U': U, **counters}
        row.update({
            'package_rows': count_rows(pkg),
            'state_pair_rows': count_rows(st),
            'orientation_pair_rows': count_rows(op),
            'package_sha256': sha256(pkg),
            'state_pair_sha256': sha256(st),
            'orientation_pair_sha256': sha256(op),
            'log_sha256': sha256(log),
        })
        per.append(row)
        pkg_paths.append(pkg); log_paths.append(log); term_paths.extend([st, op])
    manifest = {
        'schema': 'qab12-one-nonunit-all-v1',
        'status': 'PASS',
        'range': {'U_min': 2, 'U_max': 26},
        'aggregate': aggregate,
        'family_hashes': {
            'packages': file_family_hash(pkg_paths),
            'pair_output_logs': file_family_hash(log_paths),
            'terminal_state_and_orientation_pairs': file_family_hash(term_paths),
        },
        'per_U': per,
    }
    out = args.output if args.output.is_absolute() else root / args.output
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(f'wrote {out}')
    print('aggregate_unique_state_pairs=' + str(aggregate['unique_state_pairs']))
    print('aggregate_unique_orientation_pairs=' + str(aggregate['unique_orientation_pairs']))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
