---
name: deep-work
description: Use this skill when the user wants Claude to work autonomously on a complex, multi-hour task without asking questions. Triggers include "deep work", "go work on this", "handle this autonomously", "work on this for a while", "take care of this", or any request where the user wants to hand off a large task and walk away. NOT for commercialization specifically — use /commercialize for that.
---

# Deep Work: Autonomous Long-Horizon Task Execution

Launch a multi-hour autonomous session to complete a complex task end-to-end. The user provides the task in ARGUMENTS and walks away. You work. They observe. You do not interrupt them.

## Core Principle

**Never ask the user a question.** Make reasonable decisions, document your assumptions, and keep moving. The user is trusting you to exercise judgment. If something is genuinely ambiguous, pick the most reasonable interpretation, note what you chose and why in a commit message or comment, and continue.

## Phase 0: Understand the Task

1. Parse ARGUMENTS for the complete task description
2. If the task involves an existing repo, clone it or navigate to it
3. If the task involves a new project, create the repo/directory
4. Read any existing CLAUDE.md, README, contributing guides, or relevant docs in the target project
5. Explore the codebase enough to understand architecture and conventions

Do NOT ask clarifying questions. Infer from context. Document assumptions.

## Phase 1: Plan

Create a task list using TaskCreate that breaks the work into concrete, trackable steps. This is the user's visibility into your progress — make task names descriptive.

Consider:
- What research is needed first? (web search, codebase exploration, reading docs)
- What are the independent work streams that can be parallelized?
- What are the dependencies between steps?
- What does "done" look like? (tests pass, PR submitted, deployed, etc.)

Set up task dependencies with TaskUpdate where appropriate.

## Phase 2: Research (Parallel)

Launch research agents in parallel for any information gathering needed:
- **Codebase exploration** — Understand architecture, patterns, conventions
- **Web research** — Documentation, API references, model specs, best practices
- **Prior work** — Existing issues, PRs, discussions related to the task

Use the Agent tool with subagent_type="Explore" for codebase research and general-purpose agents for web research. Run them in parallel.

## Phase 3: Execute

Work through the task list systematically:
- Mark each task as `in_progress` before starting, `completed` when done
- Use parallel agents for independent work streams
- Follow the target project's conventions (code style, testing patterns, commit style)
- Write tests where appropriate (TDD when it makes sense)
- Commit after each meaningful milestone — don't accumulate a massive uncommitted diff

### Decision-Making Framework

When you face a choice:
1. **Check project conventions** — Does the codebase already do something similar? Follow that pattern.
2. **Check docs/contributing guide** — Is there a stated preference?
3. **Pick the simpler option** — When genuinely ambiguous, simpler is usually better.
4. **Document the choice** — Brief comment in code or commit message explaining why.

## Phase 4: Verify

Before considering the task complete:
- Run the project's test suite if one exists
- Run linters/formatters if configured
- Self-review all changes: read through every modified file looking for bugs, typos, missing edge cases
- Verify the changes actually accomplish what was asked
- If the task involves a PR, double-check the diff against the task requirements

## Phase 5: Deliver

Deliver the work in whatever form the task requires:
- **PR**: Create a well-documented PR with clear title, summary, and test plan. Follow the user's PR protocol (feature branch, request reviews, etc.)
- **Local changes**: Commit with clear messages
- **Documentation**: Ensure README/docs are updated if behavior changed
- **Handoff**: If more work remains beyond what was asked, note it in the PR description or a comment

## Progress & Context Management

- **Task tracking**: Update task status continuously so the user can see progress
- **Frequent commits**: Commit after each phase or major milestone, not just at the end
- **Handoff notes**: If context limits approach, immediately save `~/.claude/handoff.md` with:
  - What was accomplished
  - What's in progress (with branch names, file paths)
  - What remains to be done
  - Exact commands to resume

## Autonomy Guidelines

- **Bias toward action**: Don't deliberate when you can just do it
- **Don't over-engineer**: Do what was asked, not what you think should also be done
- **Parallelize aggressively**: Use multiple agents for independent work streams
- **Web research is cheap**: When unsure about an API, model architecture, or library — search, don't guess
- **Quality matters**: This is autonomous, not rushed. Review your own work carefully.
- **Stay on task**: Don't wander into tangential improvements. Do the thing that was asked.
- **Git safety**: Follow the user's git protocols (branches, PRs, no force-push, etc.)
