---
name: research-slides
description: Build or review empirical ML/LLM research update slides (weekly mentor meetings, team syncs, research-log decks). Covers deck structure (summary/agenda/results/backup/discussion), chart design rules, and annotation patterns for prompt/completion examples, scaling curves, and definitions. Use when the user asks for research meeting slides, a mentor-update deck, a results/progress deck, or wants an existing research deck reviewed for clarity. Based on Chua/Hughes/Perez/Evans, "Tips On Empirical Research Slides" (LessWrong, Jan 2025), including the visual patterns in the post's example slide images and Ted Sanders' comment additions.
user_invocable: true
---

# Research Slides

Guidance for building or reviewing empirical-research update decks — the kind presented weekly to a mentor, PI, or team, showing experiment results and asking for a decision. The goal of every slide is the same: let a busy person who manages multiple projects understand what happened and what you need from them, in seconds, without re-deriving your reasoning.

Two failure modes to design against: (1) the mentor has to ask "wait, what were we discussing again?" because there's no recap, and (2) the mentor has to squint at a dense chart or transcript to figure out what you want them to notice. Everything below exists to prevent one of those two things.

## When to use this

- User asks to build slides for a research update, mentor meeting, lab meeting, or progress review involving experiments/metrics
- User wants an existing deck (Google Slides export, Markdown outline, or HTML deck) reviewed for clarity/structure
- User is deciding how to present an A/B-style intervention result, a scaling curve, or a prompt/completion example
- If the deliverable is an actual HTML/reveal.js deck, pair this skill with `frontend-slides` for the rendering/build mechanics — this skill governs *what goes on each slide and why*, not the build tooling.

## Deck structure, in order

1. **Summary slide (always slide 1).** Two things only:
   - Recap: last meeting's key takeaway and what you said you'd do next.
   - This week: what you ran and the headline result — worked or didn't. If it worked, your mentor will want sanity checks, controls, and extension ideas. If it didn't, they'll want to debug why (better data? better prompts?). Say which mode you're in so they can orient immediately.
   - End with 1-2 discussion bullets (e.g. "what's a reasonable control baseline?"). This slide alone should let a mentor who forgot everything about your project re-engage in 10 seconds.
2. **Agenda slide** (group meetings only, where time is contested). List sections in priority order, with slide count and rough minutes per section, so people can calibrate how deep to go given the time left.
3. **Results slides**, one experiment/claim per slide, most important result first. See "Chart design rules" below.
4. **Backup slides**, appended at the end, held in reserve for likely questions. See "Backup slide patterns" below.
5. **Discussion slide (always last of the main deck, before backups).** Concrete proposed next steps + explicit ask (a decision, feedback on priorities, or a resource — e.g. "I'm compute-bottlenecked, can I get X").

## Deck-level habits

- **One deck per project, not one per meeting.** A single running Google Slides link. Add new slides at the *front* of the deck, oldest at the back — so the deck always opens on "what's new" and still reads as a chronological record if someone scrolls back.
- **Use the weekly deck to pressure-test the paper's narrative**, not just report numbers. Include a slide stating the current story you'd tell in the paper, even in a form as short as one sentence, and ask directly whether it holds up. Catching a narrative problem in week 3 is cheap; catching it while writing the paper is not.
- **Get a peer read before the meeting.** Someone outside the project will catch jargon and slides that assume context the mentor doesn't have.
- Budget real time for this: expect 1-2 days on your first few decks, dropping to about half a day once you have reusable slide templates and chart code.

## Chart design rules

These are the mechanics behind every "good" example in the source post — confirmed by inspecting the actual slide images, not just the surrounding prose.

- **Always show the prompt/setup next to the chart it produced**, not just the metric name. Put a compact boxed diagram (e.g. "Test setup" card: User prompt → Sycophantic Answer vs. Normal Answer, each answer in a small colored chip) to the left of the bar chart it explains. Truncate long prompts here; put the full prompt in a backup slide.
- **Give the slide a claim for a headline, not a topic label.** "Takeaway: intervention reduces sycophancy" beats "Sycophancy results." Every strong example slide in the source states its conclusion in the title, above the chart — the chart then proves the headline, it doesn't stand in for it. (Ted Sanders' comment makes this explicit: use verb-based, active titles, not noun labels.)
- **Bar chart mechanics that show up consistently in the good examples:**
  - Error bars on every bar (fast heuristic for a proportion: SE = sqrt(p(1-p)/N)).
  - The numeric value printed directly above/on each bar — don't make the reader read the axis.
  - Y-axis labeled with the metric AND the desired direction, e.g. "% sycophantic answer (lower better)" — don't make the reader infer whether up or down is good.
  - 3-5 flat, distinct solid colors max on one chart; no gradients. A light tint background panel behind the plot area (not white) helps it read as a distinct chart region on a slide, not a floating dangling widget.
  - Category labels horizontal, not diagonal. If names are long enough to force a diagonal tilt, that's the signal to cut conditions or switch to horizontal bars (Ted Sanders' suggestion) rather than rotate labels.
- **Make the plot big.** On a video call the plot is often the only thing anyone can actually read — err toward oversized over "elegant." Add takeaway text only if it doesn't shrink the plot.
- **Lead with your best/most important result**, not a chronological tour of everything you tried. A slide that lists five interventions side by side with no stated winner forces the mentor to do your synthesis for you — do the synthesis yourself and only show the setups that are still live.
- **Calculate error bars on deltas, not just endpoints**, when the claim is about a difference between two conditions (Ted Sanders' addition) — the raw per-bar SE understates uncertainty in the comparison you're actually making.
- **Use real data and real prompts, not abstracted metric names**, wherever it fits on the slide — a slide that says "sycophancy rate" in the abstract is less convincing than one showing an actual model transcript next to the number.

### Two specific things to avoid (confirmed from the post's own negative examples)

- **Don't put 8+ bars with diagonal x-axis labels on a main slide.** The source's own "Things I tried last week" negative example does exactly this: nine differently-colored bars, tilted category names, no stated winner. It's illegible and has no single takeaway — exactly the failure mode the headline rule above exists to prevent. Cut to the top 2-3 conditions on the main slide; the rest belong in backup slides for if-asked.
- **Don't use a heatmap to show a grid of point values** (e.g. accuracy by learning-rate × intervention). Heatmaps force the audience to cross-reference both axes to read a single number, which is real cognitive work on a call. Condense to a bar chart of the conditions that actually matter, or to a short table if you truly need the full grid, and keep the heatmap (if at all) in backup slides.

## Backup slide patterns

Backup slides are reference material, not presentation material — they can be denser and less polished, since they're something you flick to only if the conversation goes there. Three recurring patterns from the source's own backups:

1. **Term definitions.** State the definition in one bold sentence at the top, larger than body text (e.g. "Sycophancy - model changes answer to match user's opinion"), then show a real annotated transcript below it with the key phrase highlighted (background-color highlight, not just bold, so it's findable at a glance) rather than a wall of unmarked dialogue. This is the slide you flick to when a new collaborator joins the call and needs the term defined precisely.
2. **Annotated prompt/completion pairs.** Two columns, prompt on the left and model completion on the right. Draw a colored rectangle box around the specific sentence(s) in each column that support your claim — don't rely on the reader to find them in a full transcript. Add one short arrow-and-caption at the bottom stating the inference in plain words (e.g. "Model produces motivated reasoning"). State the interpretive claim as the slide's headline, above both columns, exactly like the main-slide headline rule.
3. **Scaling curves, ready for "have you tried more data?".** A line plot with error bars and value labels at each point, PLUS a flat horizontal reference line in a second, contrasting color marking the target/ceiling you're aiming for (labeled inline, e.g. "Accuracy we aim for: totally unaffected by sycophancy") so the gap between "where we are" and "where we want to be" is visible at a glance rather than something the mentor has to hold in their head. Add a side annotation with an arrow pointing at the flattening part of the curve that translates the plot into one plain-English sentence with the actual before/after numbers (e.g. "Accuracy improves from 34% with 1k samples → 36% with 20k samples"). Also keep ready: log-log versions if you suspect scaling-law behavior (plot -log(acc) on y if using accuracy), a slide proposing simple baselines that would invalidate your result, and a training-details slide (prompts/responses used, hyperparameters, dataset, loss curve) for anything that didn't work.

## Pre-presentation checklist

- [ ] Slide 1 recaps last meeting's takeaway + this week's headline result (worked/didn't) + a discussion prompt
- [ ] Every results slide's title is a claim/sentence, not a topic label
- [ ] Every chart has error bars, on-chart value labels, and an axis label stating the metric's direction
- [ ] No chart has more than ~5 bars/colors on a main slide; nothing has diagonal axis labels
- [ ] No heatmaps on main slides
- [ ] The most important result is first, not buried after weaker ones
- [ ] Every prompt-based claim shows the actual prompt (truncated on the main slide, full version in backup)
- [ ] Backup slides exist for: term definitions, at least one annotated prompt/completion example, and a scaling-curve answer to "did you try more data?"
- [ ] Last slide states concrete next steps and a specific ask (decision, feedback, or resource)
- [ ] A peer has read through it once for jargon/gaps
- [ ] New slides were added at the front of the running deck, not a fresh deck

## Source

James Chua, John Hughes, Ethan Perez, Owain Evans, ["Tips On Empirical Research Slides"](https://www.lesswrong.com/posts/i3b9uQfjJjJkwZF4f/tips-on-empirical-research-slides), LessWrong, 7 Jan 2025. Chart/annotation mechanics above were confirmed by inspecting the post's own example slide screenshots, not inferred from text alone. Additional points (horizontal bars for long labels, verb-based titles, delta error bars, real-data-over-abstraction) from Ted Sanders' top comment on the post.
