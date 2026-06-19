"""
Kaggle GPU push helper — assembles kernel dir and submits to Kaggle.
Usage: python push_kernel.py --slug <slug> --script <path/to/script.py> [--title "My Run"]
"""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

HF_TOKEN = os.environ.get("HF_TOKEN", "")
KAGGLE_USER = "calebdeleeuw"
RUNS_DIR = Path(r"C:\Users\caleb\kaggle-runs")

parser = argparse.ArgumentParser()
parser.add_argument("--slug", required=True, help="Kernel slug (lowercase, hyphens only, max 50 chars)")
parser.add_argument("--script", required=True, help="Path to the Python script to run")
args = parser.parse_args()

slug = args.slug.lower().replace(" ", "-")[:50]
# Title MUST equal slug — Kaggle rejects push if they don't match (verified 2026-06-18)
title = slug
script_path = Path(args.script)

# Build staging dir
stage = RUNS_DIR / slug
stage.mkdir(parents=True, exist_ok=True)

# Copy and patch script — inject HF token
script_text = script_path.read_text(encoding="utf-8")
if HF_TOKEN:
    script_text = script_text.replace("INJECT_HF_TOKEN", HF_TOKEN)
# Warn on non-ASCII — Kaggle pipelines can mangle Unicode (use Write tool, not PowerShell, to author scripts)
non_ascii = [(i+1, c) for i, c in enumerate(script_text) if ord(c) > 127]
if non_ascii:
    print(f"WARNING: script contains {len(non_ascii)} non-ASCII chars (first: line ~{non_ascii[0][0]}, char '{non_ascii[0][1]}')")
    print("  Use ASCII-only in scripts to avoid Windows charset mangling. Proceeding anyway.")
(stage / "script.py").write_text(script_text, encoding="utf-8")

# Write kernel-metadata.json
meta = {
    "id": f"{KAGGLE_USER}/{slug}",
    "title": title,
    "code_file": "script.py",
    "language": "python",
    "kernel_type": "script",
    "is_private": True,
    "enable_gpu": True,
    "enable_internet": True,
    "dataset_sources": [],
    "competition_sources": [],
    "kernel_sources": []
}
(stage / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

print(f"Staging dir: {stage}")
print(f"Kernel ID:   {KAGGLE_USER}/{slug}")

# Push
result = subprocess.run(
    [sys.executable, "-m", "kaggle", "kernels", "push", "-p", str(stage)],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr, file=sys.stderr)
    sys.exit(result.returncode)

print(f"\nQueued. Poll with:")
print(f"  python -m kaggle kernels status {KAGGLE_USER}/{slug}")
print(f"\nDownload outputs when complete:")
print(f"  python -m kaggle kernels output {KAGGLE_USER}/{slug} -p {stage / 'output'}")
