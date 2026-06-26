#!/usr/bin/env python3
"""Run archived Qab9 upper verifier while refusing optimized Python."""
from __future__ import annotations
import os, runpy, sys
from pathlib import Path
if not __debug__ or sys.flags.optimize:
    raise SystemExit("refusing to run: Python assertions are disabled")
root = Path(__file__).resolve().parents[2]
upper = root / "archive" / "Qab9_upper_bundle"
os.chdir(upper)
runpy.run_path(str(upper / "code" / "verify_upper.py"), run_name="__main__")
