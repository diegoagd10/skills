---
name: dev-pr
description: Deliver an implemented, verified sub-issue as a pull request — create a branch, commit with a
  conventional message, push, and open a PR linking the sub-issue. NEVER merges and never pushes to the
  default branch (the PR is the human's verification point). Loaded by a sub-agent in the dev pipeline.
  Use to "open the PR for the slice" or "dev-pr".
---

> **EXECUTOR skill** — you are a delivery sub-agent. You package the work as a PR. You **NEVER merge** and
> you **never push to the default branch**.

## Precondition
Run only after `slice/{prd}/issue-{n}/verify` is **pass**. If it is not, STOP.

## Do
1. **Branch** off the default branch — name it for the sub-issue, e.g. `feat/issue-{n}-<slug>`.
2. **Commit** the slice's changes with a **conventional commit** message (`feat:` / `fix:` / `refactor:`
   …). Do **not** add AI attribution or `Co-Authored-By` lines.
3. **Push** the branch.
4. **Open the PR** (`gh pr create`): the body summarizes the capability, lists the implemented classes,
   and links the sub-issue with **`Closes #{n}`**. Target = the default branch. **Do not merge.**

## Persist + report (MANDATORY)
```
mem_save(topic_key: "slice/{prd}/issue-{n}/pr", type: "architecture", project, capture_prompt: false,
  content: "branch: ...\ncommit: ...\npr_url: ...")
```
Return the PR URL to the orchestrator.
