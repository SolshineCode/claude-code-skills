# Agent Team Prompts

Full prompt templates for each parallel agent spawned during the deep-work session. Each prompt is designed to be passed directly to the Agent tool.

## Phase 3: Research Agents

### Agent 1 — Patent Prior Art Search

```
TASK: Patent Prior Art Search

TECHNOLOGY: {{extensive_description}}

REPO: {{repo_path}}

Search for related patents and prior art. Use WebSearch extensively with queries like:
- "patent [key technical terms]"
- "USPTO [core mechanism]"
- "patent application [problem domain]"
- "[specific technique] patent claims"
- site:patents.google.com [key terms]

For each relevant result found:
1. Record the patent number, title, assignee, and filing date
2. Summarize what the patent covers
3. Identify how our technology DIFFERS from this patent
4. Rate relevance: HIGH (same problem + similar approach), MEDIUM (same problem, different approach), LOW (related field)

Create two files:
1. `research/prior-art/patent-search-results.md` — All search results organized by relevance
2. `research/prior-art/key-patents.md` — Deep analysis of the 3-5 closest patents, with specific claim-by-claim differentiation

Also note any unpatented approaches found in academic papers or open-source projects that are relevant prior art.

IMPORTANT: Be thorough. Search at least 10 different query variations. The strength of the patent application depends on the completeness of the prior art search.
```

### Agent 2 — Academic Literature Search

```
TASK: Academic Literature Search

TECHNOLOGY: {{extensive_description}}

REPO: {{repo_path}}

Search for related academic papers, surveys, and benchmarks. Use WebSearch with queries like:
- "[technical terms] survey"
- "[problem domain] state of the art"
- "[specific technique] paper"
- "[related method] benchmark results"
- site:arxiv.org [key terms]
- site:scholar.google.com [key terms]

For each relevant paper:
1. Record: authors, title, venue, year
2. Summarize: what problem it addresses, the approach, key results
3. Identify: how it relates to our technology (precursor, alternative, complementary)
4. Note: any benchmarks or datasets it introduces

Create `research/literature-review.md` with:
- **Overview** — The research landscape in 2-3 paragraphs
- **Categorized review** — Papers grouped by approach/theme (3-5 categories)
- **Identified gaps** — What the existing literature does NOT address that our technology does
- **Key benchmarks** — Relevant evaluation methods and datasets
- **Reference list** — Full citations formatted for IEEE

Target: 15-25 relevant papers, with 5-8 analyzed in depth.
```

### Agent 3 — Competitive Landscape

```
TASK: Competitive Landscape Analysis

TECHNOLOGY: {{extensive_description}}

REPO: {{repo_path}}

Search for existing products, startups, and open-source projects in this space. Use WebSearch with queries like:
- "[problem domain] startup"
- "[solution type] SaaS/product/tool"
- "[key terms] alternative"
- "[industry] market leaders"
- "companies solving [specific problem]"
- site:github.com [relevant project terms]
- site:producthunt.com [relevant terms]
- site:crunchbase.com [industry terms]

For each competitor:
1. Name, website, founding date, funding (if found)
2. What they offer (features, pricing if public)
3. How they differ from our technology
4. Their strengths and weaknesses

Create `research/competitive-landscape.md` with:
- **Direct competitors** — Companies solving the same problem (same approach or different)
- **Indirect competitors** — Companies solving adjacent problems or serving the same market
- **Open-source alternatives** — Relevant OSS projects
- **Feature comparison matrix** — Table comparing key features across competitors and our technology
- **Market positioning map** — Where each player sits on key dimensions (e.g., price vs. capability, generality vs. specialization)
- **Competitive advantages** — What our technology offers that no competitor does

Target: 5-10 direct competitors, 5-10 indirect, 3-5 OSS alternatives.
```

### Agent 4 — Market Data

```
TASK: Market Data Research

TECHNOLOGY: {{extensive_description}}

REPO: {{repo_path}}

Search for market size, growth trends, and industry data. Use WebSearch with queries like:
- "[industry] market size 2024 2025"
- "[market segment] TAM SAM SOM"
- "[industry] growth rate forecast"
- "[problem domain] spending trends"
- "[target customer type] budget allocation"
- "[industry] market report"

Gather data on:
1. **Total Addressable Market (TAM)** — The full market if every potential customer adopted
2. **Serviceable Addressable Market (SAM)** — The segment reachable with our go-to-market
3. **Serviceable Obtainable Market (SOM)** — Realistic capture in first 1-3 years
4. **Growth trends** — YoY growth rates, 5-year projections
5. **Customer segments** — Who buys, how much they spend, what drives their decisions
6. **Pricing benchmarks** — What similar solutions charge

Create `research/market-data.md` with:
- **Market Overview** — Size, growth, key trends (with sources)
- **TAM/SAM/SOM Analysis** — With methodology and sources
- **Customer Segments** — Profiles of 3-5 target segments with size and willingness to pay
- **Pricing Landscape** — How competing solutions price (freemium, subscription, usage-based, etc.)
- **Industry Trends** — Regulatory, technological, and market forces that help or hinder adoption
- **Key Statistics** — Bullet list of the most compelling data points for a pitch deck

IMPORTANT: Cite sources for ALL numerical claims. Distinguish between hard data and estimates.
```

## Phase 4: Workstream Agents

### Patent Agent

```
TASK: Draft Provisional Patent Application

TECHNOLOGY: {{extensive_description}}

REPO: {{repo_path}}

Read the following before starting:
1. The CLAUDE.md in the repo root (technology description and key terms)
2. research/prior-art/ (prior art analysis — essential for claims differentiation)
3. research/literature-review.md (academic context)
4. The patent template in the skill's references/patent-template.md

Then draft the complete provisional patent application:

1. `patent/claims.md` — Start here. Draft 3 independent claims (method, system, CRM) and 15-20 dependent claims. Each claim must be distinguishable from the closest prior art identified in research.

2. `patent/specification.md` — Detailed technical specification enabling reproduction. Reference specific prior art to establish novelty. Include pseudocode/algorithms where applicable.

3. `patent/abstract.md` — 150 words max. Technical, not marketing.

4. `patent/drawings-descriptions.md` — Describe 5-8 figures that would accompany the application.

5. `patent/prior-art-differentiation.md` — For each independent claim, explicitly state how it differs from the 3 closest prior art references.

6. `patent/provisional-application.md` — The assembled full application draft.

7. `patent/filing-checklist.md` — Steps to file with USPTO.

8. `patent/README.md` — Patent strategy overview, claim summary, and key differentiators.

CRITICAL GUIDANCE:
- Claims must be precise: one sentence each, proper antecedent basis, consistent terminology
- The specification must ENABLE — someone skilled in the art must be able to build it
- Every feature in the claims must be described in the specification
- Reference actual prior art from the research phase (don't make up patent numbers)
- Err on the side of broader claims with dependent claims for specificity
```

### Paper Agent

```
TASK: Draft Scientific Publication

TECHNOLOGY: {{extensive_description}}

REPO: {{repo_path}}

Read the following before starting:
1. The CLAUDE.md in the repo root
2. research/literature-review.md (essential for related work section)
3. research/competitive-landscape.md (context for positioning)
4. The paper template in the skill's references/paper-template.md

Then draft the complete paper:

1. `publication/paper-draft.md` — Full paper draft following the template structure:
   - Abstract (150-250 words)
   - Introduction with clear contribution statement
   - Related Work organized by theme/approach (reference actual papers from research)
   - Method/Approach section with technical depth (include algorithms, formulas where applicable)
   - Evaluation section (design evaluation plan even if experiments haven't been run yet — describe what WOULD be measured and how)
   - Discussion with honest limitations
   - Conclusion

2. `publication/abstract.md` — Standalone abstract for submission systems

3. `publication/figures/figure-descriptions.md` — Detailed descriptions for 4-6 figures

4. `publication/related-work-notes.md` — Extended notes on each related work reference

5. `publication/supplementary-material.md` — Additional technical details, proofs, or extended results

6. `publication/submission-checklist.md` — Venue selection and formatting requirements

7. `publication/README.md` — Publication strategy, target venues, and timeline

WRITING GUIDANCE:
- Active voice, precise language, no marketing speak
- Cite real papers from the literature review — don't fabricate references
- If experiments haven't been run, write the evaluation as a proposed plan: "We plan to evaluate..." or "The evaluation methodology will..."
- Be honest about what is theoretical vs. empirically validated
- Target 8-10 pages in two-column format (approximately 5,000-7,000 words)
```

### Product Agent

```
TASK: Product Design and Specification

TECHNOLOGY: {{extensive_description}}

REPO: {{repo_path}}

Read the following before starting:
1. The CLAUDE.md in the repo root
2. research/competitive-landscape.md (feature benchmarking)
3. research/market-data.md (pricing and customer segments)

Then create the complete product design:

1. `product/product-spec.md` — Detailed product specification:
   - Product vision (one paragraph)
   - Target users (primary and secondary personas)
   - Core features (must-have for launch)
   - Nice-to-have features (post-launch roadmap)
   - Non-functional requirements (performance, security, scalability)
   - Integration points (APIs, third-party services)
   - Success metrics (KPIs to track)

2. `product/user-stories.md` — User stories organized by persona:
   - Format: "As a [persona], I want to [action] so that [benefit]"
   - Priority: Must/Should/Could/Won't (MoSCoW)
   - Acceptance criteria for each Must story

3. `product/user-flows.md` — Key user journeys:
   - Onboarding flow
   - Core usage flow (the primary value-delivering workflow)
   - Admin/configuration flow (if applicable)
   - Each flow described step-by-step with decision points

4. `product/competitive-analysis.md` — Feature comparison:
   - Table: our product vs. top 5 competitors
   - Features as rows, products as columns
   - Highlight unique differentiators

5. `product/pricing-strategy.md` — Pricing model:
   - Recommended pricing model (subscription, usage-based, freemium, etc.) with rationale
   - Tier definitions if applicable
   - Comparison to competitor pricing
   - Unit economics analysis

6. `product/mvp-definition.md` — MVP scope:
   - What's in the MVP (minimum viable set of features)
   - What's explicitly OUT of the MVP
   - Estimated effort (T-shirt sizes: S/M/L/XL)
   - Launch criteria

7. `product/mockups/mockup-descriptions.md` — UI/UX descriptions:
   - Key screens/pages with layout descriptions
   - Navigation structure
   - Information architecture

8. `product/README.md` — Product overview and status

GUIDANCE:
- Ground everything in market data — don't invent target markets
- Pricing should be benchmarked against actual competitor pricing
- MVP should be genuinely minimal — resist scope creep
- User stories should be testable (clear acceptance criteria)
```

### Business Agent

```
TASK: Business Strategy and Go-to-Market Plan

TECHNOLOGY: {{extensive_description}}

REPO: {{repo_path}}

Read the following before starting:
1. The CLAUDE.md in the repo root
2. research/market-data.md (market sizing and trends)
3. research/competitive-landscape.md (positioning)

Then create the complete business strategy:

1. `business/market-analysis.md` — Market analysis:
   - TAM/SAM/SOM with methodology (use data from research)
   - Market segmentation
   - Customer personas with buying behavior
   - Market trends and tailwinds
   - Regulatory landscape (if applicable)

2. `business/go-to-market.md` — Launch strategy:
   - Positioning statement: "For [target] who [need], [product] is a [category] that [differentiator]. Unlike [alternative], our product [key advantage]."
   - Channel strategy: How to reach customers
   - Launch timeline (Phase 1: beta, Phase 2: public launch, Phase 3: scale)
   - Marketing plan: Content, partnerships, events, ads
   - Sales strategy: Self-serve, sales-assisted, or enterprise
   - Key partnerships to pursue

3. `business/business-model.md` — Revenue model:
   - Revenue streams
   - Pricing model (align with product/pricing-strategy.md)
   - Unit economics (CAC, LTV, LTV:CAC ratio targets)
   - Margin analysis
   - Break-even analysis

4. `business/pitch-deck-outline.md` — Investor deck outline:
   - Slide-by-slide content (12-15 slides):
     1. Title/hook
     2. Problem
     3. Solution
     4. Market size
     5. Business model
     6. Traction/validation
     7. Product demo/screenshots
     8. Competition
     9. Team (placeholder)
     10. Financial projections
     11. Ask (funding amount and use of funds)
     12. Closing/contact

5. `business/financial-projections.md` — 3-year projections:
   - Revenue projections (conservative, base, optimistic)
   - Cost structure (fixed and variable)
   - Headcount plan
   - Cash flow projections
   - Key assumptions stated explicitly

6. `business/risk-analysis.md` — Risk assessment:
   - Technical risks and mitigations
   - Market risks and mitigations
   - Competitive risks and mitigations
   - Regulatory risks and mitigations
   - Financial risks and mitigations

7. `business/README.md` — Business strategy overview

GUIDANCE:
- All financial numbers should be grounded in market data with explicit assumptions
- Be realistic — investors see through hockey stick projections without justification
- Include both optimistic and conservative scenarios
- Positioning should be clear and defensible
```

### Technical Agent

```
TASK: Technical Architecture and Implementation Roadmap

TECHNOLOGY: {{extensive_description}}

REPO: {{repo_path}}

Read the following before starting:
1. The CLAUDE.md in the repo root
2. patent/specification.md (technical details from patent, if available)
3. product/product-spec.md (features to support, if available)

Then create the complete technical design:

1. `technical/architecture.md` — System architecture:
   - High-level architecture diagram (described in text/ASCII)
   - Component breakdown with responsibilities
   - Data flow between components
   - External integrations
   - Scalability considerations
   - Security architecture
   - Deployment architecture (cloud provider, containers, serverless, etc.)

2. `technical/tech-stack-analysis.md` — Technology choices:
   - Recommended stack with rationale for each choice
   - Alternatives considered and why they were rejected
   - Build vs. buy decisions
   - Open-source vs. proprietary components
   - Licensing implications

3. `technical/implementation-roadmap.md` — Development plan:
   - Phase 1: Prototype (weeks 1-4) — core proof of concept
   - Phase 2: MVP (weeks 5-12) — minimum viable product
   - Phase 3: Beta (weeks 13-20) — testing and iteration
   - Phase 4: Launch (weeks 21-26) — production readiness
   - Each phase: goals, deliverables, key risks, team size needed

4. `technical/api-design.md` — API specification (if applicable):
   - RESTful or GraphQL design
   - Key endpoints with request/response schemas
   - Authentication/authorization scheme
   - Rate limiting strategy
   - Versioning strategy

5. `technical/data-model.md` — Data design:
   - Core entities and relationships (ERD described in text)
   - Storage strategy (SQL, NoSQL, time-series, graph, etc.)
   - Data migration and versioning approach
   - Privacy and data retention policies

6. `technical/prototype/README.md` — Prototype specification:
   - What the prototype demonstrates
   - Setup instructions (even if placeholder)
   - Dependencies
   - Architecture of the prototype itself

7. `technical/README.md` — Technical overview and key decisions

GUIDANCE:
- Architecture should support the features in the product spec
- Be specific about technology choices — "a database" is not helpful, "PostgreSQL with TimescaleDB for time-series data" is
- Implementation roadmap should be realistic for a small team (2-5 engineers)
- Include diagrams described in ASCII art or structured text
- Consider operational concerns: monitoring, logging, alerting, disaster recovery
```

## Agent Spawning Pattern

When spawning agents, use this pattern:

```
# Research phase — spawn all 4 in parallel
Agent(prompt="[Agent 1 prompt with {{variables}} filled in]", description="Prior art research")
Agent(prompt="[Agent 2 prompt]", description="Literature search")
Agent(prompt="[Agent 3 prompt]", description="Competitive analysis")
Agent(prompt="[Agent 4 prompt]", description="Market research")

# Wait for all research agents to complete

# Workstream phase — spawn all 5 in parallel
Agent(prompt="[Patent Agent prompt]", description="Patent drafting")
Agent(prompt="[Paper Agent prompt]", description="Paper drafting")
Agent(prompt="[Product Agent prompt]", description="Product design")
Agent(prompt="[Business Agent prompt]", description="Business strategy")
Agent(prompt="[Technical Agent prompt]", description="Technical architecture")

# Wait for all workstream agents to complete
```

Each agent runs in the repo directory and has access to Read, Write, Edit, Glob, Grep, Bash, WebSearch, and WebFetch tools.
