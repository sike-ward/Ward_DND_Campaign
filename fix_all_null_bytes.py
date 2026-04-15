"""
Run once to remove null bytes from ALL Python files in the project.
This fixes the encoding corruption that causes 'source code string cannot
contain null bytes' errors on Windows.

Usage:
    python fix_all_null_bytes.py
"""

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
cleaned = []
failed = []
already_clean = 0

print("Scanning all Python files for null bytes...")

for p in PROJECT_ROOT.rglob("*.py"):
    # Skip .venv
    if ".venv" in p.parts:
        continue
    data = p.read_bytes()
    if b"\x00" not in data:
        already_clean += 1
        continue
    clean = data.replace(b"\x00", b"")
    try:
        ast.parse(clean)
        p.write_bytes(clean)
        cleaned.append(str(p.relative_to(PROJECT_ROOT)))
    except SyntaxError as e:
        failed.append((str(p.relative_to(PROJECT_ROOT)), str(e)))

print("\nResults:")
print(f"  Already clean : {already_clean} files")
print(f"  Cleaned       : {len(cleaned)} files")
print(f"  Failed        : {len(failed)} files")

if cleaned:
    print("\nCleaned files:")
    for f in cleaned:
        print(f"  {f}")

if failed:
    print("\nFailed files (need manual review):")
    for f, e in failed:
        print(f"  {f}: {e}")

if not failed:
    print("\nAll files are now null-byte free. You can delete this script.")
