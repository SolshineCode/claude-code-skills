---
name: investor-pitch-deck
description: Orchestrates investor-materials, frontend-slides, investor-outreach, and /human-writing-check into a complete end-to-end YC-style pitch deck workflow. Can mine an existing draft deck for raw content and images without copying its slide structure. Produces an HTML deck, a Marp Markdown deck, and clear PDF/PPTX export instructions.
origin: local
---

# Investor Pitch Deck

You are an orchestration skill. Your job is to wire together `investor-materials`, `frontend-slides`, `investor-outreach`, and `/human-writing-check` into a single end-to-end fundraising deck workflow. You do not introduce new business logic — you coordinate other skills and enforce quality.

---

## When to Activate

- User wants a new YC-style, seed, Series A, or demo-day investor deck.
- User wants to refactor or tighten an existing deck.
- User points to a draft deck (PDF, PPTX, HTML, Marp, or Google Slides export) as a source of materials.
- User wants to integrate a deck with outreach emails or a one-pager.

If the request is only an investor email, route to `investor-outreach` instead.

---

## Mode Detection

Before doing anything, classify the request:

- **Greenfield** — no existing deck, user describes startup and wants one built.
- **Refactor** — user gives their own deck and wants it improved, shortened, or made YC-style.
- **Mining** — user provides an external or old deck to strip for raw materials only.

If unclear, ask exactly one question:
> "Should I build from scratch, refactor your current deck, or mine an existing deck for raw materials without copying its structure?"

---

## Step 1 — Lock the Canonical Facts (via investor-materials)

Activate `investor-materials` first. Use it to gather and confirm a single source of truth:

- Problem, solution, and product description.
- Traction metrics (users, revenue, retention, growth rate).
- Pricing and revenue model.
- Market framing (TAM/SAM/SOM where relevant).
- Raise amount, instrument, and intended use of funds.
- Team (names, roles, sharpest credibility anchors).
- Key milestones and timelines.

Produce a short **Canonical Facts** block (Markdown) and keep it in context for all downstream steps. If any numbers conflict across sources, stop and reconcile before continuing.

---

## Step 2 — Mining an Existing Deck (Mining mode only)

If the user provides a draft deck file:

1. Extract from it:
   - Useful sentences that clearly explain the product, metrics, or traction.
   - Data points: numbers, growth stats, pricing, milestones.
   - Visual assets the user owns: logos, product screenshots, charts, team photos.

2. Do NOT copy:
   - Slide order, layout, or visual structure.
   - Color scheme, fonts, or template style.
   - Any copy from a company that is not the user's.

3. Tell the user explicitly:
   > "I'll reuse your copy and assets where they help, but I will design a completely fresh slide structure and narrative."

4. Feed the mined material into the Canonical Facts (Step 1), correcting or supplementing it.

If the file is a PPTX, use `python-pptx` to extract text and image assets. If the file is a PDF, extract text via available tools and note any images the user should supply manually.

---

## Step 3 — Design the Slide Outline

Before generating any deck file, produce a **slide outline** (titles + 3–5 bullet points per slide).

Default YC/Sequoia-style flow:

1. Company + wedge — what you do in one sentence, who it's for.
2. Problem — who feels it, how painful, current workaround and its cost.
3. Solution — your product and why it's meaningfully better.
4. Product / demo — key screens, workflow, or UX proof.
5. Market — size, why now, tailwinds.
6. Business model — pricing, unit economics, margin logic.
7. Traction — numbers, cohort proof, growth rate, social proof.
8. Team — founders, relevant background, unfair advantage.
9. Competition / differentiation — who else exists, your wedge.
10. Ask — raise amount, instrument, optionally terms.
11. Use of funds / milestones — what you achieve with this round.
12. Appendix — detailed metrics, tech architecture, extra screenshots (optional).

Rules:
- One core idea per slide. If a slide is doing two jobs, split it.
- 4–6 bullets max per content slide, or a small grid — never a wall of text.
- All numbers on the outline must match the Canonical Facts exactly.

Show the outline to the user and confirm before generating the deck.

---

## Step 4 — Generate the Deck Artifact

### Option A: HTML deck (default)

Activate `frontend-slides` and pass it:
- The Canonical Facts.
- The approved slide outline.
- Style preference (ask if not stated; suggest "dark, venture pitch, bold" as a starting point).
- Any mined images or assets from Step 2.

`frontend-slides` should produce: `[startup-name]-pitch.html`

Requirements:
- Every slide fits in one viewport. No internal scrolling.
- Keyboard + touch navigation.
- Reveal animations on slide entry.
- `clamp()`-based type scaling.

### Option B: Marp Markdown (if user prefers CLI/PPTX workflow)

Generate `[startup-name]-pitch.md` in Marp-compatible Markdown. Include at the top of the file:

```
<!-- marp: true -->
<!-- theme: default -->
<!-- paginate: true -->
```

Tell the user the exact conversion commands:
```bash
# Install Marp CLI once
npm install -g @marp-team/marp-cli

# Generate PPTX
marp [startup-name]-pitch.md --pptx -o [startup-name]-pitch.pptx

# Generate PDF
marp [startup-name]-pitch.md --pdf -o [startup-name]-pitch.pdf

# Preview in browser
marp [startup-name]-pitch.md --preview
```

---

## Step 5 — PDF and PPTX Export

Always tell the user their export options, regardless of which format was generated:

**From HTML:**
- Open `[startup-name]-pitch.html` in Chrome or Edge.
- Go to Print → Destination: Save as PDF → Layout: Landscape → Save.
- For a scripted version: `npx puppeteer-cli print [startup-name]-pitch.html [startup-name]-pitch.pdf`

**From Marp:**
- Run `marp [startup-name]-pitch.md --pptx -o [startup-name]-pitch.pptx`
- The PPTX is editable in PowerPoint or Google Slides.

**If the user has a Puppeteer/Playwright pipeline:** Offer to adjust HTML margins, aspect ratio (`--width 1280 --height 720`), or CSS print media to fit their pipeline.

---

## Step 6 — Writing Quality Check

After generating slide content (titles, bullets, callouts), run `/human-writing-check` on the deck narrative.

Pass it:
- Slide titles and bullet text (strip raw HTML tags if needed; pass readable prose).
- Any memo or one-pager produced alongside the deck.
- Investor emails if the user requested them in this workflow.

Ask `/human-writing-check` to optimize for:
- Clarity and brevity.
- Natural, direct founder voice — not corporate filler.
- Removing clichés: "disruptive", "revolutionary", "game-changing", "passionate", "excited to share".
- Short sentences. Concrete proof over vague claims.

After revisions from `/human-writing-check`, verify all numbers still match the Canonical Facts. Do not let the writing pass change any metrics or claims.

If `/human-writing-check` is not available, do an inline pass:
- Cut every sentence longer than 20 words in half.
- Replace every adjective with a number or a proof point.
- Remove any sentence that could appear in any other startup's deck.

---

## Step 7 — Optional Supporting Materials

If the user wants more than the deck, use the appropriate skills:

- **One-pager or memo** → use `investor-materials` to produce a version that matches the deck's Canonical Facts exactly.
- **Cold emails, warm intro blurbs, or follow-ups** → use `investor-outreach`, feeding it the same Canonical Facts and key proof points from the deck.
- Run `/human-writing-check` on all outbound investor text before delivery.

---

## Quality Gates

Do not call the deck done until every item passes:

- [ ] Every number matches the Canonical Facts exactly.
- [ ] Raise amount, runway, and milestones are logically consistent.
- [ ] One idea per slide. No slide is doing two jobs.
- [ ] YC narrative flow is intact: problem → solution → why now → market → traction → business model → team → ask.
- [ ] `/human-writing-check` (or inline pass) has been applied to all prose.
- [ ] If a source deck was provided, its slide order and layout have NOT been copied.
- [ ] Mined images and copy have been integrated into the new structure, not dropped in as-is.
- [ ] User knows exactly how to export PDF and PPTX.
- [ ] File is named clearly: `[startup-name]-[round]-pitch.html` or `.md`.

---

## Failure Modes to Avoid

- Opening the deck on market size instead of the problem.
- Burying the ask at the end with no setup.
- Mixing traction, product, and business model on a single slide.
- Using inconsistent numbers across slides.
- Copying the visual structure of the source deck.
- Producing a deck without telling the user how to export it.
- Forgetting to run `/human-writing-check` before final delivery.
