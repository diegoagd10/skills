---
name: coding-guidelines
description: >-
  Design and write low-complexity code using Ousterhout's deep-modules
  philosophy, routed by role. Use this skill whenever someone (a) DESIGNS a
  system, subsystem, module, class, or interface before writing code — drawing
  boundaries, deciding what to expose vs. hide, choosing how general an API
  should be (the ARCHITECT); (b) WRITES or refactors a class, function, or
  application (the DEVELOPER); or (c) REVIEWS a diff, PR, or someone's code for
  design quality (the REVIEWER). Trigger it even when the user never says
  "complexity" or "design": any time the work involves drawing a
  module/class/function boundary, deciding what an interface should reveal or
  conceal, or judging whether code is well-structured, this skill applies.
---

## How to use this skill — pick your role first

This skill fights ONE enemy at three altitudes: **complexity**. The deep
material lives in `references/`; you load only what your role needs. But the
foundation below — *The Nature of Complexity* — is shared. **Everyone reads it
first.** It is the vocabulary every reference assumes.

Then jump to your **Persona Guide** at the bottom of this file:

- **Architect** — deciding boundaries *before* code exists.
- **Developer** — writing the classes and functions *now*.
- **Reviewer** — auditing a change *after* it's written.

Each persona tells you which `references/` files to read, in what order, and the
single question to hold in your head while you work.

---

## The Nature of Complexity — read this FIRST (all personas)

Every rule in every reference is a tool to fight ONE enemy: complexity.
Definition:

> Complexity is anything related to the **structure** of a system that makes it
> hard to **understand** or **modify**.

Two consequences you must internalize:

- It is **structural and holistic** — not one ugly line, but how the pieces
  relate. Judge designs, not snippets.
- It is felt by **readers, not the author**. If others find your code confusing,
  it IS complex — your own "it's obvious to me" does not count. Weight it by
  time: a horrible file nobody touches barely matters; a mildly messy one you
  edit daily is killing you.

### The 3 symptoms (how complexity SHOWS UP)

**1. Change amplification** — a conceptually simple change forces edits in many
places.

```javascript
// BAD: the brand color is duplicated across 50 files.
ctx.fillStyle = "#3498db";          // page A
button.style.background = "#3498db"; // page B  ...and 48 more

// GOOD: one source of truth — one conceptual change, one edit.
const theme = { brandColor: "#3498db" };
```

**2. Cognitive load** — how much you must hold in your head to make a change.
Fewer lines can mean MORE load — line count is not the metric.

```javascript
// BAD: "clever", fewer lines, high load. What is b[i]? why i % 2? what does ?? do?
const r = a.filter((x, i) => i % 2 === b[i]).map(x => x.v ?? 0);

// GOOD: more lines, lower load — the reader holds almost nothing.
const result = [];
for (let i = 0; i < items.length; i++) {
  if (i % 2 === selectors[i]) result.push(items[i].value ?? 0);
}
```

**3. Unknown unknowns** — you don't even know which code you must touch, or what
you must know, to make a change correctly. This is the WORST symptom: the other
two are visible and painful, this one stays hidden until a bug hits production.

```javascript
// You edit this happily...
function registerUser(user) { db.users.insert(user); }
// ...not knowing a hidden trigger elsewhere assumed THIS sent the welcome email.
// Nothing here warns you. No visible amplification, no visible load. Just a bug, later.
```

The goal of good design is an **obvious system**: one where you can change code
confident about what is affected and what you need to know.

### The 2 causes (where it COMES FROM)

**1. Dependencies** — code that can't be understood or changed in isolation
because it relates to other code. Dependencies are **fundamental and
unavoidable**; you don't eliminate them, you reduce their number and make the
survivors obvious. Put them in signatures, not in hidden order or shared state.

```javascript
// BAD: implicit ordering dependency — reorder these and it explodes, silently.
config.load(); db.connect(); cache.warmup();

// GOOD: the dependency lives in the signatures — impossible to misorder.
const cfg = loadConfig();
const db  = connect(cfg);
const cache = warmup(db);
```

**2. Obscurity** — important information that is not obvious: a meaningless name,
a magic number, a dependency you can't see. Often paired with dependencies (the
dangerous dependency is the invisible one).

```javascript
// BAD: what is d? t? where do 0.6 / 0.4 come from?
function calc(d, t) { return d * 0.6 + t * 0.4; }

// GOOD: the code speaks for itself — no docs required.
const DISTANCE_WEIGHT = 0.6;
const TIME_WEIGHT = 0.4;
function rankRouteScore(distanceKm, durationMin) {
  return distanceKm * DISTANCE_WEIGHT + durationMin * TIME_WEIGHT;
}
```

### How it all connects

- Mismanaged **dependencies** → change amplification + unknown unknowns.
- **Obscurity** → cognitive load + unknown unknowns.

Everything in `references/` (deep modules, information hiding, the independence
test, layers) is just specific tactics against these two causes.

### Pull complexity downwards

When a module already has enough information to make a decision, the module
should absorb that complexity instead of pushing it onto callers. A slightly
more complex implementation is usually worth it if it creates a simpler, more
obvious interface.

Callers should express **intent**, not assemble internal mechanics:

```javascript
// BAD: every caller must know pagination mechanics, ordering, and limits.
const offset = (page - 1) * pageSize;
const users = await db.users.findMany({
  skip: offset,
  take: pageSize,
  orderBy: { createdAt: "desc" },
});

// GOOD: the repository owns those details.
const users = await userRepository.list({ page, pageSize });
```

This applies to validation, retries, formatting, configuration, state
transitions, error translation, and protocol details. If every caller must
remember the same "before you call this, do X/Y/Z" ritual, the module leaked a
decision upward.

```javascript
// BAD: callers know the valid order state transition.
if (order.status !== "paid") throw new Error("Only paid orders can be shipped");
order.status = "shipped";
await orderRepository.save(order);

// GOOD: the order module owns the rule.
await order.ship();
await orderRepository.save(order);
```

Do not confuse this with hiding fundamental dependencies. Required inputs should
still be explicit. The point is to hide internal decisions, not to create magic
or global state.

### Complexity is incremental — zero tolerance

It never arrives in one catastrophe. It accumulates from tiny increments — one
vague name, one hidden dependency, one missing line — each "insignificant on its
own". That is exactly the trap: because each looks harmless, nobody stops. Add
300 over two years and you have a swamp. **Do not let the small increment
through.** This is why the discipline matters at every altitude — architect,
developer, AND reviewer.

---

## The reference library

Six deep dives, each self-contained with its own examples, rules of thumb, and a
finalizing checklist. Read by role (see Persona Guides) — not front to back.

| Reference | Scope | Core question it answers |
|---|---|---|
| `references/deep-modules.md` | **Master rule** (every boundary) | Does this module hide more than the interface it adds? |
| `references/information-hiding.md` | Interfaces & secrets | Is this knowledge the caller NEEDS, or a leaked decision? |
| `references/general-purpose.md` | Interface design | Is the interface general enough, the implementation specific enough? |
| `references/layers.md` | System structure | Does each layer add a NEW abstraction, or just relay one? |
| `references/classes.md` | Class boundaries | Together or apart — by knowledge, never by execution order? |
| `references/functions.md` | Implementation | Can each function be understood on its own? |

`deep-modules.md` is the master yardstick; the other five are tactics that serve
it. When in doubt, that file is the one nobody skips.

---

## Persona Guides

### 🏛️ ARCHITECT — deciding boundaries *before* code exists

Your altitude is **the system**: subsystems, modules, layers, where each design
decision lives. You are choosing seams that will be expensive to move later, so
your leverage is highest and your reading is broadest.

> **Hold this question:** *"Where does each piece of knowledge live, and does
> every boundary I draw hide something real without pushing rituals upward?"*

Read, in this order:

1. **`deep-modules.md`** — the yardstick for every boundary. Deep over shallow;
   reject classitis. This is non-negotiable.
2. **`classes.md`** — *better together or apart?* Decompose by **knowledge**,
   never by order of execution (temporal decomposition). The class boundary IS
   the architectural decision.
3. **`layers.md`** — make every layer earn its place; kill pass-through layers
   and the global-state "shortcut" before they calcify.
4. **`general-purpose.md`** — design interfaces *somewhat* general; push
   special-purpose decisions UP, but don't overshoot into speculative generality.
5. **`information-hiding.md`** — give each design decision ONE owner; this is how
   the system survives change.

At boundary time, ask: "Can this module make the decision itself?" If yes, pull
that complexity downward so callers state intent rather than coordinating steps.

You can skim `functions.md` — it's the developer's altitude. But the principle
(independence test) is the same one you apply to modules.

### 🔨 DEVELOPER — writing the classes and functions *now*

Your altitude is **the code in front of you**: the function you're writing, the
class you're extending, what you expose vs. keep private. You realize the
architect's boundaries in code without leaking or conjoining anything.

> **Hold this question:** *"Can each piece be understood on its own — and am I
> leaking any decision I could have kept secret or handled below?"*

Read, in this order:

1. **`functions.md`** — the independence test. Split/join by complexity, NEVER by
   line count. Conjoined functions (hidden shared state, required call order) are
   the daily trap.
2. **`classes.md`** — the same independence test at class scope; don't merge on a
   one-directional "uses" relationship.
3. **`information-hiding.md`** — don't leak data structures, formats, or magic
   constants through your interfaces; hide *within* the class too (`private`
   over `public`).
4. **`deep-modules.md`** — apply the depth yardstick to every function and class
   you add: is it deeper than the interface it costs?
5. **`layers.md`** — while wiring things together, refuse pass-through methods and
   pass-through variables; inject context, don't reach for a global.

`general-purpose.md` is worth a skim for the *"one method, one caller = smell"*
rule when you design a helper's signature.

While writing, watch for call sites that repeat setup, validation, retries,
formatting, or state checks. That repetition is usually a signal that the callee
should absorb the rule.

### 🔍 REVIEWER — auditing a change *after* it's written

Your altitude is **the diff**. You are a gate: your job is to catch the small
increment before it's merged, name the smell, and explain WHY — not to rewrite
it. Lead with the red-flag index, then open the matching reference for the
precise argument and the fix.

> **Hold this question:** *"Which red flag is this diff about to introduce — and
> can the author understand WHY from my comment?"*

**Red-flag index — smell → where the argument & fix live:**

| If you see in the diff… | It's… | Open |
|---|---|---|
| Same value/decision duplicated across files | Change amplification | `information-hiding.md`, `classes.md` |
| Callers repeat setup/validation/retry/formatting/state-transition rituals | Complexity pushed upward | `information-hiding.md`, `deep-modules.md` |
| Magic numbers, cryptic names, hidden ordering | Obscurity | `SKILL.md` (Nature of Complexity) |
| A wrapper whose interface ≈ its body | Shallow module | `deep-modules.md` |
| Many tiny classes/methods to do one thing | Classitis | `deep-modules.md` |
| Two modules sharing an unstated assumption | Information leakage / back-door | `information-hiding.md` |
| Same value re-validated / re-sanitized in an inner layer of one process | Defensive re-checking (duplicated decision) | `information-hiding.md` |
| Classes split into Reader/Writer, Step1/Step2 | Temporal decomposition | `classes.md` |
| A method that exists for exactly one caller | Special-purpose leaking down | `general-purpose.md` |
| An API abstract enough to need glue to call | Speculative generality | `general-purpose.md` |
| A method that only forwards to a same-sig method | Pass-through method | `layers.md` |
| A param threaded through methods that ignore it | Pass-through variable | `layers.md` |
| A `static`/global introduced to "clean up" params | Hidden dependency trap | `layers.md` |
| Two functions you must read together to follow | Conjoined functions | `functions.md` |
| A function split purely to be shorter | Over-splitting by line count | `functions.md` |

For a thorough review, run the **"Checklist before finalizing…"** at the end of
whichever reference the diff touches — those checklists are written to be applied
to existing code, not just new code. Approve at "good enough, no real red flags,"
not "perfect to my taste" — bikeshedding is its own kind of complexity.

---

> The architect draws the boundaries, the developer fills them without leaking,
> the reviewer guards them. Same discipline — reduce complexity — applied at
> three altitudes. That's the whole skill.
