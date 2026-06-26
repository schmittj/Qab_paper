#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EXE=$ROOT/build/enumerate_one_nonunit_packages
CHUNKDIR=$ROOT/data/one_nonunit_chunks
mkdir -p "$CHUNKDIR"
# exact degree caps corresponding to coefficient-specific D caps
E_MAX=(0 0 143799 45934 25488 17370 13145 10589 8887 7677 6774 6075 5518 5064 4687 4368 4095 3859 3653 3470 3308 3163 3033 2914 2806 2708 2617)
for U in $(seq 2 26); do
  max=${E_MAX[$U]}
  if [[ $U -eq 2 ]]; then chunk=500; else chunk=1000; fi
  echo "BEGIN U=$U max_e=$max $(date -u +%FT%TZ)"
  lo=2
  while [[ $lo -le $max ]]; do
    hi=$((lo+chunk-1)); [[ $hi -gt $max ]] && hi=$max
    out="$CHUNKDIR/U${U}_e${lo}_${hi}.csv"
    if [[ ! -s $out ]]; then
      echo "RUN U=$U e=$lo-$hi"
      timeout --kill-after=10s 600s "$EXE" --U "$U" --e-start "$lo" --e-end "$hi" --threads 25 --output "$out"
    fi
    lo=$((hi+1))
  done
  python3 "$ROOT/code/merge_package_chunks.py" --U "$U" --chunk-dir "$CHUNKDIR" --output "$ROOT/data/one_nonunit_packages_U${U}.csv"
  echo "END U=$U $(date -u +%FT%TZ)"
done
echo "ALL_DONE $(date -u +%FT%TZ)"
