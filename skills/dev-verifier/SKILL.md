---
name: dev-verifier
description: The quality gate for an implemented sub-issue — runs the linter, enforces ≥95% TOTAL test
  coverage, and checks design-fidelity (the public interface hides what the spec says it must; the code
  matches the design scope). Writes a pass/fail verdict the bounded retry loop reads. Loaded by a sub-agent
  in the dev pipeline. Use to "verify the slice" or "dev-verifier".
---

> **EXECUTOR skill** — you are a verification sub-agent. You run checks and write a verdict; you do **not**
> fix code (the orchestrator routes failures back to `tdd-implement` retry mode).

## Inputs
- `slice/{prd}/testing-capabilities` (the lint + coverage commands).
- `…/plan` and each `…/class-{C}/spec` (the `hides` obligations), the sub-issue's **## Design (scope)**,
  and `…/integration`.

## Checks — run all three; the verdict is FAIL if ANY fails
1. **Lint** — run the repo's linter clean (e.g. ruff). Report every violation.
2. **Coverage** — run the suite with coverage; require **≥95% TOTAL** (whole-project, not per-file).
   Report the number.
3. **Design-fidelity** — *the check that was historically the real gap.* For each class, confirm its
   **public interface hides** what its spec says it hides — no backing store / connection / encoding /
   SQLite leaking into public signatures — and that the implemented surface matches the sub-issue's
   design scope. Report any leak as `file:symbol`.

## Verdict (MANDATORY)
```
mem_save(topic_key: "slice/{prd}/issue-{n}/verify", type: "architecture", project, capture_prompt: false,
  content: "lint: pass/fail (...)\ncoverage: NN% (>=95? y/n)\nfidelity: pass/fail (leaks: ...)\nverdict: pass|fail")
```
Return the verdict + the precise failures to the orchestrator. On `fail` it spawns a `tdd-implement`
retry sub-agent (bounded to 2 retries) and re-runs you.
