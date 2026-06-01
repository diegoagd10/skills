# Task List Example: Personal Kanban TUI

> Worked example for the `to-tasks` skill. It is the task list derived from the Personal Kanban
> TUI design in `to-design/EXAMPLE.md`. Read it for the expected *grouping, ordering, and
> granularity* — how main tasks follow the design's `Implementation Order`, how each subtask is a
> single verifiable unit, and how dependency order is encoded purely by array position (models and
> infra first, integration tests last).

The markdown form you reason about before serializing:

```
## 1. Models & Infra

- [ ] 1.1 Define enums and entities in modules/models.py (Project, Task, ArchivedTaskRow)
- [ ] 1.2 Define value objects in modules/models.py (TaskDraft, ProjectDraft, BoardSnapshot, DeleteRequest)
- [ ] 1.3 Define domain errors in modules/errors.py (KanbanError + subclasses)
- [ ] 1.4 Implement AppPaths in infra/paths.py
- [ ] 1.5 Implement Clock in infra/clock.py

## 2. Repository

- [ ] 2.1 Implement KanbanRepository.initialize (schema + indexes)
- [ ] 2.2 Implement project CRUD and filtering queries
- [ ] 2.3 Implement task CRUD and active-task queries
- [ ] 2.4 Implement set_task_status, archive_task, and archived-task queries
- [ ] 2.5 Write KanbanRepository unit tests (schema, CRUD, filtering, archive ordering)

## 3. Core Service

- [ ] 3.1 Implement project lifecycle methods on KanbanService
- [ ] 3.2 Implement task lifecycle methods on KanbanService
- [ ] 3.3 Implement load_board with the documented priority ordering
- [ ] 3.4 Implement stepwise move_task_left/right and archive_task rules
- [ ] 3.5 Implement prepare_deletion and confirm_delete with exact-phrase validation
- [ ] 3.6 Write KanbanService unit tests (ordering, transitions, archive eligibility, clock usage, confirmation)

## 4. Board Navigator

- [ ] 4.1 Implement BoardNavigator movement and clamping
- [ ] 4.2 Implement BoardNavigator.focus capability computation
- [ ] 4.3 Write BoardNavigator unit tests (row preservation, clamping, empty columns, capabilities)

## 5. Read-only Screens

- [ ] 5.1 Build WelcomeScreen and ProjectPickerScreen on KanbanRepository
- [ ] 5.2 Build ArchiveScreen with case-insensitive filtering

## 6. Board & Task Flows

- [ ] 6.1 Build KanbanBoardScreen wired to KanbanService and BoardNavigator
- [ ] 6.2 Build ProjectFormScreen and TaskFormScreen submitting drafts
- [ ] 6.3 Build TaskDetailScreen (read-only)
- [ ] 6.4 Build ConfirmDeleteScreen and wire prepare_deletion/confirm_delete flows

## 7. Integration

- [ ] 7.1 Wire main.py and PersonalKanbanApp composition
- [ ] 7.2 Add integration tests for the main user stories
```

The same list, serialized as `tasks.json` (this is what you SAVE):

```json
[
  {
    "id": "20260530-154412-1",
    "name": "Models & Infra",
    "subtasks": [
      { "id": "20260530-154412-1.1", "name": "Define enums and entities in modules/models.py (Project, Task, ArchivedTaskRow)", "completed": false },
      { "id": "20260530-154412-1.2", "name": "Define value objects in modules/models.py (TaskDraft, ProjectDraft, BoardSnapshot, DeleteRequest)", "completed": false },
      { "id": "20260530-154412-1.3", "name": "Define domain errors in modules/errors.py (KanbanError + subclasses)", "completed": false },
      { "id": "20260530-154412-1.4", "name": "Implement AppPaths in infra/paths.py", "completed": false },
      { "id": "20260530-154412-1.5", "name": "Implement Clock in infra/clock.py", "completed": false }
    ]
  },
  {
    "id": "20260530-154412-2",
    "name": "Repository",
    "subtasks": [
      { "id": "20260530-154412-2.1", "name": "Implement KanbanRepository.initialize (schema + indexes)", "completed": false },
      { "id": "20260530-154412-2.2", "name": "Implement project CRUD and filtering queries", "completed": false },
      { "id": "20260530-154412-2.3", "name": "Implement task CRUD and active-task queries", "completed": false },
      { "id": "20260530-154412-2.4", "name": "Implement set_task_status, archive_task, and archived-task queries", "completed": false },
      { "id": "20260530-154412-2.5", "name": "Write KanbanRepository unit tests (schema, CRUD, filtering, archive ordering)", "completed": false }
    ]
  },
  {
    "id": "20260530-154412-3",
    "name": "Core Service",
    "subtasks": [
      { "id": "20260530-154412-3.1", "name": "Implement project lifecycle methods on KanbanService", "completed": false },
      { "id": "20260530-154412-3.2", "name": "Implement task lifecycle methods on KanbanService", "completed": false },
      { "id": "20260530-154412-3.3", "name": "Implement load_board with the documented priority ordering", "completed": false },
      { "id": "20260530-154412-3.4", "name": "Implement stepwise move_task_left/right and archive_task rules", "completed": false },
      { "id": "20260530-154412-3.5", "name": "Implement prepare_deletion and confirm_delete with exact-phrase validation", "completed": false },
      { "id": "20260530-154412-3.6", "name": "Write KanbanService unit tests (ordering, transitions, archive eligibility, clock usage, confirmation)", "completed": false }
    ]
  },
  {
    "id": "20260530-154412-4",
    "name": "Board Navigator",
    "subtasks": [
      { "id": "20260530-154412-4.1", "name": "Implement BoardNavigator movement and clamping", "completed": false },
      { "id": "20260530-154412-4.2", "name": "Implement BoardNavigator.focus capability computation", "completed": false },
      { "id": "20260530-154412-4.3", "name": "Write BoardNavigator unit tests (row preservation, clamping, empty columns, capabilities)", "completed": false }
    ]
  },
  {
    "id": "20260530-154412-5",
    "name": "Read-only Screens",
    "subtasks": [
      { "id": "20260530-154412-5.1", "name": "Build WelcomeScreen and ProjectPickerScreen on KanbanRepository", "completed": false },
      { "id": "20260530-154412-5.2", "name": "Build ArchiveScreen with case-insensitive filtering", "completed": false }
    ]
  },
  {
    "id": "20260530-154412-6",
    "name": "Board & Task Flows",
    "subtasks": [
      { "id": "20260530-154412-6.1", "name": "Build KanbanBoardScreen wired to KanbanService and BoardNavigator", "completed": false },
      { "id": "20260530-154412-6.2", "name": "Build ProjectFormScreen and TaskFormScreen submitting drafts", "completed": false },
      { "id": "20260530-154412-6.3", "name": "Build TaskDetailScreen (read-only)", "completed": false },
      { "id": "20260530-154412-6.4", "name": "Build ConfirmDeleteScreen and wire prepare_deletion/confirm_delete flows", "completed": false }
    ]
  },
  {
    "id": "20260530-154412-7",
    "name": "Integration",
    "subtasks": [
      { "id": "20260530-154412-7.1", "name": "Wire main.py and PersonalKanbanApp composition", "completed": false },
      { "id": "20260530-154412-7.2", "name": "Add integration tests for the main user stories", "completed": false }
    ]
  }
]
```

Notice: main tasks mirror the design's `Implementation Order`; each module is implemented before
the screens that depend on it; tests for a module sit in the same phase that builds it; and the
final phase wires composition and adds end-to-end coverage for the PRD's user stories.
