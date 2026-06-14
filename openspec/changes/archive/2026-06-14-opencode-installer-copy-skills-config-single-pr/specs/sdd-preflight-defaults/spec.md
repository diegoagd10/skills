# sdd-preflight-defaults Specification

## Purpose

Define simplified SDD session defaults: hybrid artifact persistence by policy and single-PR delivery without chained-PR prompting.

## Requirements

### Requirement: Hybrid Artifact Persistence Default

The SDD preflight MUST use hybrid artifact persistence by default. The system MUST NOT ask the user to choose Engram-only, OpenSpec/files-only, or hybrid persistence during normal SDD preflight.

#### Scenario: SDD preflight skips artifact-store prompt

- GIVEN a user starts an SDD workflow
- WHEN preflight runs
- THEN the workflow selects hybrid artifact persistence without asking an artifact-store question

#### Scenario: Downstream phases receive canonical mode

- GIVEN preflight selected persistence defaults
- WHEN an SDD phase is launched
- THEN the phase receives `hybrid` as the artifact store mode

### Requirement: Single-PR Delivery Policy

The SDD workflow MUST use single-PR delivery for changes. The system MUST NOT ask the user to choose chained PR, large PR, or PR-splitting strategies during normal preflight.

#### Scenario: SDD preflight skips PR-chain prompt

- GIVEN a user starts an SDD workflow
- WHEN preflight runs
- THEN the workflow proceeds with single-PR delivery without asking a PR-chain strategy question

#### Scenario: Review budget remains visible

- GIVEN a change exceeds or approaches the configured review budget
- WHEN SDD guidance reports delivery risk
- THEN it communicates review-size risk without recommending a chained PR flow

### Requirement: Removed Legacy Choice Language

The SDD prompts and shared phase contracts MUST remove user-facing language that instructs users or agents to choose artifact-store modes or chained PR strategies.

#### Scenario: Prompt text has no obsolete artifact-store options

- GIVEN SDD prompt and shared contract artifacts are inspected
- WHEN the preflight instructions are read
- THEN they do not present Engram/files/hybrid as a user decision

#### Scenario: Prompt text has no chained-PR decision flow

- GIVEN SDD prompt and shared contract artifacts are inspected
- WHEN delivery instructions are read
- THEN they do not present chained PR selection or large-PR decision flow as a preflight choice
