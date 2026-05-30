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
4. **Ground the domain in a REAL artifact, not the PRD's example.** PRD examples are
   idealized and hide structure. If the design touches a concrete artifact (a real
   note, file, payload, record, API response), ask the user for one real sample and
   read it. Real examples expose fields, links, edge cases, and naming hazards
   (missing sections, graph/parent wiring, unsafe characters, optional parts) the
   PRD omits — model the domain from the real thing. Skipping this is how an
   abstraction ships looking complete while quietly dropping or orphaning data.

## The rubric — load `coding-guidelines` first
Load the **coding-guidelines** skill and score every candidate against it, using its
exact terms — the complexity symptoms (change amplification · cognitive load ·
unknown unknowns), the causes (dependencies · obscurity), the deep-module bar, the
shallow-module red flags (pass-through/ping-pong, echo-wrapper, ceremony interface,
misnaming, premature generalization), naming, and "design it twice." Those
definitions live there: do NOT restate them here, apply them. Every rubric verdict
in this skill is phrased in those terms.

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

Before presenting, scrub each candidate against `coding-guidelines`' shallow-module
red flags — a candidate that pings-pongs, wraps as a pass-through, adds a ceremony
interface, or misnames a role is NOT ready to show. Catch it here, not after the
user has to.

**Forks become candidates, not questions.** When a design decision has several
defensible answers (reconcile-on-start or not; one class or two; where parallelism
lives), do NOT ask the user to resolve it in the abstract — make the three
candidates DIFFER along that fork, give a rubric verdict, and recommend one. The
user decides by picking a candidate. The ONLY things you stop to ask are the Phase 1
anchor and the Phase 2 completion gate.

**When depth is contested, decide at the call sites** (the call-site test in
`coding-guidelines`): write the real usage everywhere the abstraction would be used,
with it and without it, and let the diff expose the leak.

The user picks one; move to the next responsibility.

**Backward edges are allowed.** If designing a later module reveals an earlier DECIDED
module was wrong (overlap, leak, should merge/split), re-open it and generate a
**fresh** set of three candidates informed by the new constraint — do not reshuffle the
old ones.

**Completion is a gate.** When you judge the decomposition complete, do NOT silently
start writing. Present the **full map** and ask the user to ratify nothing is missing.
**STOP and wait.** Proceed only on sign-off.

## Phase 3 — Write the design INTO the PRD
Once the completion gate is signed off (shared understanding reached), persist the
design into the PRD issue's empty `# Design` section — that splice is the
deliverable, not a chat message. The PRD already holds Problem Statement, Solution,
User Stories, and Tech Stack (to-prd leaves `# Design` empty for you); fill ONLY the
Design section, leaving every other section byte-for-byte untouched.

Steps:
1. Compose the Design section from the DECIDED map, in the format below.
2. Fetch the current body: `gh issue view <number> --json body -q .body`.
3. Splice the composed content into the empty `# Design` section. Do not rewrite
   Problem/Solution/User Stories/Tech Stack.
4. Write it back: `gh issue edit <number> --body-file <file>`. Return the issue URL.

Design section format:

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

    ## Module Dependencies
    <the final wiring: one directed "A → B" edge per line; independent modules on
    separate lines>

Keep the design **logical** — interfaces and wiring only. Do NOT specify file/directory
layout; that is a downstream implementation decision.
