# Concern: Design Patterns (Gang of Four)

## Category
architecture

## Areas
api, data

## Boundary

This concern owns the **implementation-level object-oriented vocabulary** — the
Gang of Four catalog of reusable solutions for object construction, structural
composition, and runtime collaboration *within a single process*. It supplies
the shared names (Strategy, Adapter, Observer, …) developers use to describe a
recurring micro-design and the canonical trigger that justifies each. It does
**not** own domain meaning, the macro layering of the codebase, or cross-system
messaging. Three neighbors must stay distinct:

- **`domain-driven-design`** owns **what** to model and its business semantics —
  the ubiquitous language, aggregates, invariants, and the *domain roles* named
  Factory, Repository, and Domain Event. Those roles carry business meaning; GoF
  supplies the **implementation-level mechanics** that may realize them (a DDD
  Factory is often a GoF Factory Method or Builder; a DDD Domain Event is often
  delivered via Observer). Name the GoF mechanic; leave the domain semantics to
  DDD. A GoF pattern is never a reason to introduce a domain concept that the
  ubiquitous language does not name.
- **`onion-architecture`** owns the **macro arrangement** — which layer code
  lives in and the dependency rule (dependencies point inward). GoF operates
  **within a layer**, not as the application's architecture: Strategy or
  Decorator is a class-level collaboration inside one layer, not a substitute for
  the layering itself. Do not promote a GoF pattern to architecture, and do not
  restate the dependency rule here.
- **`enterprise-integration-patterns`** owns **cross-system, inter-process
  messaging** — channels, routers, message transformation between separate
  systems. GoF is **intra-process** object collaboration. A GoF Mediator
  coordinating objects in one process is not a message broker; a GoF Adapter
  converting an in-process interface is not an integration message translator.
  When the collaboration crosses a system boundary, it is EIP's lane.

## Components

The 23 GoF patterns group into three families. Each is a named solution to a
**recurring** problem, paired with the canonical trigger that justifies it.

- **Creational** — control how and when objects are constructed, decoupling
  client code from concrete classes.
- **Structural** — compose objects and classes into larger structures while
  keeping them flexible and efficient.
- **Behavioral** — assign responsibility and define the runtime collaboration
  and communication between objects.

### Intent table (pattern → intent → canonical trigger)

| Pattern | Family | Intent | Use when |
|---|---|---|---|
| Factory Method | Creational | Define an interface for creating an object, letting subclasses choose the concrete type | A class cannot anticipate the concrete class it must instantiate, or wants subclasses to specify it |
| Abstract Factory | Creational | Provide an interface for creating *families* of related objects without naming concretes | The system must work with one of several interchangeable product families |
| Builder | Creational | Separate construction of a complex object from its representation | Constructing an object has many steps / optional parts and the same process yields different representations |
| Prototype | Creational | Create new objects by cloning an existing instance | Object creation is costly, or the concrete type is decided at runtime by copying a prototype |
| Singleton | Creational | Ensure a class has exactly one instance with a global access point | Exactly one instance must exist and be shared (use sparingly — see Constraints) |
| Adapter | Structural | Convert one interface into another that clients expect | An existing/legacy class has the right behavior but the wrong interface |
| Bridge | Structural | Decouple an abstraction from its implementation so both vary independently | An abstraction and its implementation should each be extensible without a combinatorial class explosion |
| Composite | Structural | Compose objects into part-whole trees, treating leaves and composites uniformly | Clients should treat individual objects and compositions the same way |
| Decorator | Structural | Attach responsibilities to an object dynamically | Behavior must be added/removed per-object at runtime without subclassing every combination |
| Facade | Structural | Provide a unified, simplified interface to a subsystem | Clients need a simple entry point and should be decoupled from a complex subsystem's parts |
| Flyweight | Structural | Share fine-grained objects to support large numbers efficiently | Many objects are near-identical and per-instance memory is the bottleneck (intrinsic state can be shared) |
| Proxy | Structural | Provide a surrogate that controls access to another object | Access control, lazy loading, remoting, or logging must wrap a real subject transparently |
| Chain of Responsibility | Behavioral | Pass a request along a chain until a handler processes it | More than one object may handle a request and the handler is not fixed in advance |
| Command | Behavioral | Encapsulate a request as an object | Requests must be queued, logged, parameterized, or made undoable/redoable |
| Interpreter | Behavioral | Represent a grammar and interpret sentences in it | A simple, stable, well-understood language/grammar recurs and is worth modeling as rule classes |
| Iterator | Behavioral | Provide sequential access to a collection without exposing its structure | Traversal must be uniform across collections and independent of their internal representation |
| Mediator | Behavioral | Centralize how a set of objects interact | Many-to-many object coupling has become a tangle; a coordinator can own the interaction |
| Memento | Behavioral | Capture and restore an object's state without breaking encapsulation | Snapshot/restore (undo) is needed without exposing internal fields |
| Observer | Behavioral | Define a one-to-many dependency so dependents are notified of changes | A change in one object must update an open, varying set of others without tight coupling |
| State | Behavioral | Let an object alter its behavior when its internal state changes | Behavior depends on state and is otherwise a sprawl of conditionals over a state variable |
| Strategy | Behavioral | Define a family of interchangeable algorithms behind one interface | Several algorithms solve one problem and the choice varies (at runtime or by configuration) |
| Template Method | Behavioral | Define an algorithm's skeleton, deferring steps to subclasses | Several variants share one algorithmic shape but differ in specific steps |
| Visitor | Behavioral | Represent an operation over an object structure, separate from the elements | New operations must be added over a *stable* element hierarchy without editing each element |

## Constraints

### A pattern is a vocabulary for a recurring problem, not a goal

- Patterns are a **shared vocabulary** applied to **recurring** problems that have
  actually appeared, not a target to hit or a sign of sophistication. The measure
  of a design is whether it solves the problem simply — not how many named
  patterns it contains.
- A pattern is introduced **only against a named recurring problem, with the
  intent recorded** (the row of the table above it satisfies) — never
  speculatively, "to be flexible later", or because the pattern is familiar.

### Prefer the simplest construct that solves the problem (KISS/YAGNI)

- Prefer the simplest construct that meets the requirement. A plain function, a
  direct call, a `switch`, or a literal value is the right answer until a
  *concrete* recurring force demands the indirection.
- A pattern earns its place only by **removing duplication or absorbing a real
  variability/extension point that exists now**. A pattern that adds indirection
  without removing either is **speculative generality** — a finding, not a
  feature. This is the YAGNI/KISS guard against "pattern-itis" and the golden
  hammer (forcing one familiar pattern onto every problem).

### GoF mechanics, not domain or architecture

- GoF supplies **implementation-level** vocabulary. When the construct carries
  business meaning, name the **domain role** (`domain-driven-design`) and let GoF
  describe only the mechanic. When it concerns which layer code lives in, that is
  `onion-architecture`. When it crosses a process/system boundary, that is
  `enterprise-integration-patterns`. Do not stretch a GoF pattern to cover any of
  the three.

### Singleton and global state are constrained

- **Singleton** is the most abused creational pattern: it introduces hidden
  global state and coupling that frustrates testing and concurrency. Prefer
  passing the single instance via dependency injection / composition; reserve
  the Singleton pattern for cases where exactly-one is a genuine, enforced
  invariant, and record why.

## Drift Signals (anti-patterns to reject in review)

- A pattern introduced with **no named recurring problem** and no recorded intent
  → speculative; remove it or record the concrete force it answers
- Indirection (factory, strategy, decorator, …) that removes **neither**
  duplication **nor** a real variability point → pattern-itis / speculative
  generality; collapse to the simplest construct
- One familiar pattern forced onto unrelated problems → **golden hammer**; choose
  the construct that fits, or no pattern at all
- A GoF pattern standing in for the **domain model** (inventing a concept the
  ubiquitous language does not name) → that is `domain-driven-design`'s lane
- A GoF pattern promoted to the application's **architecture / layering** → that
  is `onion-architecture`'s lane; keep GoF within a layer
- A GoF Mediator/Adapter spanning **separate systems / processes** → that is
  `enterprise-integration-patterns`' lane
- **Singleton** used as ambient global state (reached for statically, not
  injected) → inject the instance; justify any true exactly-one invariant
- A name claimed but not realized (called "Strategy" with one hardcoded branch,
  "Observer" with a single fixed listener) → either the pattern is unwarranted or
  it is misnamed; align the name with the mechanic actually present

## When to use

Select this concern for work involving **non-trivial object-oriented modeling** —
recurring extension points, varying runtime behavior, or object-collaboration
mechanics that benefit from a shared, named vocabulary (a rules/strategy engine,
a pluggable-handler pipeline, an event/notification fan-out, an
adapter/anti-corruption seam, an undoable command surface). It is a
**non-exclusive reference / vocabulary concern** (no slot, fills no exclusive
position); `areas: api, data` scopes its practices to the implementation layers
where OO collaboration lives. Compose it with the tech-stack concern (which fixes
the language idioms), with `domain-driven-design` (which supplies domain
semantics for the roles GoF implements), and with `onion-architecture` (which
arranges those objects into layers).

Do **not** select it for **thin CRUD** surfaces, glue scripts, configuration, or
read-only/marketing content where the simplest direct construct is the right
answer and naming a pattern only adds indirection.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: each pattern introduced against a named recurring problem + recorded intent
- TD: the pattern and the variability/duplication it absorbs at the collaboration point
