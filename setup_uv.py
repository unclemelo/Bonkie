#!/usr/bin/env python3
"""Script to set up uv environment with dev dependencies."""
import subprocess
import shutil
import os
import sys

os.chdir('c:\\Users\\melo\\Desktop\\Bonkie')

# Clean up corrupted venv directories
for venv_dir in ['.venv', '.venv_new']:
    if os.path.exists(venv_dir):
        try:
            shutil.rmtree(venv_dir)
            print(f"Removed {venv_dir}")
        except Exception as e:
            print(f"Failed to remove {venv_dir}: {e}")

# Run uv sync with all extras
uv_exe = r'C:\Users\melo\AppData\Roaming\Python\Python314\Scripts\uv.exe'
result = subprocess.run([uv_exe, 'sync', '--all-extras'], capture_output=False)
sys.exit(result.returncode)
