---
name: gpu-grant
description: Use this skill when the user grants Claude a block of GPU time (e.g., "you have the next 8 hours of GPU time") and wants Claude to keep the GPU running useful work continuously until a timer fires. Handles timer setup, job chaining, GPU health monitoring, and graceful shutdown. Designed for AI/ML research workloads on local consumer-grade GPUs (4–16 GB VRAM).
---

# GPU Grant: Continuous Autonomous GPU Session

**This skill builds on and triggers the `/deep-work` autonomous execution framework.** At the start of every GPU grant session, load the deep-work skill and follow its full Phase 0–5 protocol (understand → plan → research → execute → verify → deliver) for the research work itself. The GPU grant skill adds on top of deep-work: the timer setup, job chaining, GPU health monitoring, and graceful shutdown that deep-work doesn't cover.

**Core principle from deep-work applies here:** never ask the user a question; make reasonable decisions and keep moving. The user has handed off the session.

You have been granted a block of GPU time. Your job is to keep the GPU doing useful research work every minute until the session timer fires, then gracefully wind down.

## Phase 0: Session Setup (Do First)

1. **Check current time**: Run `date` — do the math explicitly: "Current: X:XX, target: Y:YY, timer cron: MM HH DOM M *"
2. **Check GPU health**: `nvidia-smi --query-gpu=name,memory.used,memory.free,temperature.gpu --format=csv,noheader`
3. **Verify CUDA works**: `python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"`
4. **Set end timer via CronCreate**: One-shot timer at session end. Prompt: "GPU marathon timer fired. Wind down gracefully: let the current job finish its step, save outputs, commit and push everything."
5. **Read project CLAUDE.md and STATUS.md** to understand the current GPU job priority queue.

## Phase 1: Job Priority

Work from the highest-priority available job. Check the project's CLAUDE.md for its specific priority queue. For BioRefusalAudit (`C:\Users\caleb\projects\Deleeuw-AI-x-Bio-hackathon`):

1. Cross-model format ablations
2. Longer SAE training runs
3. Additional intervention experiments
4. Flagship reruns with new seeds
5. Held-out calibration

## Phase 2: Starting a GPU Job

- Always activate venv first: `source .venv/Scripts/activate` (Git Bash) or `.\.venv\Scripts\Activate.ps1` (PowerShell)
- Use `run_in_background=true` for all long jobs so Claude's main context stays responsive
- Create a new output directory per run — never overwrite a prior run
- After starting: set a monitoring CronCreate timer for the estimated completion time (err later, not earlier)

## Phase 3: Monitor and Chain

When a job's monitoring timer fires:
1. Check GPU: `nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv,noheader`
2. Check if output directory has the expected output file (`report.json`, `training_log.jsonl`, etc.)
3. If complete: parse results, commit outputs, write a 3-line note in `notes/`
4. Kill stray Python processes only if a job died ungracefully (verify with `nvidia-smi` first)
5. **Start the next job immediately** — no idle GPU time

## Phase 4: Graceful Shutdown (When Session Timer Fires)

1. Let the active job finish its current step or epoch — do NOT kill mid-epoch
2. Save all outputs to disk
3. Commit everything to git with message: `"GPU grant session <date> — <what ran>"`
4. Push to GitHub
5. Write `notes/SESSION_SUMMARY_<date>.md`: what ran, what it produced, what it means for next steps

## Windows-Specific Notes (GTX 1650 Ti / WDDM)

- **KMP OpenMP conflict**: Prefix all runs with `KMP_DUPLICATE_LIB_OK=TRUE`. Both torch and numpy load OpenMP separately on Windows.
- **device_map bug (bitsandbytes 0.49.2)**: Use `device_map={"": torch.cuda.current_device()}` (integer), NOT `{"": "cuda"}` (string). The string form silently falls to CPU with no error.
- **VRAM budget on 4 GB**: Gemma 2 2B-IT or Gemma 4 E2B-IT in 4-bit NF4 each fit. SAE training with d_sae=6144 needs ~0.8 GB additional. Budget model (~3 GB) + SAE (~0.8 GB) + buffer (0.2 GB).
- **Residual hook VRAM leak**: Overwrite `captured[0]` instead of appending. Appending fills ~240 MB over a 200-token generation and causes CPU spill on 4 GB cards.

## Standard Commands (BioRefusalAudit)

### Full eval run (new seed or new eval set)
```bash
KMP_DUPLICATE_LIB_OK=TRUE PYTHONPATH=. python -m biorefusalaudit.cli run \
    --model google/gemma-2-2b-it \
    --eval-set data/eval_set_public/eval_set_public_v1.jsonl \
    --out runs/gemma-2-2b-it-<suffix> \
    --sae-source gemma_scope_1 \
    --sae-release gemma-scope-2b-pt-res \
    --sae-id "layer_12/width_16k/average_l0_82" \
    --layer 12 \
    --catalog data/feature_catalog/gemma-2-2b-it.json \
    --calibration configs/calibration_gemma2_2b.yaml
```

### SAE local training (WMDP or local eval set)
```bash
KMP_DUPLICATE_LIB_OK=TRUE PYTHONPATH=. python scripts/train_sae_local.py \
    --eval-set data/eval_set_public/eval_set_public_v1.jsonl \
    --out runs/sae-training-<suffix> \
    --steps 5000 --batch-size 4
```

### Held-out calibration (fit T on new data)
```bash
# Step 1: Run eval on held-out set to collect activations + labels
KMP_DUPLICATE_LIB_OK=TRUE PYTHONPATH=. python -m biorefusalaudit.cli run \
    --eval-set data/eval_set_public/calibration_holdout_v3.jsonl \
    --out runs/gemma-2-2b-it-holdout-cal-<date> [... other flags ...]

# Step 2: Fit T from the resulting report
KMP_DUPLICATE_LIB_OK=TRUE PYTHONPATH=. python scripts/fit_calibration.py \
    --report runs/gemma-2-2b-it-holdout-cal-<date>/report.json \
    --config configs/calibration_gemma2_2b.yaml
```

### Intervention experiment (new prompt-category pair)
```bash
KMP_DUPLICATE_LIB_OK=TRUE PYTHONPATH=. python scripts/run_intervention.py \
    --model google/gemma-2-2b-it \
    --prompt-id <id> \
    --eval-set data/eval_set_public/eval_set_public_v1.jsonl \
    --catalog data/feature_catalog/gemma-2-2b-it.json \
    --calibration configs/calibration_gemma2_2b.yaml \
    --category refusal_circuitry \
    --top-k 5 \
    --out runs/interventions/<id>_ablation.json
```

## Skill Source

Authored 2026-04-25 for BioRefusalAudit (AIxBio Hackathon 2026). Generalizes to any local ML research project with a 4–16 GB GPU.
