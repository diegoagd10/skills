---
name: to-prd
description: Use when the user asks to generate a PRD. Assesses context, grills if needed, optionally explores the codebase, then creates a GitHub issue.
---

# Behavior

1. **Assess context** — read the current conversation. If the problem, solution, and at least some user stories are already clear, proceed to step 3. If context is thin, go to step 2.
2. **Grill** — load and execute the `grill-me` skill. Interview the user until problem statement, solution, user stories, keystone business/technical concepts, deep module design, and tech stack are all resolved.
3. **Optional codebase exploration** — if after grilling any section still lacks the depth needed to write it accurately (e.g. tech stack is unclear, module boundaries are ambiguous), explore the codebase. Read only what is necessary to fill the gap. Skip if context is already sufficient.
4. **Draft the PRD** — read `skills/coding-guidelines/SKILL.md` to load the definitions of Deep Module, Important, Unimportant, and complexity symptoms before filling in the Design section. Produce the full markdown using the template below. Show it to the user and wait for explicit confirmation before creating the issue.
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

# Common Business Knowledge
- <Keystone domain concept>: <one-line definition — the concept that, once understood, collapses the most other business ambiguities>
- <Repeat for each keystone concept only>

# Common Technical Knowledge
- <Keystone technical concept>: <one-line definition — the decision or abstraction that, once made, solves the most other technical problems>
- <Repeat for each keystone concept only>

# Design

## Deep Module: <ModuleName>

**Class:** `ClassName`

**Important:** <Only what a caller NEEDS to construct and use this class correctly — what it represents, what it guarantees, and what the caller must account for. NEVER describe internal routing, which private methods are called, or how deps flow internally.>
**Unimportant:** <Everything the class hides — internal state machines, routing decisions, which private methods or external calls it uses, how deps are threaded to collaborators. If the caller doesn't need to know it to USE the class correctly, it belongs here.>

> Filter rule: if removing a sentence from Important would not change how a caller constructs or uses this class, it belongs in Unimportant.

**Decision:**
| Option | Benefit | Con |
|--------|---------|-----|
| <Option A — alternative design considered> | <why it was attractive> | <why it was rejected> |
| **<Option B — chosen approach>** | <what makes it better> | <its tradeoff> |

Chosen because: <one sentence grounded in the APoSD complexity rubric — simpler interface, less information leakage, fewer dependencies, or lower cognitive load>

### `method_name(param_name: ParamType, ...) -> ReturnType`

**Important:** <Only what a caller NEEDS to use this correctly — parameters and their constraints, return value and what it means, postconditions and side effects the caller must account for. NEVER describe how the method works internally.>
**Unimportant:** <How the method achieves its contract — algorithms, internal calls, branching, I/O mechanics. If the caller doesn't need to know it to USE the method correctly, it belongs here.>

> Filter rule: if removing a sentence from Important would not change how a caller uses the method, it belongs in Unimportant. Only include lifecycle or framework methods that callers invoke directly; skip internal hooks.

**Decision:**
| Option | Benefit | Con |
|--------|---------|-----|
| <Option A — alternative signature or behavior> | <why it was attractive> | <why it was rejected> |
| **<Option B — chosen approach>** | <what makes it better> | <its tradeoff> |

Chosen because: <one sentence grounded in the APoSD complexity rubric>

<Repeat ### method block for each method of this class>

---
<Repeat ## Deep Module block for each module>

## Module Dependencies

```
<ModuleA> → <ModuleB> → <ModuleC>
```

List every directed dependency edge between the Deep Modules above. Each arrow means "depends on / calls". One line per root chain; branch with indentation if a module has multiple dependencies. Example:

```
NoteAssistantApp → SetupOrchestrator → ServiceManagement
```

If two modules are independent (no shared dependency), list them on separate lines.

---

# Tech Stack

- **Languages:** <e.g. Python 3.12, TypeScript 5>
- **Frameworks:** <e.g. FastAPI, React, Bubbletea>
- **Storage:** <e.g. SQLite, PostgreSQL, S3>
- **Infrastructure:** <e.g. systemd --user services, Docker, AWS Lambda>
- **Deployment:** <e.g. self-hosted on user machine, Fly.io, GitHub Actions CI>
```
