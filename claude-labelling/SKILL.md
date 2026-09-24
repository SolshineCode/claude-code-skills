---
name: claude-labelling
description: Run a labelling task (classify, annotate, per-turn or per-item labels over transcripts, logs, documents or any text dataset) with Claude Code subagents on the subscription, with measured quality (two independent labellers, agreement gate, mechanical truth checks, recorded corrections) and continuous usage pacing against the session and weekly limits so spend stays reasonable for how close the weekly renewal is. Use when the user asks to label, annotate, classify or autolabel a dataset with Claude, or to "use spare Claude Code tokens for labelling".
---

# Claude labelling, with measured quality and paced spend

Labels produced here are **Claude autolabels: advisory, not ground truth**. Say so in every
output file. They become evidence only after someone independent checks them.

Two things decide whether a labelling run was worth its tokens: **were the labels right**, and
**did it leave the user enough of their plan**. This skill treats both as measured quantities.

---

## 1. Spend: pace against the usage page, never into a limit

**Read the real numbers, never estimate them.** Open Settings → Usage in the Claude web app
(with the Chrome tools: `https://claude.ai/settings/usage`; the panel can load a few seconds
late, so wait and re-zoom if the bars are grey). Record:
- current session % and its reset time
- weekly % and the weekly reset day/time
- whether **usage credits** are toggled on. If they are, reaching a plan limit spends real
  money instead of pausing. **Never plan to use them.** Tell the user the toggle is on, and do
  not change it yourself: it's an account setting.

**Before every batch, run the pacer:**
```bash
python ~/.claude/skills/claude-labelling/pace.py --session <S> --week <W> \
  --week-reset "YYYY-MM-DD HH:MM" --batch-session <measured> --batch-week <measured> [--credits-on]
```
- `GO`: launch the batch.
- `WAIT`: the session would pass 80% (75% with credits on). Schedule a wake-up just after the
  session reset and do only zero-token prep meanwhile (extraction, splitting, validators).
- `STOP`: the weekly ceiling is reached. Finish validating what exists, write it up, stop
  launching.
- The weekly ceiling is `100 - max(15, 12 × days to renewal)`: about 67% two days out, rising
  as renewal approaches. Early in the week the user keeps a large reserve.
- **Final window: in the last 2 hours before the weekly renewal, labelling may take the week up
  to 98% total.** Unused capacity is lost at reset. The session ceiling still applies, and a
  batch must be sized to finish before the reset.

**Measure batch cost, don't guess it.** Run the first batch, re-read the usage page, and set
`--batch-session` / `--batch-week` to the observed delta per batch. Re-measure if the batch
shape changes. Reference point from one real run, only for the first guess: five Sonnet
labellers on about 50 long agent transcripts cost about 18% of a session and 1-2% of a week.

**Re-read usage every 2-3 batches** and log each reading (time, session %, week %) in the
run's notes file.

---

## 2. Quality: the pipeline

### 2.1 Write the schema before labelling
A `SCHEMA.md` next to the data holds:
- purpose, unit and key (one row per what? keyed how, so labels can be joined back to the
  source, e.g. an activation capture);
- every field, with allowed values;
- **explicit scope decisions**. Example: whether hidden reasoning text is in scope. Leaving
  this implicit caused a real labelling defect on this machine;
- causality, if the labels describe a process over time: a label at step *t* may use only
  steps ≤ *t*. Episode outcomes are separate fields and never leak into step labels;
- the validation the labels must pass before use.

### 2.2 Extract exactly what the subject saw
The labelled text must be **exactly** what the labelled system saw: no truncation, no
re-rendering. A 1,500-character cut in an extractor once hid evidence the agent had actually
seen, and the labellers had to guess. Log per item what was stripped (e.g. hidden reasoning)
and why.

### 2.3 Pilot: 20-30 items, two independent labellers
- Two subagents label the same pilot separately (Sonnet is a good default).
- **Isolation:**
  - each labeller gets its own scratch-file prefix (`scratch_<ID>_*`), because a shared
    filename caused a write race once;
  - each is told never to open the other's outputs;
  - each must read every item itself, with scripts only to serialise decisions it has already
    made, no keyword heuristics.
- Compute Cohen's kappa per categorical field. **Gate: kappa ≥ 0.7 on the main field before
  scaling.**
- Read every disagreement. Most turn out to be **definitional gaps in the schema**, not reading
  errors. Write each resolution into the schema as a numbered rule (R1, R2, …), adjudicate the
  pilot under the rules, and keep both labellers' raw files.

### 2.4 Add a mechanical truth wherever one exists
Any field that can be computed from the data (a tool call happened, a string appeared, a
count) gets a script that computes it, and each labeller is scored for **accuracy against it**,
not just agreement with the other. When the labellers are right and the script is wrong, fix
the script (e.g. a regex missing a paraphrase), re-run everything, and say so.

### 2.5 Scale in tranches of about 50 items
- Labeller A labels the whole tranche in parts of about 12.
- An independent labeller B labels a **seeded 25% overlap**.
- Per tranche, validate:
  - coverage (exactly one row per item);
  - kappa on the overlap;
  - mechanical-truth accuracy;
  - structural checks (e.g. no impossible phase regressions).
- **Suspiciously perfect agreement is a reason to check for copying, not a result.** Grep B's
  tool-call record for reads of A's files, compare finish times, and compare free-text fields
  (independent labellers almost never write identical descriptions).
- **Never trust a labeller's self-reported counts.** Labellers mis-summarise their own output.
  Always recompute from the files.

### 2.6 Corrections: mechanical, uniform, recorded
- Rules that follow from the schema itself (e.g. "a turn with the report tool call IS the
  reporting phase") run as a **sweep over every tranche**, not just the ones you inspected.
  In one real run the sweep found 8 errors outside every overlap sample.
- Every change goes to a `CORRECTIONS_*.jsonl` with rule, from, to and why. **Raw label files
  are never edited.**
- A combined dataset is built by a script from the raw labels plus corrections, with a card
  giving per-source kappa, accuracy and correction counts.

### 2.7 Close out
- Dataset card: what it is, per-source quality, scope and limits, including "both labellers
  are the same model family" if true.
- Notes file: every defect found, and how it was caught.
- Everything committed.

---

## 3. Rules of thumb

- **Small test first.** The pilot always precedes scale.
- Correct your own mistakes in the record, dated, rather than editing them away.
- When a subagent reports something surprising, verify it from the files before repeating it.
- Parallel labellers are fine (5 at once worked well), but each needs distinct output and
  scratch paths.
- Stop and write up when `pace.py` says STOP, even mid-dataset. A clean partial dataset beats
  an exhausted plan.
