# Authoring an Implementation Task List

This guide is read by the **writer** during the `to-tasks` loop. It defines the breakdown
METHOD — how to turn a PRD and a system design into a dependency-ordered, grouped checklist of
implementation work. Paths, the write→validate loop, and when the list is "done" are handled by
the orchestrator; your job is the breakdown itself.

The PRD says WHAT to build and for whom; the design says HOW. You produce the ordered checklist
someone can execute. Derive the tasks from THESE TWO DOCUMENTS ONLY — invent nothing neither
justifies.

## Method

1. **Read the PRD** — extract every requirement / user story. These are the things the finished
   work MUST achieve. They are your coverage checklist: each one has to be satisfied by at least
   one subtask, or the list is incomplete.
2. **Read the design** — the design says how each requirement is built: the modules, the
   dependency graph, the data flow, the storage, the testing strategy, and (if present) the
   `Implementation Order` / `Module Dependencies` section. The design's build order is your
   primary source for sequencing; reading it wrong is how tasks end up out of order.
3. **Map requirements to work** — for each PRD requirement, identify the design pieces that
   implement it. Every subtask must trace back to the design (HOW) and forward to a PRD
   requirement (WHY). A task that traces to neither is invented work — drop it.
4. **Group into main tasks** — cluster related work under numbered MAIN tasks (e.g. `Setup`,
   `Repository`, `Core service`, `Edge / UI`, `Integration tests`). A main task is a phase of the
   build, not a single action.
5. **Order by dependency** — array order IS the dependency order; the implementer never skips
   ahead. Models and infra first, then the repository, then the service, then navigators, then
   read-only edge components, then mutation flows, then integration tests. Nothing may depend on a
   task that comes later. When the design has an `Implementation Order` section, follow it.
6. **Size the subtasks** — each subtask is one unit of work, small enough to finish in one
   session, and verifiable (you know when it is done). Break anything larger into multiple
   subtasks.
7. **Fill the template** — emit the list in the exact JSON shape of `TEMPLATE.md` (in this
   directory) and write it to the tasks path. `EXAMPLE.md` shows the expected depth.

## Coverage is the whole point

The validator's first job is traceability: every PRD requirement must be reachable through the
tasks. Before you finish, walk the PRD requirement by requirement and confirm each one is covered
by a subtask. A list that builds a beautiful subset of the PRD still fails. Conversely, a subtask
that no PRD requirement needs is scope creep — remove it.

## Granularity rules

- Every unit of work MUST be a **subtask** (`X.Y`). Progress is tracked by the `completed` boolean
  on each subtask — anything not expressed as a subtask is NOT tracked and effectively does not
  exist for the implementer.
- A main task carries NO `completed` field. It is done when ALL its subtasks are completed
  (derived, never stored — one source of truth).
- Subtasks should be verifiable: prefer "Implement `KanbanRepository.create_task`" over "Work on
  the repository".
- Do not split a single trivial edit into ceremony subtasks, and do not bundle three unrelated
  changes into one. One coherent, completable unit per subtask.

## The `id` — date-time plus sequence

Capture the current date-time ONCE for the whole file with `date +%Y%m%d-%H%M%S` (e.g.
`20260530-154412`); use that same stamp for every id so the list is stamped with its creation
time. Append a sequence so ids are unique within the file:

- **Main task** `N` → `<stamp>-<N>` (e.g. `20260530-154412-2`).
- **Subtask** `X.Y` → `<stamp>-<X>.<Y>` (e.g. `20260530-154412-2.1`), where `X` is its main
  task's number.

A plain timestamp is NOT unique — the whole file is written in the same second — so the sequence
suffix is what makes each id addressable. When REVISING an existing list, keep the ids already
present stable; only mint new ids (reusing the file's existing stamp) for genuinely new tasks.

## Not negotiable

1. Break down ONLY what the PRD requires and the design specifies — invent neither requirements
   nor architecture.
2. Every unit of work is a **subtask** with `completed: false` — never a bare main task.
3. Array order encodes dependencies — never place a task before something it depends on.
4. Every PRD requirement is covered by at least one subtask.
