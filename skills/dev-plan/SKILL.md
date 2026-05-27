---
name: dev-plan
description: Turn one sub-issue's design-scope plus the explorer's facts into an executable TDD plan — a
  per-class spec (interface, hides, status, ORDERED tests), a sequential/parallel class graph, and an
  integration plan. Also detects testing-capabilities once per PRD. SELECTS classes from the design;
  never invents architecture. Loaded by a sub-agent in the dev pipeline. Use to "plan the slice" or
  "dev-plan".
---

> **EXECUTOR skill** — you are a planning sub-agent. You SELECT and SEQUENCE; you do **not** design new
> abstractions (the sub-issue's design scope already did) and you do **not** write production code.

## Inputs
- The sub-issue's **## Design (scope)** — the classes/modules + their methods + status (builds/changes/
  stubs).
- `mem_get_observation` of `slice/{prd}/issue-{n}/exploration` (the explorer's facts).

## Step A — testing-capabilities (idempotent, PRD-scoped)
`mem_search("slice/{prd}/testing-capabilities")`. **If present, reuse it.** If absent, detect from the
repo (pyproject.toml + pytest → Python/pytest; go.mod → Go; package.json → JS/TS) and save:
```
mem_save(topic_key: "slice/{prd}/testing-capabilities", type: "config", project, capture_prompt: false,
  content: "language: ...\nrunner: ...\nconventions: ...\ncoverage_cmd: ...\nlint_cmd: ...")
```
You need this to order tests idiomatically — that is *why* the planner owns it, not the explorer.

## Step B — per-class spec (one per class in scope)
For each class, derive and persist a spec `tdd-implement` (class mode) can execute directly:
- **interface** — the public methods (from the design scope).
- **hides** — the deep-module obligation: implementation detail that must NOT leak into the public
  interface (backing store, connection, encoding, test-role). The design scope rarely states this — you
  add it.
- **status** — builds | changes | stubs.
- **ordered tests** — the leaf-first sequence of failing tests, in the repo's test idiom.
```
mem_save(topic_key: "slice/{prd}/issue-{n}/class-{Class}/spec", type: "architecture", project,
  capture_prompt: false, content: "interface: ...\nhides: ...\nstatus: ...\nordered_tests: [...]")
```

## Step C — class graph + integration plan
From the design scope's dependencies + the explorer's facts, compute and persist:
- **parallel sets** — classes sharing no unbuilt dependency (can run concurrently).
- **blocked-by edges** — a class needing a not-yet-built class waits for it (points backward only).
- **integration plan** — how the classes wire together + the slice's E2E recipe (from the sub-issue's
  Deliverables).
```
mem_save(topic_key: "slice/{prd}/issue-{n}/plan", type: "architecture", project, capture_prompt: false,
  content: "parallel_sets: [[...],[...]]\nblocked_by: {...}\nintegration: ...\ne2e: ...")
```
Return a short summary (class list + parallel sets) to the orchestrator.
