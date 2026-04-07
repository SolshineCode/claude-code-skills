---
name: commercialize
description: Use this skill when the user wants to take a technology concept from idea to market-ready assets. Triggers include "bring to market", "commercialize", "patent and publish", "create everything needed to commercialize", "autonomous product development", or when the user wants patent drafts, scientific publications, product design, and business strategy built out in a dedicated GitHub repo.
---

# Commercialize: Autonomous Technology Commercialization Session

Launch a multi-hour autonomous session to take a technology concept from idea to market-ready assets — patent drafts, scientific publications, product design, business strategy — all in a new GitHub repo.

## Phase 0: Orientation

Before anything else:
1. Read `references/agent-prompts.md` for the full agent team definitions
2. Read `references/repo-structure.md` for the target repository layout
3. Read `references/patent-template.md` and `references/paper-template.md` for output templates

## Phase 1: Technology Interview (5-10 minutes)

If the user has not already provided a detailed technology description, conduct a focused interview. Ask in batches of 2-3 questions max:

**Round 1 — Core Concept:**
- What does this technology do in one sentence?
- What specific problem does it solve, and for whom?
- What is the key technical innovation (the thing that makes this non-obvious)?

**Round 2 — Technical Depth:**
- How does it work at a high level? (mechanism, architecture, process)
- What are the key components or subsystems?
- What existing approaches does this improve upon, and how?

**Round 3 — Market & IP:**
- Who would buy/use this? (target market segments)
- Are there existing patents or products in this space you're aware of?
- What's the intended form factor? (SaaS, hardware, API, library, device, etc.)

**Round 4 — Scope & Priorities:**
- Which workstreams matter most? (patent, paper, product, all?)
- Any specific conferences, journals, or patent offices to target?
- Preferred repo name and any branding/naming preferences?

After the interview, synthesize two descriptions:
- **Extensive description**: 2-3 paragraphs covering all technical and market details
- **Casual one-liner**: The "essentially it's..." version

Present both to the user for confirmation before proceeding.

## Phase 2: Repository Setup

Create a new GitHub repo and scaffold it:

```bash
# Create repo (private by default — user can publicize later)
gh repo create <repo-name> --private --clone --description "<casual one-liner>"
cd <repo-name>
```

Scaffold the directory structure per `references/repo-structure.md`. Create a comprehensive `CLAUDE.md` in the repo root with:
- The extensive technology description
- The casual one-liner
- Key technical terms and definitions
- Links between workstreams (e.g., patent claims should align with paper contributions)
- Any user preferences or constraints from the interview

Commit the scaffold as the initial commit.

## Phase 3: Prior Art & Research (Parallel Agents)

Before drafting anything, launch research agents in parallel:

**Agent 1 — Patent Prior Art Search:**
- Search Google Patents, USPTO, and web for related patents
- Identify the closest prior art and key differentiators
- Document in `research/prior-art/`

**Agent 2 — Academic Literature Search:**
- Search for related papers, surveys, and benchmarks
- Identify gaps this technology fills
- Document in `research/literature-review.md`

**Agent 3 — Competitive Landscape:**
- Search for existing products, startups, and open-source projects
- Map the competitive landscape
- Document in `research/competitive-landscape.md`

**Agent 4 — Market Data:**
- Search for market size, growth trends, and industry reports
- Identify target customer segments and pricing benchmarks
- Document in `research/market-data.md`

Wait for all research agents to complete. Review their findings — these inform ALL subsequent workstreams.

## Phase 4: Parallel Workstream Agents

Launch the main workstream agents in parallel. Each agent should read the research output and CLAUDE.md before starting. Full agent prompts are in `references/agent-prompts.md`.

### Agent Team:

1. **Patent Agent** — Drafts provisional patent application
   - Output: `patent/` directory (claims, specification, abstract, drawings descriptions)
   - Must reference prior art to establish novelty

2. **Paper Agent** — Drafts scientific publication
   - Output: `publication/` directory (full paper draft, figures descriptions)
   - Target format based on user's preferred venue, default to IEEE/ACM style

3. **Product Agent** — Designs the product
   - Output: `product/` directory (spec, user stories, UX flows, pricing)
   - Ground in competitive analysis and market data

4. **Business Agent** — Develops go-to-market strategy
   - Output: `business/` directory (market analysis, GTM plan, business model, pitch outline)
   - Use market data from research phase

5. **Technical Agent** — Designs implementation architecture
   - Output: `technical/` directory (architecture, tech stack, roadmap, prototype scaffolding)
   - Align with product spec and patent claims

## Phase 5: Cross-Workstream Alignment

After all agents complete, verify alignment across workstreams:

1. **Patent claims vs. paper contributions** — Each novel claim should map to a paper contribution and vice versa
2. **Product features vs. patent claims** — Key product differentiators should be covered by patent claims
3. **Business model vs. product spec** — Pricing and GTM should match the product's form factor and target market
4. **Technical architecture vs. product spec** — Architecture should support all specified features
5. **Competitive analysis consistency** — All workstreams should reference the same competitive landscape

Document any gaps or conflicts in `ALIGNMENT-REVIEW.md` at the repo root.

## Phase 6: Consolidation & Commit

1. Write a comprehensive `README.md` covering all workstreams with status
2. Create a `NEXT-STEPS.md` with prioritized action items for the user
3. Stage all files, create a meaningful commit
4. Push to GitHub
5. Save handoff notes to `.claude/handoff.md` in the user's home directory

## Progress Tracking

Use TaskCreate at the start to create tasks for each phase. Update task status as work progresses. This gives the user visibility into progress if they check in.

## Autonomy Guidelines

This is a long autonomous session. Follow these principles:

- **Bias toward action**: Make reasonable decisions rather than stopping to ask. Document assumptions in CLAUDE.md.
- **Depth over breadth**: One thorough patent draft is worth more than five shallow ones.
- **Web research is critical**: Use WebSearch and WebFetch extensively during research. Real prior art and market data make everything downstream stronger.
- **Save progress frequently**: Commit after each major phase completes, not just at the end.
- **Handoff notes**: If context limits approach, immediately save `.claude/handoff.md` with full status.
- **Quality over speed**: Patent claims need to be precise. Paper arguments need to be rigorous. Don't rush.

## Additional Resources

### Reference Files
- **`references/agent-prompts.md`** — Full prompt templates for each parallel agent
- **`references/repo-structure.md`** — Target directory layout for the created repo
- **`references/patent-template.md`** — Provisional patent application template and guidance
- **`references/paper-template.md`** — Scientific paper structure and writing guidance
