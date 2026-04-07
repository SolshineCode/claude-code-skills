# Target Repository Structure

Scaffold this structure when creating the new technology repo. Not all directories need content immediately — create the structure and populate as agents complete their work.

```
<repo-name>/
├── README.md                          # Project overview, status dashboard, links to all sections
├── CLAUDE.md                          # Technology description, key terms, cross-workstream rules
├── NEXT-STEPS.md                      # Prioritized action items for the user
├── ALIGNMENT-REVIEW.md                # Cross-workstream consistency check results
├── LICENSE                            # Appropriate license (default: proprietary until user decides)
│
├── patent/
│   ├── README.md                      # Patent strategy overview and filing guidance
│   ├── provisional-application.md     # Full provisional patent application draft
│   ├── claims.md                      # Independent and dependent claims (numbered)
│   ├── specification.md               # Detailed technical specification
│   ├── abstract.md                    # Patent abstract (150 words max)
│   ├── drawings-descriptions.md       # Descriptions of each figure/drawing needed
│   ├── prior-art-differentiation.md   # How each claim differs from closest prior art
│   └── filing-checklist.md            # Steps to file with USPTO/EPO/WIPO
│
├── publication/
│   ├── README.md                      # Publication strategy (target venue, timeline)
│   ├── paper-draft.md                 # Full paper draft (abstract through references)
│   ├── abstract.md                    # Standalone abstract for submission
│   ├── supplementary-material.md      # Additional results, proofs, or data
│   ├── figures/
│   │   └── figure-descriptions.md     # Description of each figure to be created
│   ├── related-work-notes.md          # Detailed notes on related work for literature review
│   └── submission-checklist.md        # Venue-specific formatting requirements
│
├── product/
│   ├── README.md                      # Product vision and status
│   ├── product-spec.md                # Detailed product specification
│   ├── user-stories.md                # User stories organized by persona
│   ├── user-flows.md                  # Key user journey descriptions
│   ├── competitive-analysis.md        # Feature comparison matrix
│   ├── pricing-strategy.md            # Pricing model, tiers, and rationale
│   ├── mvp-definition.md              # Minimum viable product scope
│   └── mockups/
│       └── mockup-descriptions.md     # Descriptions of UI mockups to be created
│
├── business/
│   ├── README.md                      # Business strategy overview
│   ├── market-analysis.md             # TAM/SAM/SOM, growth trends, segments
│   ├── go-to-market.md                # Launch strategy, channels, timeline
│   ├── business-model.md              # Revenue model, unit economics
│   ├── pitch-deck-outline.md          # Slide-by-slide outline for investor deck
│   ├── financial-projections.md       # Revenue/cost projections (3-5 year)
│   └── risk-analysis.md              # Key risks and mitigation strategies
│
├── technical/
│   ├── README.md                      # Technical overview and architecture decisions
│   ├── architecture.md                # System architecture and design
│   ├── tech-stack-analysis.md         # Technology choices with rationale
│   ├── implementation-roadmap.md      # Phased development plan
│   ├── api-design.md                  # API specification (if applicable)
│   ├── data-model.md                  # Data structures and storage design
│   └── prototype/
│       └── README.md                  # Prototype scope and setup instructions
│
└── research/
    ├── README.md                      # Research methodology and sources
    ├── prior-art/
    │   ├── patent-search-results.md   # Related patents with analysis
    │   └── key-patents.md             # Deep analysis of closest prior art
    ├── literature-review.md           # Academic literature survey
    ├── competitive-landscape.md       # Companies, products, and open-source alternatives
    └── market-data.md                 # Market size, trends, and projections
```

## Scaffold Script

To create the structure:

```bash
# Create all directories
mkdir -p patent publication/figures product/mockups business technical/prototype research/prior-art

# Create placeholder READMEs in each directory
for dir in patent publication product business technical research; do
  echo "# ${dir^}" > "$dir/README.md"
  echo "" >> "$dir/README.md"
  echo "_This section is being populated by the deep-work agent team._" >> "$dir/README.md"
done
```

## README.md Template

The root README should follow this structure:

```markdown
# [Technology Name]

> [Casual one-liner description]

## Overview

[Extensive description — 2-3 paragraphs]

## Repository Contents

| Section | Status | Description |
|---------|--------|-------------|
| [Patent](./patent/) | Draft | Provisional patent application and claims |
| [Publication](./publication/) | Draft | Scientific paper draft |
| [Product](./product/) | Draft | Product specification and design |
| [Business](./business/) | Draft | Market analysis and go-to-market strategy |
| [Technical](./technical/) | Draft | Architecture and implementation roadmap |
| [Research](./research/) | Complete | Prior art, literature review, competitive analysis |

## Key Innovation

[2-3 sentences on what makes this novel]

## Target Market

[Primary market segments]

## Status

This repository was generated as a comprehensive commercialization package. All documents are drafts requiring expert review before filing, submission, or execution.

## Next Steps

See [NEXT-STEPS.md](./NEXT-STEPS.md) for prioritized action items.
```
