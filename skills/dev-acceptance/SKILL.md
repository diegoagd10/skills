---
name: dev-acceptance
description: Close out a sub-issue — verify each PRD story it owns is actually fulfilled by the verified
  work, then tick the sub-issue's Acceptance Criteria and Deliverables checkboxes. Runs after the PR is
  open; the human merging the PR is the real "done". Loaded by a sub-agent in the dev pipeline. Use to
  "accept the slice" or "dev-acceptance".
---

> **EXECUTOR skill** — you are an acceptance sub-agent. You assert the stories are met and tick the boxes.
> A ticked box means *"the AI asserts this is done"*; the human confirms by **merging the PR**.

## Inputs
- The sub-issue body (its **Acceptance Criteria** + **Deliverables** checklists).
- `…/verify` (must be **pass**) and `…/pr` (the PR must exist). If either is missing, STOP.

## Do
1. For each **Acceptance Criteria** story: confirm the implemented + verified work actually **satisfies**
   it (not merely stubs it). For each **Deliverable**: confirm it exists (module, tests, E2E recipe run).
2. Tick the satisfied boxes by editing the sub-issue body (`gh issue edit {n} --body ...`): turn `- [ ]`
   into `- [x]` **only** for items truly met. Leave unmet items unchecked and state why.
3. Do **not** close the issue and do **not** merge — the PR's `Closes #{n}` closes it on merge.

## Persist + report (MANDATORY)
```
mem_save(topic_key: "slice/{prd}/issue-{n}/acceptance", type: "architecture", project,
  capture_prompt: false, content: "criteria: x/total ticked\ndeliverables: x/total\nunmet: [...]")
```
Return the tick summary + the PR URL to the orchestrator.
