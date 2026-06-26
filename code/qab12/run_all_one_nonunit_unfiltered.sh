#!/usr/bin/env bash
set -euo pipefail
cd "$(cd "$(dirname "$0")/../.." && pwd)"
mkdir -p data/one_nonunit_all_chunks
: > run_all_one_nonunit_unfiltered.log
maxes=(0 0 143799 45934 25488 17370 13145 10589 8887 7677 6774 6075 5518 5064 4687 4368 4095 3859 3653 3470 3308 3163 3033 2914 2806 2708 2617)
for U in $(seq 2 26); do
  max=${maxes[$U]}
  if [ "$U" -eq 2 ]; then step=500; else step=1000; fi
  echo "BEGIN U=$U max_e=$max $(date -u +%FT%TZ)" | tee -a run_all_one_nonunit_unfiltered.log
  files=()
  start=2
  while [ "$start" -le "$max" ]; do
    end=$((start+step-1)); [ "$end" -gt "$max" ] && end=$max
    f="data/one_nonunit_all_chunks/U${U}_e${start}_${end}.csv"
    files+=("$f")
    if [ ! -f "$f" ]; then
      echo "RUN U=$U e=$start-$end" | tee -a run_all_one_nonunit_unfiltered.log
      ./build/qab12_enumerate_one_nonunit_packages --U "$U" --e-start "$start" --e-end "$end" --threads 25 --keep-known-irreducible --output "$f" | tee -a run_all_one_nonunit_unfiltered.log
    fi
    start=$((end+1))
  done
  python3 code/merge_package_chunks.py --U "$U" --chunk-dir data/one_nonunit_all_chunks --output "data/one_nonunit_all_packages_U${U}.csv" | tee -a run_all_one_nonunit_unfiltered.log
  ./build/qab12_pair_one_nonunit --input "data/one_nonunit_all_packages_U${U}.csv" --output "data/one_nonunit_all_state_pairs_U${U}.csv" --pairs-output "data/one_nonunit_all_orientation_pairs_U${U}.csv" | tee "data/one_nonunit_all_pair_output_U${U}.txt" | tee -a run_all_one_nonunit_unfiltered.log
  echo "END U=$U $(date -u +%FT%TZ)" | tee -a run_all_one_nonunit_unfiltered.log
done
echo "ALL_DONE $(date -u +%FT%TZ)" | tee -a run_all_one_nonunit_unfiltered.log
