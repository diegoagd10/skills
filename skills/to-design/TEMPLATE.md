# System Design: <Feature / System Name>

## Goal

<One paragraph. What is being built and for whom. State the core design bet in a single
sentence — usually "keep the <UI/transport/edge> layer thin and concentrate the rules in a
small set of deep modules so <the cross-cutting concerns> stay consistent everywhere.">

## Scope

V1 covers:

- <bullet the capabilities that ARE in this version>

V1 excludes <list the deferred capabilities in one line>.

## Non-Goals

This design does not attempt to solve:

- <each thing the design deliberately refuses to solve, and that a reader might wrongly assume
  is in scope — multi-user, plugins, undo, general-purpose engines, packaging, etc.>

## Design Principles

- <3–5 principles that justify the module boundaries below. Each principle should map to a
  decision a reader can check later, e.g. "Keep the UI focused on rendering and key bindings",
  "Concentrate domain rules in a few deep modules", "Prevent storage/transport details from
  leaking into <UI>".>

## Architecture Overview

The application has <N> layers:

1. `<entry layer>`: bootstraps the runtime, builds connections, wires modules together.
2. `<edge layer>`: <UI / API / CLI>. Translates external events into domain calls only.
3. `<modules>`: the deep modules that own the rules.
4. `<infra>`: storage schema and row/wire mapping, hidden behind a repository module.

<One paragraph naming WHICH module absorbs most of the complexity and why. Call out any
module that is intentionally allowed to be used directly by the edge layer for read-only
queries — and justify it against the echo-wrapper rule (don't relay calls just to preserve a
layer boundary).>

## Domain Model

<Define the data the modules exchange. Group as Enums / Entities / Value Objects. Prefer
immutable types. State derived-vs-stored explicitly — if a value is computed (priority,
status rollups, ordering keys), say WHERE that computation lives so it cannot leak into
storage or the edge layer.>

### Enums

```<language>
<status / category enums>
```

### Entities

```<language>
<the persisted nouns, with their fields and types>
```

### Value Objects

```<language>
<drafts, snapshots, requests — the transient shapes passed across boundaries>
```

<If any ordering / priority / derivation rule exists, spell it out as a numbered list and name
the single method that owns it.>

## Deep Modules

<For EACH deep module, repeat the block below. A module earns a slot here only if it is deep:
simple interface, real functionality hidden, called from more than one place. Reject
pass-throughs, echo-wrappers, single-implementation interfaces, and premature generalization.>

### <N>. `<ModuleName>`

Purpose: <one or two sentences — what knowledge this module hides from everyone else.>

```<language>
class <ModuleName>:
    def __init__(self, <deps>) -> None: ...

    <domain-vocabulary method signatures — names speak the domain, not the inner module's
    verbs. Keep parameter counts low; prefer passing a value object over many primitives.>
```

Why this is deep / Rules absorbed here:

- <each piece of knowledge this module owns so no other module has to know it — schema,
  ordering, transition rules, time source, cascade behavior, confirmation, etc.>

## <Edge Layer> Controllers

<Describe the edge components (screens / handlers / endpoints). Each owns rendering and event
handling, NOT business rules. Show the constructor shape so the dependency direction is
explicit — edge components receive the deep modules they need, nothing more.>

```<language>
class <EdgeComponent>:
    def __init__(self, <only the modules this component needs>) -> None: ...
```

<State the rule: read-only components may depend on the repository directly for domain-shaped
queries; anything that mutates depends on the service/workflow module.>

## Data Flow

<Walk the key flows as numbered steps, grouped by area (startup, then each major flow). Each
step names the module method called. The reader should be able to trace an external event to
the exact method that handles it without guessing.>

### App Startup

1. <resolve config / paths>
2. <initialize storage>
3. <construct modules and wire them>
4. <enter the first screen / start serving>

### <Flow A>

1. ...

### <Flow B>

1. ...

## Dependency Graph

```text
<entry point>
  -> <module>
  -> <module>
  -> <app>

<app>
  -> <edge components>

<edge components>
  -> <modules they may depend on>

<service / workflow module>
  -> <repository>
  -> <clock / other infra>

<repository>
  -> <storage driver>
```

Dependency rule:

- `<edge>` may depend on `<modules>` (and on the repository for read-only queries only).
- `<modules>` may depend on `<infra>`.
- `<infra>` must not depend on `<edge>`.
- Only the entry point wires concrete instances together.

## Storage Design

<If the system persists data, define it. Tables/collections with fields and constraints,
indexes, and any storage detail the repository deliberately hides from callers (e.g. archived
rows sharing a table, soft-delete flags, denormalized columns). State which persistence facts
must NOT appear in module interfaces.>

### Tables / Collections

`<name>`

- `<field> <type/constraint>`

### Indexes

- `<index>` on `<columns>` — <why>

## Project Structure

```text
<package_root>/
  <entry point file>
  <app composition file>
  modules/
    <one file per deep module + models + errors>
  <edge>/
    <screens / handlers / endpoints>
  infra/
    <paths, clock, storage adapters>
```

Entry points exposed:

- <the files a reader runs or imports to start the system>

Hidden implementation:

- <which directories hold rules vs. environment details vs. reusable rendering pieces>

## Error Model

<Define explicit domain exceptions so the edge layer can show precise messages without knowing
storage internals. One base error plus specific subclasses for each rule that can be violated.>

```<language>
class <BaseError>(Exception): ...
class <NotFoundError>(<BaseError>): ...
class <InvalidTransitionError>(<BaseError>): ...
<one subclass per distinct failure the edge layer must distinguish>
```

## Testing Strategy

Prioritize tests around the deep modules, not edge internals.

1. `<ServiceOrWorkflowModule>`
   - <the rules it owns, each as a testable assertion>
2. `<NavigatorOrSecondModule>`
   - <its rules>
3. `<Repository>`
   - <schema init, CRUD, filtering, ordering, and the persistence invariants it guarantees>

## Implementation Order

<A numbered build order that respects the dependency graph: models and infra first, then the
repository, then the service, then navigators, then read-only edge components, then mutation
flows, then integration tests for the user stories.>

1. ...
