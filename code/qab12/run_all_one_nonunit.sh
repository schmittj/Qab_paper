#!/usr/bin/env bash
set -euo pipefail
cd "$(cd "$(dirname "$0")/../.." && pwd)"
exec bash code/qab12/run_all_one_nonunit_unfiltered.sh "$@"
