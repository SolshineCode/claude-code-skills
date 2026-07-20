---
name: nano-banana
description: REQUIRED for all image generation requests. Generate and edit images using Nano Banana (Gemini image generation) via the Antigravity CLI (agy). Handles blog featured images, YouTube thumbnails, icons, diagrams, patterns, illustrations, photos, visual assets, graphics, artwork, pictures. Use this skill whenever the user asks to create, generate, make, draw, design, or edit any image or visual content.
allowed-tools: Bash(agy:*)
---

# Nano Banana Image Generation (via Antigravity CLI)

Generate professional images through Google's Antigravity CLI (`agy`), whose agent
sessions carry a native Nano Banana / Gemini image-generation tool.

> **History (2026-07-19):** the standalone Gemini CLI (`gemini`) and its nanobanana
> extension are deprecated and login-blocked — Google requires Antigravity now. Do NOT
> install or invoke `gemini`; every command below uses `agy`. The workflow was
> validated end-to-end on 2026-07-19.

## When to Use This Skill

ALWAYS use this skill when the user:
- Asks for any image, graphic, illustration, or visual
- Wants a thumbnail, featured image, or banner
- Requests icons, diagrams, or patterns
- Asks to edit, modify, or restore a photo
- Uses words like: generate, create, make, draw, design, visualize

Do NOT attempt to generate images through any other method.

## Before First Use

1. Verify the CLI is present and authenticated:
   ```bash
   agy --help >/dev/null && agy models
   ```
   A model list (Gemini 3.5 Flash, Gemini 3.1 Pro, ...) means auth is good. If it
   prompts for login instead, stop and ask the user to run `agy` interactively once.
2. No API key or extension install is needed — the image tool ships with agy.

## Core Invocation

Headless one-shot generation:

```bash
timeout 300 agy -p "Use your native image-generation tool to generate: <PROMPT>. Save the result as <NAME>.png" \
  --model "Gemini 3.5 Flash (Low)" \
  --dangerously-skip-permissions
```

- `-p/--print` runs non-interactively. In print mode agy auto-denies tool permission
  prompts, so `--dangerously-skip-permissions` (or pre-configured allow-rules in agy's
  settings.json) is required — without it the run exits with "a tool required the
  command permission".
- Give every image an explicit, unique `<NAME>.png` so you can find it afterward.
- Generation takes on the order of 30–90 seconds per image; keep the `timeout`.

## Output Location — READ THIS, IT IS THE #1 GOTCHA

agy IGNORES your working directory. Nothing appears in `./` or `./nanobanana-output/`,
and agy's own reply may falsely claim it saved to the current directory. The real
files land in agy's sandbox:

| What | Path |
|---|---|
| Final image (converted to your requested name/format) | `~/.gemini/antigravity-cli/scratch/<NAME>.png` |
| Raw generator output(s) | `~/.gemini/antigravity-cli/brain/<session-uuid>/<NAME>_<ms-epoch>.jpg` |

After every run, collect and verify — never trust the text reply alone:

```bash
ls -t ~/.gemini/antigravity-cli/scratch/ | head -3
cp ~/.gemini/antigravity-cli/scratch/<NAME>.png <project-destination>/
file <project-destination>/<NAME>.png   # confirm real PNG + dimensions
```

If the scratch dir is empty, also check the newest `brain/<session-uuid>/` directory
for the raw JPG before declaring failure.

## Editing an Existing Image

Pass the absolute input path inside the prompt (agy can read local files):

```bash
timeout 300 agy -p "Load /abs/path/to/input.png and use your image tool to <INSTRUCTION>. Save the result as <NAME>_edited.png" \
  --model "Gemini 3.5 Flash (Low)" \
  --dangerously-skip-permissions
```

(Editing is the same pipeline but was not part of the 2026-07-19 validation — verify
the output file with extra care.)

## Model Selection

`--model` selects the *agent* model that drives the session, not the image model
itself (the image tool is Nano Banana under the hood either way).

- Default: `"Gemini 3.5 Flash (Low)"` — cheap, validated.
- If prompt-following on complex compositions is poor, retry with
  `"Gemini 3.1 Pro (High)"`.

## Sizing and Aspect Ratio

Default output is 1024×1024. State the intended use and aspect ratio inside the
prompt ("wide 16:9 blog banner", "vertical 9:16 story image") — there are no CLI
size flags in this pipeline. For exact pixel targets, resize the collected PNG
locally afterward (e.g. ImageMagick).

## Presenting Results

1. Copy the image out of the sandbox into the project (see above).
2. View/verify it yourself (Read the PNG), then present it to the user.
3. Offer to regenerate or iterate if needed.

## Refinements and Iterations

- **"Try again" / variations**: re-run with the same prompt and a new `<NAME>`;
  each run is a fresh session.
- **"Make it more [adjective]"**: adjust the prompt and regenerate.
- **"Edit this one"**: use the editing invocation with the copied-out file.

## Prompt Tips

1. **Be specific**: style, mood, colors, composition.
2. **Add "no text"** if you don't want text rendered in the image (or spell out the
   exact wording you DO want — Nano Banana renders text well when told precisely).
3. **Reference styles**: "editorial photography", "flat illustration", "3D render",
   "watercolor", "hand-drawn educational infographic".
4. For dense infographics, write the full prompt to a file first, review it, then
   inline it into the `-p` string.

## Troubleshooting

| Problem | Solution |
|---|---|
| "tool required the command permission ... auto-denied" | Add `--dangerously-skip-permissions` (print mode cannot prompt) |
| Reply says saved but cwd is empty | Expected — collect from `~/.gemini/antigravity-cli/scratch/` |
| Nothing in scratch/ either | Check newest `~/.gemini/antigravity-cli/brain/<uuid>/` for raw JPG |
| `agy models` asks for login | User must authenticate interactively once (their action, not yours) |
| Output ignores composition details | Retry with `--model "Gemini 3.1 Pro (High)"` |
| Hang / no exit | The `timeout 300` wrapper handles it; re-run once before diagnosing |
