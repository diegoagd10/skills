# Personal Kanban TUI

> Worked example for the `to-prd` skill. It shows the `TEMPLATE.md` sections filled in for a real
> feature — how the problem is made concrete, how the solution stays at the system level (no module
> names or schemas), and how each capability becomes a testable Given/When/Then story. This is the same
> feature `to-design`'s `EXAMPLE.md` turns into a system design, so reading both shows the PRD→design
> handoff.

## Problem Statement

A solo developer juggling several side projects has no lightweight way to track work without leaving the
terminal. General task apps are web-based, sync-driven, and account-bound; they pull focus out of the
shell and bury a handful of tasks under collaboration features that a single user never touches. The
result is that personal projects drift: tasks live in scattered notes, half-remembered, with no clear
"what's next" and no record of what was finished.

The cost of not solving this is lost momentum. Without a fast, local board the developer either adopts a
heavyweight tool they resent and abandon, or tracks nothing and loses the thread between sessions.

## Solution

A local-first, single-user terminal application that manages personal projects on a fixed kanban
workflow. The user creates projects, and within a selected project creates tasks that move one step at a
time across a small set of workflow columns until they are done. Completed tasks can be archived out of
the active board into a separate archive the user can browse and prune later. All data is stored locally
on the user's machine so the app works offline and owns no account.

The system presents three high-level areas that share the same data: a project area for choosing and
managing projects, a board area for moving a project's tasks through the workflow, and an archive area
for reviewing finished work. Filtering helps the user find a project or an archived task by name, and any
permanent deletion is gated behind an explicit confirmation so nothing is destroyed by accident.

## User Stories

Given the app is open
When the user creates a project with a name and description
Then the project is saved and can be selected from the project list

Given several projects exist
When the user types a substring into the project filter
Then only projects whose name contains that substring (case-insensitive) are shown

Given a project is selected
When the user creates a task with a title, description, complexity, and importance/urgency flags
Then the task appears in the first workflow column of that project's board

Given a task is on the board
When the user moves it one column to the right or left
Then the task changes to the adjacent workflow status and never skips a column

Given a task has reached the final workflow column
When the user archives it
Then the task leaves the active board and appears in the archive

Given a task has not reached the final column
When the user attempts to archive it
Then the action is rejected and the task stays on the board

Given archived tasks exist
When the user opens the archive and filters by name
Then only archived tasks whose title matches the filter (case-insensitive) are shown

Given the user requests deletion of a project, task, or archived task
When the user is asked to confirm by typing the exact name
Then the item is permanently deleted only if the typed text matches exactly, and the deletion is cancelled otherwise

Given the user reopens the app later
When the app starts
Then all previously saved projects, tasks, and archived tasks are present

## Tech Stack

- **Languages:** Python 3.12
- **Frameworks:** Textual (terminal UI)
- **Storage:** SQLite in a local application data directory
- **Infrastructure:** runs locally on the user's machine; no network services
- **Deployment:** self-hosted — launched as a CLI on the user's machine
