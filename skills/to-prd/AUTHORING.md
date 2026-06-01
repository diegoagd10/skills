# Authoring a Product Requirements Document

This guide is read by the **writer** during the `to-prd` loop. It defines the PRD METHOD — how to turn
the user's captured requirements into a PRD that says WHAT to build and WHY, without drifting into HOW.
Paths, the write→validate loop, and when the PRD is "done" are handled by the orchestrator; your job is
the PRD itself.

## Method

1. **Read the requirements brief** — it is the CONTRACT. Derive the problem, the solution shape, the
   user stories, and the tech stack from it, not from assumptions. Never invent a requirement the brief
   does not justify, and never drop one it states.
2. **State the problem before the solution** — name the real friction: who feels it, when, and what the
   cost of leaving it unsolved is. A PRD that opens with the solution has skipped its most important
   job. Do not smuggle solution detail into this section.
3. **Describe the solution at the system level** — what capabilities appear or change, and how the
   major pieces interact at a high level. Stop at the boundary where design begins: no class names, no
   schemas, no algorithms, no file layout. If you are naming a method, you have gone too deep.
4. **Write observable user stories** — one Given/When/Then block per capability the brief justifies.
   Each story must be testable: the `Then` is an outcome someone could assert against. Cover every
   requirement in the brief with at least one story.
5. **Pin the tech stack** — record only what is true of this project. Where the codebase already fixes
   a choice, state it; where the brief leaves it open, choose and say why. No speculative entries.
6. **Fill the template** — fill in every section of `TEMPLATE.md` (in this directory).

## What makes a good PRD (the validator enforces it)

- **Complete coverage, zero invention.** Every requirement in the brief is reflected in the PRD; the
  PRD adds nothing the brief does not justify. This is the validator's primary check.
- **Right altitude.** The PRD is WHAT and WHY. The moment it specifies HOW (modules, schemas, code
  structure), it is doing the design's job — that is a defect, not thoroughness.
- **Testable stories.** Given/When/Then with observable outcomes. "The system is fast" is not a story;
  "Given N items, when the user filters, then matching items appear" is.
- **Grounded problem.** The problem statement describes real pain and the cost of inaction, not a
  generic desire.
- **Concrete stack.** The tech stack reflects the codebase and the brief, not a guess.

## Authoring notes

- Follow `TEMPLATE.md` for the section structure and the guidance in each placeholder.
- Read `EXAMPLE.md` (the Personal Kanban TUI) for the expected depth and tone — how the problem is made
  concrete, how the solution stays at the system level, and how each capability becomes a testable
  story. That example is the same feature `to-design`'s example designs, so it shows the PRD→design
  handoff.
- Keep the solution section honest about scope: if the brief defers something, the PRD may note it as
  out of scope, but it must not quietly expand scope.

## Not negotiable

1. Write only what the requirements brief justifies — do not invent requirements.
2. Do not specify implementation detail — keep the PRD at the WHAT/WHY altitude. If you cannot describe
   the solution without naming classes or schemas, you are writing the design, not the PRD.
