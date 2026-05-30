---
name: to-prd
description: Use when the user asks to generate a PRD. Assesses context, grills if needed, optionally explores the codebase, then creates a GitHub issue.
---

# Behavior

1. **Assess context** — read the current conversation. If the problem, solution, and at least some user stories are already clear, proceed to step 3. If context is thin, go to step 2.
2. **Grill** — load and execute the `grill-me` skill. Interview the user until problem statement, solution, user stories, and tech stack are all resolved.
3. **Optional codebase exploration** — if after grilling any section still lacks the depth needed to write it accurately (e.g. tech stack is unclear), explore the codebase. Read only what is necessary to fill the gap. Skip if context is already sufficient.
4. **Draft the PRD** — produce the full markdown using the template below. **Leave the `# Design` section empty** — it is authored later by the `deep-design` skill, which splices the module design into it. Do NOT design modules here. Show the PRD to the user and wait for explicit confirmation before creating the issue.
5. **Create GitHub issue** — run `gh issue create --title "<title>" --body "<prd-markdown>"`. Return the issue URL.

---

# Template

```markdown
# Problem Statement
<Describe the user's pain point. One or two paragraphs. What situation forces this problem to exist? What is the cost of not solving it?>

# Solution
<Describe the proposed solution at the system level. What components are introduced or changed? How do they interact? Keep it high-level — implementation detail belongs in Design.>

# User Stories

Given <precondition>
When <action>
[And <additional action>]
Then <observable outcome>
[And <additional outcome>]

# Design

<Leave this section empty. The `deep-design` skill authors it later — designing the
deep modules one at a time with the user, then splicing the module design and a
`## Module Dependencies` subsection into this section. Do NOT design modules in the PRD.>

---

# Tech Stack

- **Languages:** <e.g. Python 3.12, TypeScript 5>
- **Frameworks:** <e.g. FastAPI, React, Bubbletea>
- **Storage:** <e.g. SQLite, PostgreSQL, S3>
- **Infrastructure:** <e.g. systemd --user services, Docker, AWS Lambda>
- **Deployment:** <e.g. self-hosted on user machine, Fly.io, GitHub Actions CI>
```
