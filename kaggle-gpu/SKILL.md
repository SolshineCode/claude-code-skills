# Kaggle GPU — Fully Headless GPU Kernel Execution

This skill is **fully autonomous and headless** — no browser, no MCP bridge, no hang risk. It submits Python scripts to Kaggle's GPU infrastructure via the `kaggle` CLI/SDK, polls for completion, and retrieves outputs. Zero human interaction required.

## Credentials & Setup (already done)

- **kaggle.json**: `C:\Users\caleb\.kaggle\kaggle.json`
- **Username**: `calebdeleeuw`
- **CLI invocation**: always use `python -m kaggle` (bare `kaggle` is not on PATH)
- **GPU quota**: ~30 GPU-hours/week (resets weekly), shared across T4/P100

## Workflow Overview

```
Write script → build kernel dir → push → poll status → download outputs → upload to HF
```

All steps are pure CLI/API — no Chrome automation needed.

---

## Step 1: Prepare the Kernel Directory

Create a local staging directory (e.g. `C:\Users\caleb\kaggle-runs\<run-name>\`):

```
C:\Users\caleb\kaggle-runs\<run-name>\
  script.py              # the training/eval script
  kernel-metadata.json   # kernel config
```

### kernel-metadata.json

```json
{
  "id": "calebdeleeuw/<slug>",
  "title": "<slug>",
  "code_file": "script.py",
  "language": "python",
  "kernel_type": "script",
  "is_private": true,
  "enable_gpu": true,
  "enable_internet": true,
  "dataset_sources": [],
  "competition_sources": [],
  "kernel_sources": []
}
```

**⚠ Title must equal slug exactly.** Kaggle derives a slug from the title and rejects the push if they don't match. Set `"title": "<slug>"` — the same value as the `id` suffix. Do NOT use spaces, em-dashes, or any character that would change the slug. (Verified failure 2026-06-18: title "BioRefusalAudit SAE v3 AuxK Continuation" with slug `biosae-auxk-cont-20260618` was rejected.)

**Slug rules:** lowercase, hyphens only, max 50 chars, must be globally unique under your username. Use pattern `<project>-<date>` e.g. `biosae-auxk-run2-20260618`.

**enable_internet: true** — required for HF Hub downloads (`huggingface-hub`, `transformers`, etc.).

**GPU type:** Kaggle assigns T4 or P100 automatically when `enable_gpu: true`. You cannot request a specific GPU type on the free tier. Check `nvidia-smi` in your script to log what was assigned.

---

## Step 2: Write the Script

**⚠ ALWAYS use the Write tool to create script.py — NEVER PowerShell `Set-Content` or `Out-File`.** PowerShell defaults to Windows-1252 encoding and mangles any non-ASCII characters (em-dashes, box-drawing chars, Unicode arrows) into `â€"` garbage. The Write tool writes clean UTF-8. Even if the script looks fine locally, Kaggle will run the mangled bytes and the script will print garbage or fail. (Verified failure 2026-06-18.)

**⚠ Keep scripts ASCII-only where possible.** Use `->` not `→`, `--` not `—`, plain hyphens not Unicode dashes. This survives any encoding pipeline without risk.

Key rules for Kaggle scripts (different from Colab):

- **Output directory is `/kaggle/working/`** — all files you want to retrieve must be written here. Files elsewhere are ephemeral.
- **No Drive mount** — use `/kaggle/working/` for persistence.
- **Install packages at top of script** with `subprocess.run(["pip", "install", "-q", ...])` or `os.system("pip install -q ...")` — the kernel environment is fresh each run.
- **HF token injection**: pass via environment variable. Set it in the script using `os.environ.get("HF_TOKEN")`, and inject it via the push helper (see Step 3).
- **Unbuffered output**: always use `python -u` semantics — set `PYTHONUNBUFFERED=1` at the top:
  ```python
  import os; os.environ["PYTHONUNBUFFERED"] = "1"
  ```
- **Checkpoint every N steps to /kaggle/working/** — if the kernel times out (9h limit), the last checkpoint survives in the output.
- **Upload to HF inside the training loop** if the run might exceed 9h — don't rely solely on the final output download.

### Script template skeleton

```python
import os, subprocess
os.environ["PYTHONUNBUFFERED"] = "1"

# Install deps
subprocess.run(["pip", "install", "-q", "huggingface_hub", "transformers", "bitsandbytes"], check=False)

import torch
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

HF_TOKEN = os.environ.get("HF_TOKEN", "")

# ... training code ...

# Save outputs to /kaggle/working/
torch.save(model.state_dict(), "/kaggle/working/checkpoint.pt")
print("DONE. Saved to /kaggle/working/")
```

---

## Step 3: Push the Kernel

Use the helper script `C:\Users\caleb\.claude\skills\kaggle-gpu\push_kernel.py` or run directly:

```powershell
# Set HF token as env var (injected into the kernel's environment secrets via API)
$env:HF_TOKEN = "hf_YOUR_TOKEN_HERE"

# Push — this QUEUES the run (returns immediately, does not block)
python -m kaggle kernels push -p "C:\Users\caleb\kaggle-runs\<run-name>"
```

**Important:** `kaggle kernels push` returns immediately after queuing. The run starts within ~1–5 minutes depending on GPU availability. Do NOT wait for it inline — proceed to Step 4.

### Injecting secrets (HF_TOKEN)

Kaggle kernels cannot read your local env vars. Pass secrets via the script itself (hardcode temporarily then remove, or use Kaggle's "Secrets" UI). The cleanest pattern: write the HF token into the script as a variable before pushing:

```python
# At top of script.py — replace placeholder at push time:
HF_TOKEN = "INJECT_HF_TOKEN"
```

Then in the push helper, sed-replace `INJECT_HF_TOKEN` with the real token before pushing. See `push_kernel.py` for this pattern.

---

## Step 4: Poll Status

Poll every 60–120 seconds (minimum). For runs expected to take 30+ min, set a CronCreate timer.

```powershell
python -m kaggle kernels status calebdeleeuw/<slug>
```

**Status values:**
- `queued` — waiting for GPU allocation (can take 1–10 min)
- `running` — executing
- `complete` — finished successfully ✓
- `error` — script raised an exception
- `cancelAcknowledged` — was cancelled

**Parse status in a loop:**

```powershell
while ($true) {
    $s = python -m kaggle kernels status calebdeleeuw/<slug> 2>&1
    Write-Host $s
    if ($s -match "complete|error|cancel") { break }
    Start-Sleep 60
}
```

For long runs (30+ min), use CronCreate with a reasonable estimate rather than polling every turn. Set the timer LATER not earlier (a late wake is cheaper than a premature one).

---

## Step 5: Download Outputs

```powershell
python -m kaggle kernels output calebdeleeuw/<slug> -p "C:\Users\caleb\kaggle-runs\<run-name>\output\"
```

This downloads all files from `/kaggle/working/` to the local output path. Typical outputs: checkpoints (`.pt`), logs (`.jsonl`), metrics (`.json`).

**After download:**
- Immediately upload checkpoints to HF Hub (use `hf_sizes.py` pattern or `huggingface_hub`)
- Commit metrics/logs to the relevant git repo
- Per the data mandate: "regeneratable from script" is NOT persistence — commit the actual files

---

## Step 6: Upload to HF Hub

```powershell
$env:HF_TOKEN = "hf_YOUR_TOKEN_HERE"
python -c "
from huggingface_hub import HfApi
import os
api = HfApi(token=os.environ['HF_TOKEN'])
api.upload_folder(folder_path='C:/Users/caleb/kaggle-runs/<run-name>/output', repo_id='Solshine/<repo-name>', repo_type='model')
print('Uploaded to HF')
"
```

---

## BioRefusalAudit AuxK Continuation — Ready-to-Run Config

For the immediate task (longer AuxK SAE training on gemma-4-E2B-it L17):

- **Slug**: `biosae-auxk-cont-<YYYYMMDD>`
- **Script**: loads checkpoint from `Solshine/gemma4-e2b-bio-sae-v2-auxk`, continues training 10k–30k steps, saves checkpoint every 1000 steps to `/kaggle/working/`, uploads to HF at the end
- **HF source checkpoint**: `Solshine/gemma4-e2b-bio-sae-v2-auxk` (public)
- **Output repo**: `Solshine/gemma4-e2b-bio-sae-v3-auxk` (create before pushing)

Use `push_kernel.py` to assemble and push this run.

---

## GPU Limits & Quotas

| Resource | Limit |
|---|---|
| Free GPU hours/week | ~30h (resets Sunday UTC) |
| Max session length | 9 hours |
| GPU type | T4 or P100 (auto-assigned) |
| VRAM | ~15 GB (T4) or ~16 GB (P100) |
| Internet access | Yes (when `enable_internet: true`) |
| Output storage | Files in `/kaggle/working/` survive; elsewhere ephemeral |

---

## GPU Compatibility: P100 (sm_60) vs T4 (sm_75+)

Kaggle auto-assigns T4 or P100. **Current PyTorch (2.x) does NOT support P100 (sm_60)** — it will warn and CUDA ops will fail. Detect and handle early:

```python
# At top of script, BEFORE importing torch:
import subprocess, sys

GPU_CAP = 99.0
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
                       capture_output=True, text=True, timeout=10)
    GPU_CAP = float(r.stdout.strip().split('\n')[0].strip())
    print(f"GPU compute capability: {GPU_CAP}")
except Exception as e:
    print(f"Could not detect GPU capability: {e}")

if GPU_CAP < 7.0:
    print("P100/sm_60: installing torch 2.0.1+cu117 for compatibility...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
        "torch==2.0.1+cu117", "torchvision==0.15.2+cu117",
        "--index-url", "https://download.pytorch.org/whl/cu117"], check=False)

# Now safe to import torch
import torch
```

After import, check again and skip NF4 4-bit quantization for P100 (bitsandbytes NF4 requires sm_75+):

```python
USE_QUANTIZATION = torch.cuda.is_available() and torch.cuda.get_device_properties(0).major >= 7

if USE_QUANTIZATION:
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL,
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16),
        device_map={"": 0}, token=HF_TOKEN)
else:
    # P100: load in float16 (2B model fits in 16GB without quant)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL,
        torch_dtype=torch.float16, device_map={"": 0}, token=HF_TOKEN)
```

**P100 training is slower** (~2-4x vs T4 NF4). For a 20k-step run, budget ~2x the wall-clock. Checkpoints every 1000 steps mean partial results survive even if 9h limit is hit.

---

## New/Bleeding-Edge Model Types (gemma4, etc.)

Kaggle's pre-installed `transformers` may be months behind. If you see:

```
ValueError: The checkpoint has model type `gemma4` but Transformers does not recognize this architecture.
```

Install from git at the top of your script:

```python
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "git+https://github.com/huggingface/transformers.git"], check=False)
```

This pulls the latest HEAD and takes ~60s. Required for any model added to HF Hub after the last transformers PyPI release.

---

## Error Recovery

| Symptom | Fix |
|---|---|
| `push` returns `404` or `403` | Slug conflicts with existing kernel; change the slug |
| Status stays `queued` > 15 min | GPU quota may be exhausted for the week; check kaggle.com |
| Status `error` | Download the output anyway (`kernels output`) — logs in `/kaggle/working/` often show the traceback |
| Output download empty | Script crashed before writing to `/kaggle/working/`; check logs |
| Auth failure | Re-run `Copy-Item "$env:USERPROFILE\Downloads\kaggle.json" "$env:USERPROFILE\.kaggle\kaggle.json"` |
| `ValueError: model type X not recognized` | Install transformers from git (see "New/Bleeding-Edge Model Types" above) |
| `CUDA capability sm_60 not compatible` + crash | Detect GPU cap before importing torch; install `torch==2.0.1+cu117` for P100 (see "GPU Compatibility" above) |
| PowerShell charmap error on `kernels output` | Run from Bash with `PYTHONUTF8=1 python -m kaggle kernels output ...` |

---

## Comparison vs Colab GPU Skill

| | Kaggle (this skill) | Colab (colab-gpu skill) |
|---|---|---|
| Browser needed | No | Yes |
| Hang risk | None | Yes (MCP connect) |
| Mid-run interaction | No (outputs on completion) | Yes |
| GPU quota | ~30h/week | ~4h/day |
| Max session | 9h | ~12h |
| Headless | **Fully** | Partially |
| Account gate | Not needed | Hard gate (caleb.deleeuw@gmail.com) |

Use Kaggle when Colab GPU quota is exhausted or for unattended overnight runs.
