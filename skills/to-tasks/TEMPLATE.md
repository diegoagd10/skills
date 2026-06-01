# Task List Schema

The writer produces `tasks.json` in EXACTLY this shape. The downstream `to-implementation` skill
consumes it, so the structure below is a contract — do not add, rename, or drop fields.

`tasks.json` is a JSON array of **main tasks**. Each main task has:

- `id` — `<stamp>-<N>` (see the id rules in `AUTHORING.md`).
- `name` — the phase heading (e.g. `Setup`, `Core Implementation`).
- `subtasks` — an array of subtasks, in dependency order.

Each **subtask** has:

- `id` — `<stamp>-<X>.<Y>`.
- `name` — a verifiable description of one unit of work.
- `completed` — always `false` when the list is created.

A main task carries NO `completed` field of its own — it is done when ALL its subtasks are
completed (derived by the implementer, never stored, so there is one source of truth).

Array order is dependency order: `to-implementation` always takes the FIRST main task with an
incomplete subtask and never skips ahead.

```json
[
  {
    "id": "20260530-154412-1",
    "name": "Setup",
    "subtasks": [
      { "id": "20260530-154412-1.1", "name": "Create new module structure", "completed": false },
      { "id": "20260530-154412-1.2", "name": "Add dependencies to package.json", "completed": false }
    ]
  },
  {
    "id": "20260530-154412-2",
    "name": "Core Implementation",
    "subtasks": [
      { "id": "20260530-154412-2.1", "name": "Implement data export function", "completed": false },
      { "id": "20260530-154412-2.2", "name": "Add CSV formatting utilities", "completed": false }
    ]
  }
]
```

The same list, in the markdown form you reason about before serializing (DO NOT save this form —
save the JSON above):

```
## 1. Setup

- [ ] 1.1 Create new module structure
- [ ] 1.2 Add dependencies to package.json

## 2. Core Implementation

- [ ] 2.1 Implement data export function
- [ ] 2.2 Add CSV formatting utilities
```
