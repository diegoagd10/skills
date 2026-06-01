# <Feature / System Name>

## Problem Statement

<Describe the user's pain point in one or two paragraphs. What situation forces this problem to
exist? Who feels it, and when? What is the cost of NOT solving it? Stay concrete — name the real
friction, not a generic "users want X". Do not propose a solution here.>

## Solution

<Describe the proposed solution at the SYSTEM level. What capabilities are introduced or changed, and
how do the major pieces interact at a high level? Keep it to WHAT the system does and WHY — leave
class names, schemas, and algorithms to the design. A reader should finish this section understanding
the shape of the solution without seeing any implementation detail.>

## User Stories

<One block per story. Cover every capability the brief justifies — each story must be observably
testable (someone could write a test that passes only when the outcome holds). Use the Given/When/Then
form below; add `And` lines as needed.>

Given <precondition>
When <action>
[And <additional action>]
Then <observable outcome>
[And <additional outcome>]

Given <precondition>
When <action>
Then <observable outcome>

## Tech Stack

<List only what is true of THIS project. If the codebase already fixes a choice, state it; if the
brief leaves something open, state the chosen option and why. No speculative "maybe" entries.>

- **Languages:** <e.g. Python 3.12, TypeScript 5>
- **Frameworks:** <e.g. FastAPI, React, Bubbletea, Textual>
- **Storage:** <e.g. SQLite, PostgreSQL, S3>
- **Infrastructure:** <e.g. systemd --user services, Docker, AWS Lambda>
- **Deployment:** <e.g. self-hosted on user machine, Fly.io, GitHub Actions CI>
