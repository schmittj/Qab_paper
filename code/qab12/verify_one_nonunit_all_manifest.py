#!/usr/bin/env python3
"""Verify the Qab12 all-shapes one-nonunit manifest.

This is a proof-artifact consistency checker, not an independent mathematical
coverage proof.  It checks that the per-U CSV files and pair-sieve logs match
the manifest exactly and that every terminal state/orientation-pair file is
header-only.
"""
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
    text = path.read_text().strip()
    out: dict[str, int] = {}
    for part in text.split():
        if '=' in part:
            k, v = part.split('=', 1)
            out[k] = int(v)
    missing = [k for k in COUNTER_KEYS if k not in out]
    if missing:
        raise RuntimeError(f'{path}: missing counters {missing}')
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=Path('.'))
    ap.add_argument('--data-dir', type=Path, default=Path('data/qab12'))
    ap.add_argument('--manifest', type=Path, default=Path('data/qab12/one_nonunit_all_manifest.json'))
    args = ap.parse_args()
    root = args.root
    data = args.data_dir if args.data_dir.is_absolute() else root / args.data_dir
    manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('schema') != 'qab12-one-nonunit-all-v1':
        raise RuntimeError('bad manifest schema')
    aggregate = {k: 0 for k in COUNTER_KEYS}
    pkg_paths = []
    log_paths = []
    term_paths = []
    for row in manifest['per_U']:
        U = int(row['U'])
        pkg = data / f'one_nonunit_all_packages_U{U}.csv'
        st = data / f'one_nonunit_all_state_pairs_U{U}.csv'
        op = data / f'one_nonunit_all_orientation_pairs_U{U}.csv'
        log = data / f'one_nonunit_all_pair_output_U{U}.txt'
        for key, path in [('package_sha256', pkg), ('state_pair_sha256', st), ('orientation_pair_sha256', op), ('log_sha256', log)]:
            got = sha256(path)
            if got != row[key]:
                raise RuntimeError(f'U={U}: {key} mismatch {got} != {row[key]}')
        if count_rows(pkg) != row['package_rows'] or count_rows(pkg) != row['package_records']:
            raise RuntimeError(f'U={U}: package row count mismatch')
        if count_rows(st) != row['state_pair_rows'] or row['state_pair_rows'] != 0:
            raise RuntimeError(f'U={U}: state-pair file is not empty')
        if count_rows(op) != row['orientation_pair_rows'] or row['orientation_pair_rows'] != 0:
            raise RuntimeError(f'U={U}: orientation-pair file is not empty')
        counters = parse_log(log)
        for k in COUNTER_KEYS:
            if counters[k] != row[k]:
                raise RuntimeError(f'U={U}: counter {k} mismatch {counters[k]} != {row[k]}')
            aggregate[k] += counters[k]
        pkg_paths.append(pkg)
        log_paths.append(log)
        term_paths.extend([st, op])
    if aggregate != manifest['aggregate']:
        raise RuntimeError(f'aggregate mismatch {aggregate} != {manifest["aggregate"]}')
    family = manifest['family_hashes']
    def family_hash(paths):
        h = hashlib.sha256()
        for p in paths:
            h.update(p.name.encode() + b'\0' + p.read_bytes() + b'\0')
        return h.hexdigest()
    got_pkg = family_hash(pkg_paths)
    got_log = family_hash(log_paths)
    got_term = family_hash(term_paths)
    if got_pkg != family['packages']:
        raise RuntimeError('package family hash mismatch')
    if got_log != family['pair_output_logs']:
        raise RuntimeError('log family hash mismatch')
    if got_term != family['terminal_state_and_orientation_pairs']:
        raise RuntimeError('terminal family hash mismatch')
    print('one_nonunit_all_manifest=PASS')
    for k in COUNTER_KEYS:
        print(f'{k}={aggregate[k]}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
