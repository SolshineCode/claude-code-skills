# Provisional Patent Application Template & Guidance

## Overview

A US provisional patent application establishes a priority date and gives 12 months to file a non-provisional. It requires:
1. A specification (description) that enables someone skilled in the art to practice the invention
2. At least one claim (recommended but technically optional for provisional)
3. Drawings (if necessary to understand the invention)
4. Cover sheet, filing fee, and inventor information

## provisional-application.md Structure

```markdown
# Provisional Patent Application

## Title of Invention
[Descriptive title — specific enough to distinguish from prior art]

## Cross-Reference to Related Applications
[If any — typically "Not applicable" for new filings]

## Field of the Invention
[Technical field, 1-2 sentences]
Example: "The present invention relates to natural language processing, and more particularly to methods and systems for real-time semantic disambiguation in multilingual conversational interfaces."

## Background of the Invention
[2-4 paragraphs covering:]
- The technical problem being solved
- Existing approaches and their limitations (reference specific prior art)
- Why existing solutions are inadequate
- The gap this invention fills

**Writing guidance:** Be specific about prior art shortcomings. Each limitation mentioned should map to a feature your invention addresses. Do NOT disparage prior art — describe factual limitations.

## Summary of the Invention
[1-2 paragraphs giving a high-level overview]
- State the invention in terms of its function and advantage
- Reference the key claims without restating them verbatim
- Mention unexpected or non-obvious benefits

## Brief Description of the Drawings
[List each figure with a one-sentence description]
Example:
- FIG. 1 is a system architecture diagram showing the major components of the invention.
- FIG. 2 is a flowchart illustrating the method of [core process].
- FIG. 3 is a comparison chart showing performance improvements over prior art.

## Detailed Description of the Invention

### Definitions
[Define key technical terms as used in this application]

### System Architecture
[Describe the overall system with reference to drawings]
- Name and describe each component
- Explain how components interact
- Include specific technical details (protocols, data formats, algorithms)

### Method of Operation
[Step-by-step description of how the invention works]
- Reference specific components from the architecture
- Include decision points and alternative paths
- Describe data transformations at each step

### Implementation Details
[Specific implementation guidance]
- Hardware requirements (if applicable)
- Software architecture
- Key algorithms with pseudocode or formulas
- Data structures

### Preferred Embodiments
[Describe 2-3 specific implementations]
- The primary/preferred embodiment in detail
- Alternative embodiments (different platforms, scales, use cases)
- Each embodiment should be specific enough to enable reproduction

### Experimental Results (if applicable)
[Performance data, benchmarks, comparisons]
- Quantitative comparisons with prior art
- Test conditions and methodology
- Statistical significance if applicable

## Claims
[See claims.md for detailed claim drafting]

## Abstract
[See abstract.md — 150 words max]
```

## claims.md Guidance

### Claim Structure

**Independent Claims** (broadest protection):
- Start with preamble: "A method for..." / "A system comprising..." / "A non-transitory computer-readable medium..."
- Include ONLY essential elements
- Use functional language where possible
- Draft at least 3 independent claims: method, system, and computer-readable medium

**Dependent Claims** (narrower, fallback protection):
- Reference the independent claim: "The method of claim 1, further comprising..."
- Add specific features, parameters, or alternatives
- Create a claim tree 3-4 levels deep
- Each dependent claim should add meaningful narrowing

### Claim Drafting Rules

1. **One sentence per claim** — use semicolons and "wherein" clauses, not periods
2. **Antecedent basis** — introduce elements with "a" first time, "the" thereafter
3. **Consistent terminology** — use the same term for the same thing throughout
4. **Means-plus-function** — avoid "means for" language unless intentional (triggers 35 USC 112(f))
5. **Method claims** — use gerund form: "receiving...", "processing...", "generating..."
6. **System claims** — describe components and their functions: "a processor configured to..."
7. **Avoid absolute language** — use "at least one", "one or more", "substantially"

### Example Claim Set

```
1. A method for [doing X], comprising:
   receiving, by a processor, [input data];
   processing the [input data] using [technique] to generate [intermediate result];
   determining, based on the [intermediate result], [decision]; and
   outputting [final result] based on the [decision].

2. The method of claim 1, wherein the [technique] comprises [specific algorithm].

3. The method of claim 1, wherein the [input data] comprises at least one of: [type A], [type B], or [type C].

4. The method of claim 2, further comprising:
   storing the [intermediate result] in [storage]; and
   retrieving previously stored [intermediate results] to improve subsequent [processing].

5. A system for [doing X], comprising:
   a memory storing instructions; and
   a processor coupled to the memory and configured to execute the instructions to:
     receive [input data];
     process the [input data] using [technique] to generate [intermediate result];
     determine, based on the [intermediate result], [decision]; and
     output [final result] based on the [decision].

6. A non-transitory computer-readable medium storing instructions that, when executed by a processor, cause the processor to perform operations comprising:
   [same steps as method claim 1].
```

## abstract.md Guidance

- Exactly 150 words or fewer
- One paragraph, no line breaks
- State the technical problem and solution
- Mention key advantage
- Do NOT use marketing language or subjective terms
- Do NOT reference claim numbers or drawing numbers

## drawings-descriptions.md Guidance

Describe each figure needed. A patent attorney or illustrator will create the actual drawings from these descriptions.

Required figures (minimum):
1. **System architecture diagram** — showing all major components and their connections
2. **Method flowchart** — showing the core process step-by-step
3. **Comparison/results figure** — showing improvement over prior art (if quantitative data exists)

Optional but recommended:
4. **Data flow diagram** — showing how data transforms through the system
5. **Alternative embodiment diagram** — showing a different implementation
6. **User interface diagram** — if the invention has a user-facing component

For each figure, describe:
- What it shows
- All labeled components
- Arrows and their meaning
- Any data values or annotations

## Filing Guidance (filing-checklist.md)

```markdown
# Patent Filing Checklist

## Before Filing
- [ ] Review all claims with a patent attorney
- [ ] Conduct professional prior art search (supplement the AI-generated one)
- [ ] Verify all technical details are accurate and enabling
- [ ] Ensure consistent terminology throughout
- [ ] Have all inventors review and approve

## Filing Options
- **USPTO Provisional**: $320 (small entity) / $160 (micro entity) — 12 months to file non-provisional
- **PCT International**: For international protection — 30/31 months from priority date
- **Direct foreign filing**: Country-specific requirements

## Post-Filing
- [ ] Record filing date and application number
- [ ] Set 12-month reminder for non-provisional deadline
- [ ] Continue developing the technology (improvements can be filed as continuations)
- [ ] Consider publication strategy (patent publishes 18 months after filing)

## Cost Estimates (USPTO, 2024-2025)
- Provisional filing: $160-$320
- Non-provisional filing: $800-$1,600
- Patent attorney fees: $5,000-$15,000+
- Total through grant: $10,000-$30,000+
```
