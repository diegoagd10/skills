---
name: tdd-implement
description: Implement one class of a slice with strict red→green→refactor TDD and APoSD-quality
  comments, reading its spec from engram and writing its result back. Language-agnostic — reads
  the repo's testing capabilities rather than assuming a stack. Has an integration mode that
  wires a slice's classes and runs the full suite. Invoked by a sub-agent during the dev-orchestrator pipeline.
---

> **EXECUTOR skill.** You are a sub-agent loading this to do the implement stage of the dev-orchestrator
> pipeline. If you are the orchestrator, STOP and delegate this instead.

## Load first
- **Injected skills:** if your prompt has a `## Skills to load before work` block, read those
  exact `SKILL.md` files first (e.g. a language testing skill) and apply them. Report your
  `skill_resolution` status when you return.
- **Testing capabilities:** `mem_search("slice/{prd}/testing-capabilities", project)` → id ;
  `mem_get_observation(id)`. Use the recorded language, test runner, and conventions. If absent,
  detect from the repo (pyproject.toml+pytest → Python; go.mod → Go; package.json → JS/TS).

---

## Class mode (default)
Input: `slice/{prd}/issue-{n}/class-{Class}/spec` (interface, **hides**, status, ordered tests).

**TDD — strict and leaf-first inside the class:**
1. **Red** — write the next failing test from the ordered list. Run it; confirm it fails.
2. **Green** — minimal code to pass. Run; confirm green.
3. **Refactor** — clean up with tests green. Repeat for each test.
Honor `hides`: the deep-module obligation. Implementation detail must NOT leak into the public
interface (no backing store / connection / encoding in public signatures).

**Comments — APoSD ch. 13, baked in (not a later pass):**
- Combat **obscurity**: comment only what is NOT obvious from the code; never restate it.
- **Interface docstring = WHAT** (the abstraction the caller needs). Never name the storage,
  mechanism, or test-role in it — that re-leaks what the module exists to hide.
- **Implementation comments = HOW**, inside the method body, next to the non-obvious step.
- **Constants/enums**: comment at the declaration with units / valid range / why, so the IDE
  hover shows it at every call site.

Persist (MANDATORY):
```
mem_save(title/topic_key: "slice/{prd}/issue-{n}/class-{Class}/impl", type: "architecture",
  project, capture_prompt: false, content: "files: [...]\ntests_added: [...]\nstatus: green|blocked\nnotes/deviation: ...")
```

---

## Integration mode
Triggered when the orchestrator says "integration mode for issue {n}".
1. Read every `slice/{prd}/issue-{n}/class-*/impl`.
2. Wire the classes per the plan (entrypoints, dependency injection).
3. Run the **full** test suite (per testing-capabilities). Then run the slice's **E2E recipe**
   from the sub-issue's Deliverables.
Persist (MANDATORY):
```
mem_save(title/topic_key: "slice/{prd}/issue-{n}/integration", type: "architecture",
  project, capture_prompt: false, content: "suite: pass/fail + counts\ne2e: steps run + outcome\nexit_code: ...")
```

---

## Retry mode
If the orchestrator passes a failing verdict key (`slice/{prd}/issue-{n}/verify` from dev-verifier),
read it first, fix exactly what it reports (lint / coverage / design-fidelity), keep the suite green,
then re-persist your `impl`/`integration` artifact. Report back: the key you wrote + green/blocked.
