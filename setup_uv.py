#!/usr/bin/env python3
"""Script to set up uv environment with dev dependencies."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

for venv_dir in [ROOT / ".venv", ROOT / ".venv_new"]:
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
        print(f"Removed {venv_dir}")

result = subprocess.run(["uv", "sync", "--all-extras"], cwd=ROOT)
sys.exit(result.returncode)
