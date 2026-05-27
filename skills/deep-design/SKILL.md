---
name: deep-design
description: Turn a GitHub-issue PRD into a software design. Designs deep modules from
  user stories by proposing 3 interface candidates each and choosing via the "A Philosophy
  of Software Design" complexity rubric. Use when the user wants to design from a PRD,
  design deep modules, or mentions "deep-design".
---

Turn a PRD into a deep-module software design, one abstraction at a time, using
*A Philosophy of Software Design* as the evaluation rubric.

## Input
1. The user gives a GitHub issue **number** (assumes the current repo) or an issue
   **URL**. Fetch it: `gh issue view <number-or-url> --json title,body`.
2. **User stories are the hard floor.** If the PRD has no user stories, STOP and tell
   the user to add them. Never invent stories.
3. **Codebase is optional.** By default, design from the PRD text alone. If the user
   opts in ("also read the repo" / "brownfield"), read the existing code too; every
   module in the map then carries a status: `KEEP` (exists, unchanged),
   `CHANGE` (exists, must change), or `BUILD` (new).

## The rubric — use these exact terms everywhere
- **Symptoms of complexity** (score every candidate on all three):
  - **Change amplification** — one logical change forces edits in many places.
  - **Cognitive load** — how much you must hold in your head to use it.
  - **Unknown unknowns** — what you must know to use it correctly but can't tell you
    need to know. (The worst symptom.)
- **Causes of complexity**:
  - **Dependencies** — a piece can't be understood or changed in isolation.
  - **Obscurity** — important information isn't obvious.
- **Deep-module bar** — a good abstraction has a *simple interface* and *large
  functionality*, hiding implementation (a balanced tree exposes `insert/get/delete`
  and hides rebalancing). Reject shallow modules whose interface is nearly as complex
  as their implementation.
- **Design it twice — here, thrice.** Never commit to the first interface.

## Phase 1 — The most important thing  (GATE)
From the user stories, identify the single most important thing: the problem whose
solution dissolves the most other problems, or the information most modules need.
State it in ONE sentence and ask the user to confirm or correct it. **STOP and wait.**
Everything downstream derives from this anchor — never proceed on a wrong one.

## Phase 2 — Abstractions, one at a time
Reason about the full decomposition **silently** (do not dump your thinking), but keep
a **visible running map** the user can always see:

    DECIDED
      1. <name> -> candidate #n  (one-line summary)
    OPEN
      2. <name>   <- active now
      3. ...

Work one responsibility at a time. For the active one, present **three candidate
abstractions**, each with:
- **Justification** — why this abstraction exists
- **Exposed** — the important details the consumer sees (its interface)
- **Hidden** — the implementation details kept out
- **Leverage** — how many subproblems / use cases it solves
- **Pros / cons** — stated in rubric terms (change amplification · cognitive load ·
  unknown unknowns · dependencies · obscurity)

The user picks one; move to the next responsibility.

**Backward edges are allowed.** If designing a later module reveals an earlier DECIDED
module was wrong (overlap, leak, should merge/split), re-open it and generate a
**fresh** set of three candidates informed by the new constraint — do not reshuffle the
old ones.

**Completion is a gate.** When you judge the decomposition complete, do NOT silently
start writing. Present the **full map** and ask the user to ratify nothing is missing.
**STOP and wait.** Proceed only on sign-off.

## Phase 3 — Write the design
Emit the design as your final output, in this template. It is the user's to save — do
not write files or post comments.

    # Problem
    <what is being solved — the Phase 1 anchor>

    # Solution
    <high-level: the key abstractions and the details that solve most of the problems>

    # Design
    ## <Abstraction>
    - **Methods (exposed):** ...
    - **Hidden:** ...
    - **Why chosen:** <in rubric terms>
    - **Use cases (leverage):** ...
    ### Rejected
    - Candidate B — lost on {e.g. obscurity, dependencies}
    - Candidate C — lost on {e.g. cognitive load}
    (repeat ## per abstraction)

    # Dependencies
    <the final wiring: which module depends on which>

Keep the design **logical** — interfaces and wiring only. Do NOT specify file/directory
layout; that is a downstream implementation decision.
