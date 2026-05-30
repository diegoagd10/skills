# System Design: Personal Kanban TUI

> Worked example for the `to-design` skill. It shows the `TEMPLATE.md` sections filled in for a
> real feature. Read it for the *shape and depth* expected — how Scope/Non-Goals bound the work,
> how each deep module declares the knowledge it hides ("Why this is deep"), and how the
> dependency graph stays acyclic with only the entry point wiring concretes.

## Goal

Build a local-first single-user terminal application for managing personal software projects with a kanban workflow. The design keeps the Textual UI thin and moves the important rules into a small set of deep modules so task lifecycle, ordering, archive behavior, filtering, and destructive confirmation stay consistent across screens.

## Scope

V1 covers:

- Project CRUD
- Task CRUD inside a selected project
- Kanban navigation and stepwise status movement
- Read-only task detail views
- One-way archive flow from `Done`
- Global archived task browsing and deletion
- Case-insensitive substring filtering for selectors and archive lists
- Exact-name destructive confirmation
- SQLite persistence in a local application data directory

V1 excludes sync, multi-user support, auth, subtasks, due dates, and unarchive.

## Non-Goals

This design does not attempt to solve:

- Multi-user collaboration, synchronization, or cloud storage
- Plugin systems, extension points, or customization frameworks
- General-purpose workflow engines beyond the fixed personal kanban flow
- Advanced planning features such as subtasks, due dates, reminders, or recurring tasks
- Undo, unarchive, or soft-delete recovery beyond the exact-phrase confirmation step
- Cross-platform packaging and distribution details beyond running locally with Python, Textual, and SQLite

## Design Principles

- Keep the UI layer focused on rendering and key bindings.
- Concentrate domain rules in a few deep modules with domain-oriented methods.
- Prevent leakage of SQLite details, sorting rules, and status transition rules into screens.
- Represent board focus as explicit state objects instead of ad hoc widget logic.

## Architecture Overview

The application has four layers:

1. `app`: bootstraps Textual, builds the SQLite connection, and wires services into screens.
2. `ui`: Textual screens and reusable widgets. These translate keyboard events into domain calls.
3. `modules`: deep modules that own workflow and board navigation rules.
4. `infra`: SQLite schema creation and row mapping hidden behind the repository module.

The important design choice is to make `KanbanService` and `BoardNavigator` the modules that absorb most of the workflow complexity, while `KanbanRepository` remains available for read-only domain queries that do not need workflow policy. That avoids padding the service with echo-wrapper methods just to preserve a layer boundary.

## Domain Model

### Enums

```python
class ActiveTaskStatus(StrEnum):
    READY = "ready"
    IN_PROGRESS = "in_progress"
    PENDING_CONFIRMATION = "pending_confirmation"
    DONE = "done"


class Complexity(IntEnum):
    SIMPLE = 1
    MEDIUM = 2
    COMPLEX = 3
```

### Entities

```python
@dataclass(frozen=True)
class Project:
    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Task:
    id: int
    project_id: int
    title: str
    description: str
    complexity: Complexity
    important: bool
    urgent: bool
    status: ActiveTaskStatus
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ArchivedTaskRow:
    task_id: int
    project_id: int
    project_name: str
    title: str
    description: str
    complexity: Complexity
    important: bool
    urgent: bool
    archived_at: datetime
```

### Value Objects

```python
@dataclass(frozen=True)
class TaskDraft:
    title: str
    description: str
    complexity: Complexity
    important: bool
    urgent: bool


@dataclass(frozen=True)
class ProjectDraft:
    name: str
    description: str


@dataclass(frozen=True)
class BoardSnapshot:
    project: Project
    columns: dict[ActiveTaskStatus, list[Task]]


@dataclass(frozen=True)
class DeleteRequest:
    kind: Literal["project", "task", "archived_task"]
    target_id: int
    expected_phrase: str
```

Priority is derived, not stored. The sorting key is:

1. `important and urgent`
2. `important and not urgent`
3. `not important and urgent`
4. `not important and not urgent`
5. lower complexity first
6. older creation time first for stable ordering

`KanbanService.load_board()` owns this ordering through a private `priority_key(task)` helper. `KanbanRepository.list_active_tasks()` returns active tasks in no guaranteed board order, so the domain priority rule does not leak into SQL.

## Deep Modules

### 1. `KanbanRepository`

Purpose: hide SQLite schema, queries, cascading deletion behavior, and row mapping. This module exposes domain nouns and stable query methods instead of SQL-shaped primitives.

```python
class KanbanRepository:
    def __init__(self, db_path: Path) -> None: ...

    def initialize(self) -> None: ...

    def create_project(self, draft: ProjectDraft, now: datetime) -> Project: ...
    def update_project(self, project_id: int, draft: ProjectDraft, now: datetime) -> Project: ...
    def delete_project(self, project_id: int) -> None: ...
    def get_project(self, project_id: int) -> Project | None: ...
    def list_projects(self) -> list[Project]: ...
    def list_projects_matching(self, query: str) -> list[Project]: ...

    def create_task(self, project_id: int, draft: TaskDraft, now: datetime) -> Task: ...
    def update_task(self, task_id: int, draft: TaskDraft, now: datetime) -> Task: ...
    def delete_task(self, task_id: int) -> None: ...
    def get_task(self, task_id: int) -> Task | None: ...
    def list_active_tasks(self, project_id: int) -> list[Task]: ...
    def list_archived_tasks(self) -> list[ArchivedTaskRow]: ...
    def list_archived_tasks_matching(self, query: str) -> list[ArchivedTaskRow]: ...

    def set_task_status(self, task_id: int, status: ActiveTaskStatus, now: datetime) -> Task: ...
    def archive_task(self, task_id: int, archived_at: datetime) -> ArchivedTaskRow: ...
```

Why this is deep:

- Screens never know table names, joins, or timestamp update rules.
- The repository hides the storage detail that archived rows share the same table as active tasks.
- Query methods are already domain-shaped enough for read-only screens to use directly without a service relay.
- The repository never decides what "now" is; mutating callers provide timestamps explicitly.
- Cascade deletion stays in one place.

### 2. `KanbanService`

Purpose: own the application rules for project/task lifecycle, stepwise status changes, archive eligibility, board ordering, and destructive confirmation. This is the main workflow module.

```python
class KanbanService:
    def __init__(self, repository: KanbanRepository, clock: Clock) -> None: ...

    def create_project(self, draft: ProjectDraft) -> Project: ...
    def edit_project(self, project_id: int, draft: ProjectDraft) -> Project: ...
    def require_project(self, project_id: int) -> Project: ...

    def create_task(self, project_id: int, draft: TaskDraft) -> Task: ...
    def edit_task(self, task_id: int, draft: TaskDraft) -> Task: ...
    def require_task(self, task_id: int) -> Task: ...

    def load_board(self, project_id: int) -> BoardSnapshot: ...
    def move_task_left(self, task_id: int) -> Task: ...
    def move_task_right(self, task_id: int) -> Task: ...
    def archive_task(self, task_id: int) -> ArchivedTaskRow: ...
    def prepare_deletion(
        self,
        kind: Literal["project", "task", "archived_task"],
        target_id: int,
    ) -> DeleteRequest: ...
    def confirm_delete(self, request: DeleteRequest, provided_phrase: str) -> None: ...
```

Rules absorbed here:

- New tasks always start in `Ready`.
- Only one-step moves left or right are allowed.
- Only `Done` tasks can be archived.
- Archived tasks never appear on the active board.
- Board ordering is applied in one place instead of leaking into repository SQL or UI code.
- The service is the single owner of time: every mutation reads from `Clock` and passes timestamps into the repository.
- Deletion preparation and confirmation live behind one service workflow, and the raw delete operations stay private to the service.

### 3. `BoardNavigator`

Purpose: manage board cursor behavior independent of Textual widgets. This prevents focus logic from spreading across screens and makes row preservation and clamping testable.

```python
@dataclass(frozen=True)
class BoardPosition:
    column: ActiveTaskStatus
    row: int


@dataclass(frozen=True)
class BoardFocus:
    position: BoardPosition
    task: Task | None
    at_header: bool
    can_open_task: bool
    can_move_left: bool
    can_move_right: bool
    can_archive: bool


class BoardNavigator:
    def initial_position(self) -> BoardPosition: ...
    def move_up(self, snapshot: BoardSnapshot, position: BoardPosition) -> BoardPosition: ...
    def move_down(self, snapshot: BoardSnapshot, position: BoardPosition) -> BoardPosition: ...
    def move_left(self, snapshot: BoardSnapshot, position: BoardPosition) -> BoardPosition: ...
    def move_right(self, snapshot: BoardSnapshot, position: BoardPosition) -> BoardPosition: ...
    def focus(self, snapshot: BoardSnapshot, position: BoardPosition) -> BoardFocus: ...
```

Rules absorbed here:

- Row `0` is always the header.
- Horizontal moves preserve row index when possible and clamp otherwise.
- Empty columns remain navigable at header row.
- Focus facts such as "header vs task", "can archive", and "can open" are computed once for the UI to render however it wants.

## Screen Controllers

The UI layer is built from Textual screens that depend on the deep modules. Each screen owns rendering and key handling, not business rules.

```python
class WelcomeScreen(Screen): ...
class ProjectFormScreen(Screen): ...
class ProjectPickerScreen(Screen): ...
class ConfirmDeleteScreen(Screen): ...
class KanbanBoardScreen(Screen): ...
class TaskFormScreen(Screen): ...
class TaskDetailScreen(Screen): ...
class ArchiveScreen(Screen): ...
```

Constructor shape:

```python
class KanbanBoardScreen(Screen):
    def __init__(
        self,
        project_id: int,
        service: KanbanService,
        navigator: BoardNavigator,
    ) -> None: ...
```

The same pattern applies to the other screens: pass only the modules they need. Read-only selectors may depend on `KanbanRepository` directly for domain-shaped queries; workflow and mutation screens depend on `KanbanService`.

## Data Flow

### App Startup

1. `main.py` resolves the local app data directory.
2. `KanbanRepository.initialize()` creates tables and indexes if missing.
3. `PersonalKanbanApp` is created with `KanbanRepository`, `KanbanService`, and `BoardNavigator`.
4. The app pushes `WelcomeScreen`.

### Project Flows

1. Welcome and project-picker flows ask `KanbanRepository.list_projects()` or `list_projects_matching(query)` when the filter is non-empty.
2. If empty, the picker screen renders `No projects yet`.
3. Create/edit forms submit `ProjectDraft` to `KanbanService`.
4. Delete flow asks `KanbanService.prepare_deletion("project", project_id)`.
5. `ConfirmDeleteScreen` renders UI copy derived from `DeleteRequest.kind` and `expected_phrase`.
6. On submit, `KanbanService.confirm_delete(request, provided_phrase)` validates the exact match and performs the permanent cascade.

### Board Flows

1. `KanbanBoardScreen` loads `BoardSnapshot` from `KanbanService.load_board(project_id)`.
2. Cursor movement delegates to `BoardNavigator`.
3. The screen asks `BoardNavigator.focus()` for the selected task and capabilities, then renders its own legend text from those facts.
4. `Enter` opens `TaskDetailScreen` only when `focus.can_open_task` is true.
5. `c`, `e`, `d`, `a`, `Shift+H`, and `Shift+L` call `KanbanService`.
6. Task deletion uses `KanbanService.prepare_deletion("task", task_id)` followed by `confirm_delete(...)`.
7. After any mutation, the screen reloads `BoardSnapshot` and asks `BoardNavigator` to keep or clamp focus.

### Archive Flows

1. `ArchiveScreen` loads rows from `KanbanRepository.list_archived_tasks()`.
2. Filter input calls `KanbanRepository.list_archived_tasks_matching(query)`.
3. `Enter` opens read-only detail view.
4. Delete flow uses `KanbanService.prepare_deletion("archived_task", task_id)` and `confirm_delete(...)`.

## Dependency Graph

```text
main.py
  -> AppPaths
  -> KanbanRepository
  -> KanbanService
  -> BoardNavigator
  -> PersonalKanbanApp

PersonalKanbanApp
  -> WelcomeScreen
  -> ProjectPickerScreen
  -> ProjectFormScreen
  -> KanbanBoardScreen
  -> ArchiveScreen

WelcomeScreen / ProjectPickerScreen / ArchiveScreen
  -> KanbanRepository

ProjectFormScreen / Task screens
  -> KanbanService

KanbanBoardScreen
  -> KanbanService
  -> BoardNavigator

KanbanService
  -> KanbanRepository
  -> Clock

KanbanRepository
  -> sqlite3
```

Dependency rule:

- `ui` may depend on `modules` and on `KanbanRepository` for read-only queries.
- `modules` may depend on `infra`.
- `infra` must not depend on `ui`.
- Only `main.py` wires concrete instances together.

## SQLite Design

### Tables

`projects`

- `id INTEGER PRIMARY KEY`
- `name TEXT NOT NULL UNIQUE`
- `description TEXT NOT NULL`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

`tasks`

- `id INTEGER PRIMARY KEY`
- `project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE`
- `title TEXT NOT NULL`
- `description TEXT NOT NULL`
- `complexity INTEGER NOT NULL`
- `important INTEGER NOT NULL`
- `urgent INTEGER NOT NULL`
- `status TEXT NOT NULL`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

### Indexes

- `idx_tasks_project_status` on `(project_id, status)`
- `idx_tasks_status_updated` on `(status, updated_at DESC)`

Archive is represented in storage by `status = 'archived'`. The repository treats that as a persistence detail: active-board APIs only expose `ActiveTaskStatus`, while archive queries return `ArchivedTaskRow`. `updated_at` becomes the archive timestamp when archiving occurs. This keeps v1 schema small without leaking archive state into board-facing interfaces.

## Project Structure

```text
personal_kanban_tui/
  main.py
  app.py
  modules/
    models.py
    repository.py
    service.py
    board.py
    errors.py
  ui/
    screens/
      welcome.py
      project_picker.py
      project_form.py
      confirm_delete.py
      kanban_board.py
      task_form.py
      task_detail.py
      archive.py
    widgets/
      board_column.py
      filter_input.py
      legend_bar.py
  infra/
    paths.py
    clock.py
```

Entry points exposed:

- `main.py`: CLI launch entry point
- `app.py`: Textual app composition

Hidden implementation:

- `modules/` contains workflow and domain logic
- `infra/` contains local environment details
- `ui/widgets/` contains reusable rendering pieces, not rules

## Error Model

Use explicit domain exceptions so screens can show precise messages without knowing repository details.

```python
class KanbanError(Exception): ...
class NotFoundError(KanbanError): ...
class InvalidTransitionError(KanbanError): ...
class ArchiveNotAllowedError(KanbanError): ...
class DuplicateProjectNameError(KanbanError): ...
```

## Testing Strategy

Prioritize tests around the deep modules, not widget internals.

1. `KanbanService`
   - new tasks start in `Ready`
   - create/edit/status/archive mutations all use the injected `Clock`
   - status movement is stepwise only
   - archiving only works from `Done`
   - archived tasks do not appear on active board
   - deletion cascades through project removal
   - deletion confirmation rejects non-exact input and executes delete on exact match
   - raw deletion is not exposed outside the service
   - board loading applies the documented priority order
2. `BoardNavigator`
   - initial focus is `Ready` header
   - row preservation across horizontal movement
   - clamping when target column is shorter
   - empty-column navigation
   - focus capabilities reflect header/task selection and `Done` archive eligibility
3. `KanbanRepository`
   - schema initialization
   - project/task CRUD
   - project and archive filtering stay case-insensitive and domain-shaped
   - archive ordering by `updated_at`
   - archived rows never appear in active-task queries
   - mutation methods persist caller-supplied timestamps without their own time source

## Implementation Order

1. Build `modules/models.py`, `infra/paths.py`, and `infra/clock.py`.
2. Implement `KanbanRepository` with schema initialization and CRUD.
3. Implement `KanbanService` with status, ordering, archive, and delete-confirmation rules.
4. Implement `BoardNavigator`.
5. Build read-only project/archive selectors on top of `KanbanRepository`.
6. Build board and task flows.
7. Build archive screen and destructive confirmation flows.
8. Add integration tests for the main user stories.
