# Scientific Paper Template & Writing Guidance

## Paper Structure

The default structure follows IEEE/ACM conference format. Adapt to the user's target venue if specified.

### paper-draft.md Template

```markdown
# [Paper Title]
# [Subtitle if applicable]

**Authors:** [Names and affiliations — leave as placeholder for user to fill]

## Abstract

[150-250 words]
- Sentence 1: Context/problem statement
- Sentence 2: Gap in existing work
- Sentence 3: What this paper presents (the contribution)
- Sentence 4-5: Key method/approach
- Sentence 6: Main results (quantitative if possible)
- Sentence 7: Significance/implications

**Keywords:** [5-8 keywords, comma-separated]

## 1. Introduction

[~1-1.5 pages, structured as:]

**Opening paragraph:** Broad context — establish why this problem domain matters. Include a motivating example or statistic.

**Problem paragraph:** Narrow to the specific problem. What makes it hard? Why isn't it solved?

**Gap paragraph:** What existing approaches fail to do. Be specific — cite 3-5 key works and state their limitations factually (not dismissively).

**Contribution paragraph:** "In this paper, we present [name], a [type of contribution] that [does what]. Our key contributions are:"
- Contribution 1: [The core technical novelty]
- Contribution 2: [The methodology or framework]
- Contribution 3: [The evaluation/empirical results]

**Roadmap paragraph:** "The remainder of this paper is organized as follows. Section 2 discusses related work. Section 3 describes our approach. Section 4 presents our evaluation. Section 5 discusses limitations and future work. Section 6 concludes."

## 2. Related Work

[~1-1.5 pages]

Organize by approach/theme, NOT chronologically. Each subsection covers a category of related work:

### 2.1 [Approach Category A]
[3-5 works, each with: what they do, how, and their specific limitation that your work addresses]

### 2.2 [Approach Category B]
[Same structure]

### 2.3 [Approach Category C]
[Same structure]

**Closing paragraph:** Position your work relative to ALL the above: "Unlike [A] which [limitation], and [B] which [limitation], our approach [differentiator]."

## 3. Approach / Method / System Design

[~2-3 pages — the core technical section]

### 3.1 Overview
[High-level description with reference to system diagram (Figure 1)]

### 3.2 [Component/Step 1]
[Detailed description with formulas, algorithms, or design decisions]

### 3.3 [Component/Step 2]
[Same depth of detail]

### 3.4 [Component/Step 3]
[Same depth of detail]

**Writing guidance:**
- Include at least one algorithm box or formula
- Reference figures throughout
- Explain design decisions: not just WHAT but WHY
- Define all notation before using it
- Be specific enough for reproduction

## 4. Evaluation

[~2 pages]

### 4.1 Experimental Setup
- **Dataset(s):** Name, size, source, preprocessing
- **Baselines:** What you compare against and why these were chosen
- **Metrics:** What you measure and why these metrics are appropriate
- **Implementation details:** Hardware, software, hyperparameters, training procedure

### 4.2 Results

#### [Research Question 1]
[Results with reference to Table/Figure X]
[Statistical significance if applicable]
[Interpretation — what does this tell us?]

#### [Research Question 2]
[Same structure]

### 4.3 Ablation Study (if applicable)
[What happens when you remove key components?]

### 4.4 Analysis
[Deeper analysis: failure cases, edge cases, qualitative examples]

## 5. Discussion

### 5.1 Limitations
[Be honest — reviewers WILL find these. Being upfront is better.]
- Limitation 1 and potential mitigation
- Limitation 2 and potential mitigation

### 5.2 Future Work
[Concrete, actionable directions — not vague "we plan to improve"]

### 5.3 Broader Impact (if applicable)
[Societal implications, ethical considerations]

## 6. Conclusion

[~0.5 page]
- Restate the problem and contribution (don't copy the abstract)
- Summarize key results
- End with significance: why this matters going forward

## References

[Formatted per venue requirements — default IEEE style]
[Minimum 20-30 references for a full paper, 15-20 for a short/workshop paper]
```

## Writing Quality Guidelines

### Tone and Style
- **Active voice** preferred: "We propose" not "It is proposed"
- **Precise language**: "improves by 15%" not "significantly improves"
- **Present tense** for established facts, **past tense** for experiments
- **No marketing language**: "novel" is OK sparingly, avoid "revolutionary", "groundbreaking"
- **Define acronyms** on first use

### Common Pitfalls to Avoid
1. **Overclaiming**: Don't claim your results generalize beyond what you tested
2. **Underselling limitations**: Honest limitations build reviewer trust
3. **Vague related work**: "Several works have addressed this problem" — be specific
4. **Missing baselines**: Compare against the CURRENT state of the art, not just classic methods
5. **Cherry-picked results**: Show aggregate metrics, not just best-case examples

### Figures Strategy
Every paper needs:
1. **System/architecture diagram** (Section 3) — shows the big picture
2. **Results table or bar chart** (Section 4) — quantitative comparison
3. **Qualitative example** (Section 4) — shows what the system actually produces
4. Optional: Process diagram, ablation chart, failure case examples

For each figure, create a detailed description in `figures/figure-descriptions.md` that could be given to a graphic designer or used to create the actual figure.

## Venue-Specific Formatting

### IEEE Conference
- Two-column format
- 6-8 pages (10 with references)
- Author names and affiliations at top
- IEEE citation style: [1], [2], ...

### ACM Conference
- Two-column format
- 10-12 pages
- ACM classification codes
- ACM citation style: (Author, Year)

### arXiv Preprint
- Single or two-column
- No page limit
- Can include supplementary material inline
- Great for establishing priority while preparing venue submission

### Nature/Science (for breakthrough results)
- Very specific format — check guide for authors
- Short main text (~3,000-5,000 words) with extensive supplementary
- Figures limited (typically 4-6)

## Submission Strategy (submission-checklist.md)

```markdown
# Submission Strategy

## Target Venue
- **Primary:** [venue name, deadline, acceptance rate]
- **Backup:** [venue name, deadline]
- **arXiv preprint:** Recommend posting 1-2 weeks before submission deadline

## Pre-Submission Checklist
- [ ] Paper formatted per venue requirements
- [ ] All figures are high-resolution (300+ DPI)
- [ ] References are complete and correctly formatted
- [ ] Supplementary material prepared (if applicable)
- [ ] All co-authors have reviewed and approved
- [ ] Abstract submitted by abstract deadline (if separate)
- [ ] Conflict of interest declarations prepared
- [ ] Anonymized version (if double-blind review)

## Post-Submission
- [ ] arXiv version posted (if allowed by venue)
- [ ] Prepare rebuttal materials in advance
- [ ] Plan revision timeline based on notification date
```
