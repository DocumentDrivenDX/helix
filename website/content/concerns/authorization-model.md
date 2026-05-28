---
title: "Authorization Model"
slug: authorization-model
generated: true
aliases:
  - /reference/glossary/concerns/authorization-model
---

**Category:** Security & Compliance · **Areas:** api

## Description

## Category
security

Authorization is categorized as **security**, not architecture, because its
defining failure is **Broken Access Control** — a principal performing an action
or reading data they are not permitted to. OWASP ranks Broken Access Control as
the #1 web application risk, and NIST treats access control as a core security
function (SP 800-53 AC family; the RBAC standard INCITS 359; the ABAC guide
SP 800-162). The *shape* of the model (RBAC vs ABAC vs ReBAC, and where the
decision point sits) is a design decision, but the reason this concern exists
and the property it must hold — *every privileged action and data return is
authorized, deny-by-default* — is a confidentiality/integrity guarantee. The
category reflects what review must protect.

## Areas
api

## Boundary

This concern owns the **permission model and its enforcement** — *what* an
authenticated principal may do to the resources they can legitimately reach, and
the discipline that every state-changing and data-returning handler asks that
question and refuses by default. It is composable and does **not** fill a slot.
Three neighbours stay distinct, and this concern must not duplicate them:

- **`auth`** owns **who you are** — signup, login, sessions, and that a real
  principal exists and is scoped to its account. `auth` (and the `auth-provider`
  slot behind it) answers *authentication*: "are you signed in, and as whom?".
  This concern answers *authorization*: "given who you are, **may** you do this
  to this resource?". `auth` already names "Authorization (RBAC)" and
  "enforced server-side" as a requirement of its surface; this concern owns the
  **model behind that requirement** and makes the per-handler permission check
  reviewer-checkable. Do not restate signup/session lifecycle here; consume the
  authenticated principal `auth` establishes.
- **`multi-tenancy`** owns **isolation between tenants** — that a record is even
  *in the caller's tenant at all* (an *inter-tenant* guarantee). This concern
  owns **intra-tenant permissions** — given a record the caller can legitimately
  reach, *may they do this to it* ("may this member delete this project in
  *their own* tenant?"). The two compose and are ordered: **the tenant predicate
  must hold before a permission check is meaningful** — a correct permission
  check on a record that belongs to the wrong tenant is still a cross-tenant
  leak, so tenant scoping precedes authorization. `multi-tenancy` states this
  reciprocally; do not fold tenant isolation into this concern, and do not let a
  permission check stand in for the tenant predicate.
- **`security-owasp`** owns general hardening — injection, CSRF, secret
  handling, input validation, TLS. **Broken Access Control is the OWASP umbrella
  failure; this concern is the access-control *model* that prevents it.**
  `security-owasp` says "authorization checked on every protected endpoint";
  this concern owns *how the decision is modeled and enforced* (deny-by-default,
  a chosen model, a central decision point) so that the umbrella requirement has
  a concrete, reviewer-checkable shape.

This concern owns the one thing those do not state: **there is a deliberately
chosen permission model, every state-changing and data-returning handler
authorizes the principal against it deny-by-default, and a negative test proves
an unauthorized principal is refused.**

## Components

- **Permission model** — the chosen model, recorded in an ADR. The spectrum:
  - **RBAC** (roles → permissions; NIST INCITS 359). Principals hold roles;
    roles carry permissions; access flows only through roles. Supports **role
    hierarchies** (a senior role inherits a junior role's permissions) and
    **separation of duties**. The fit for **stable, enumerable role sets**
    (owner / admin / member / viewer). Simplest to reason about and audit;
    strains when rules depend on per-request context or per-record relationships
    ("role explosion").
  - **ABAC** (attributes + policy; NIST SP 800-162). A decision evaluates
    attributes of the **subject, resource, action, and environment** against
    policy rules ("a manager may approve an expense **under $10k** during
    **business hours**"). The fit for **context-rich, fine-grained,
    attribute-dependent** rules. Most expressive; hardest to audit ("who can do
    X?" is a policy-evaluation question, not a lookup).
  - **ReBAC** (relationship tuples; Google Zanzibar). Permission is derived from
    a **graph of relationships** stored as tuples (`object#relation@subject`,
    e.g. `doc:readme#viewer@user:anna`), with permissions computed by traversing
    the graph (groups, nesting, ownership, parent-folder inheritance). The fit
    for **sharing / hierarchy / ownership graphs** (Drive-style "shared with me",
    nested groups, folder inheritance). Scales relationship-driven sharing that
    RBAC/ABAC model awkwardly; needs a tuple store and a consistency model
    (Zanzibar's *zookie* bounds read staleness).
  - These are **combinable** — RBAC with a tenant attribute, or ReBAC with
    role-like relations, is common; the ADR records the primary model and how
    the others augment it.
- **Decision point (PDP) and enforcement point (PEP)** — *where* the decision is
  made and *where* it is enforced (NIST SP 800-162 / XACML vocabulary). The
  **PDP** evaluates the model to a permit/deny; the **PEP** sits at the handler
  and enforces it. **Centralizing the PDP** (a shared authorize() function, a
  policy module, or an engine) keeps the rules in one auditable place; the PEP is
  thin and carries no policy logic. **Policy-as-code** engines (OPA/Rego, AWS
  Cedar / Amazon Verified Permissions, OpenFGA) externalize the PDP so policy is
  declarative, versioned, and testable apart from the application.
- **Permission check at the handler (PEP placement)** — every state-changing
  (write/mutation) and data-returning (read) handler calls the decision point
  before acting, on the **server**. UI affordance (hiding a button) is never the
  authorization.
- **Deny-by-default** — the absence of an explicit grant is a denial; a new
  handler is closed until a check is added, not open until someone remembers to
  close it.
- **Least privilege** — principals and roles receive the **minimum** permissions
  needed for their function; default roles are narrow, broad/superuser grants are
  deliberate and few.
- **Policy administration & audit** — where roles/permissions/policies are
  authored (PAP) and the ability to answer "who can do X?" and "why was this
  permitted?" — easiest under RBAC, a policy-evaluation question under ABAC, a
  graph query under ReBAC.

## Constraints

### A permission model is chosen deliberately and recorded

- The model (RBAC / ABAC / ReBAC, or a named combination) and the **PDP/PEP
  placement** (central decision point; thin enforcement at the handler;
  in-process vs externalized policy engine) are an explicit decision recorded in
  an ADR, justified against the selection criteria — not defaulted implicitly.
- **Selection criteria**: choose **RBAC** for a **stable, enumerable role set**;
  **ABAC** when decisions depend on **request/record context or attributes**;
  **ReBAC** when permission follows a **relationship / sharing / ownership
  graph**. Combine when one model leaves a class of rules awkward.

### Deny-by-default

- The absence of an explicit grant is a **denial**. A handler with no
  authorization check is a defect, not an implicitly-public endpoint. New
  handlers are closed until a check is added.

### Every state-changing and data-returning handler authorizes

- Every handler that **mutates state** or **returns data** authorizes the
  principal against the model, **server-side**, before acting. There is **no
  privileged path that acts or returns data without a permission decision**.
- The check is enforced at a **central decision point** (a shared authorize()
  /policy module/engine), not re-implemented ad hoc per handler — so the rules
  are auditable in one place and a handler cannot quietly diverge.
- The tenant predicate (see `multi-tenancy`) holds **before** the permission
  check: authorization is intra-tenant and presumes the record is already in the
  caller's tenant.

### Least privilege

- Roles/policies grant the **minimum** permissions for the function. Default
  roles are narrow; broad or superuser grants are deliberate, few, and recorded.

### Authorization is tested, not assumed

- A **negative guard test exists**: a principal **without** the required
  permission, calling a state-changing or data-returning handler, receives
  **403/404 — not the action's effect or the data**. Happy-path-green (the
  *permitted* principal succeeds) is necessary but not sufficient; the refusal of
  the *unauthorized* principal is the guard branch the `verification` evidence
  gate requires.

## Drift Signals (anti-patterns to reject in review)

- A state-changing or data-returning handler with **no authorization check** →
  Broken Access Control; add the deny-by-default check at the handler
- Authorization that only **hides UI** (no server-side check) → the API is open;
  enforce on the server
- A permission check **re-implemented ad hoc** in each handler → centralize the
  decision (shared authorize() / policy module / engine) so rules are auditable
- A handler **open by default** until someone adds a check → invert to
  deny-by-default; absence of a grant denies
- A **permission check standing in for the tenant predicate** (or vice versa) →
  tenant isolation is `multi-tenancy`'s and precedes authorization; compose, do
  not substitute
- **Role explosion** — proliferating roles to encode per-record or contextual
  rules → the signal RBAC is the wrong model; move that rule class to ABAC/ReBAC
- Broad/superuser grants handed out **by default** → least privilege; narrow the
  default, make broad grants deliberate
- Model **defaulted implicitly** with no ADR weighing RBAC vs ABAC vs ReBAC and
  PDP/PEP placement → record the decision
- **No negative test** that an unauthorized principal is refused → add the
  guard test; permitted-path-green is not done

## When to use

Any product with **roles or permissions beyond mere login** — where different
principals may do different things (owner vs member, admin vs viewer), resources
are shared on a graph, or actions depend on context/attributes. Compose with
**`auth`** (authn/identity — who you are, distinct from what you may do),
**`multi-tenancy`** (inter-tenant isolation — the tenant predicate precedes the
permission check), and **`security-owasp`** (Broken Access Control is the OWASP
umbrella this model prevents). `areas: api` scopes its practices to the handler
/service layer where enforcement lives. Do **not** select it for
**single-role / single-user tools** (a CLI or app where every authenticated
user may do everything), anonymous public sites, or libraries with no principal
— mere login without differentiated permissions is `auth`'s job, not this
concern's.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: permission model (RBAC/ABAC/ReBAC or combination) + PDP/PEP placement (central vs externalized policy engine)
- TD: central decision point, deny-by-default check on every state-changing/data-returning handler, least privilege
- TEST_PLAN: negative guard — unauthorized principal gets 403/404, not the effect or the data

## ADR References

Projects record an ADR when choosing the permission **model** (RBAC / ABAC /
ReBAC or a named combination) and the **PDP/PEP placement** (central in-process
decision point vs externalized policy engine such as OPA/Rego, AWS Cedar /
Amazon Verified Permissions, or OpenFGA), justified against the selection
criteria — stable role set (RBAC), context/attribute-rich rules (ABAC),
relationship/sharing graph (ReBAC) — and against auditability ("who can do X?")
and consistency needs (for ReBAC, the read-staleness/zookie model).

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

These practices govern the **permission model and its enforcement** — *what* an
authenticated principal may do, and the discipline that every privileged handler
asks and refuses by default. They sit alongside `auth` (who you are),
`multi-tenancy` (is the record even in your tenant — the predicate that precedes
any permission check), and `security-owasp` (Broken Access Control is the OWASP
umbrella this model prevents). Their one job is to make the **missing /
mis-placed authorization check** unreachable and **reviewer-checkable**. Each
MUST/SHOULD below is written so a reviewer can confirm or refute it against the
diff and the running system.

## Choose and record the model (Frame / Design)

- Record the **permission model** in an ADR before building: RBAC, ABAC, ReBAC,
  or a named combination. Apply the selection criteria explicitly:
  - **RBAC** — a **stable, enumerable role set** (owner / admin / member /
    viewer). Model roles → permissions; use **role hierarchies** for inheritance
    and **separation of duties** where two roles must not be held at once.
  - **ABAC** — decisions depend on **subject / resource / action / environment
    attributes or request context** ("approve under $10k", "owner-only after
    lock"). Model as policy rules over attributes.
  - **ReBAC** — permission follows a **relationship / sharing / ownership graph**
    (Drive-style sharing, nested groups, folder inheritance). Model as
    relationship tuples (`object#relation@subject`) traversed to a decision.
- Record the **PDP/PEP placement** in the same ADR: a **central decision point**
  (shared `authorize()` / policy module) and a **thin enforcement point** at each
  handler, in-process or externalized to a policy-as-code engine (OPA/Rego, AWS
  Cedar / Amazon Verified Permissions, OpenFGA). The PEP MUST carry no policy
  logic of its own.
- Capture, per capability, **which permission/role/relationship** each
  state-changing and data-returning operation requires — this is a feature-spec
  output, not an implementation afterthought.

## Deny-by-default (Implementation)

- Authorization **MUST** be deny-by-default: the absence of an explicit grant is
  a **denial**. A handler reachable without passing a permission decision is a
  defect, not an implicitly-public endpoint.
- A newly added state-changing or data-returning handler is **closed until a
  check is added** — not open until someone remembers to close it. Prefer a
  framework default (middleware/guard that denies unless a route opts into a
  declared permission) over per-handler discipline.

## Every privileged handler authorizes — server-side, centrally (Implementation)

- Every handler that **mutates state** or **returns data MUST** authorize the
  principal against the model, **on the server**, before acting. **There MUST be
  no privileged path that performs an action or returns data without a permission
  decision.**
- Authorization **MUST** be enforced at a **central decision point** (a shared
  `authorize(principal, action, resource)` / policy module / engine), not
  re-implemented ad hoc per handler — so the rules live in one auditable place
  and no handler can quietly diverge. Repeated hand-rolled `if role == "admin"`
  scattered across handlers is a drift signal.
- UI affordance (hiding a button, omitting a link) is **NOT** authorization; the
  server **MUST** refuse the action regardless of what the UI exposed.
- The tenant predicate (`multi-tenancy`) **MUST** hold **before** the permission
  check is meaningful: authorization is intra-tenant and presumes the record is
  already in the caller's tenant. A permission check on a wrong-tenant record is
  still a cross-tenant leak; compose the two, never substitute one for the other.

## Least privilege (Implementation)

- Roles/policies **MUST** grant the **minimum** permissions needed for the
  function. Default roles **SHOULD** be narrow; broad or superuser grants
  **MUST** be deliberate, few, and recorded.
- Proliferating roles to encode per-record or contextual rules (**role
  explosion**) is the signal RBAC is the wrong model for that rule class —
  **SHOULD** move it to ABAC/ReBAC rather than minting another role.

## Authorization is tested (Verification)

- A **negative guard test MUST exist**: a principal **without** the required
  permission, calling a state-changing or data-returning handler, **receives
  403/404 — never the action's effect or the protected data**. This is the guard
  branch the `verification` evidence gate requires for the authorization
  acceptance criterion; the permitted principal succeeding (happy-path-green) is
  necessary but **not** done.
- The test **MUST** drive the **real enforcement path** (the actual handler /
  decision point), not a unit stub that hard-codes "allowed" — otherwise it
  proves nothing about the check that ships.
- For each capability with a permission requirement, **both** the permitted
  (succeeds) and the denied (refused) cases **SHOULD** be exercised, so the
  guard branch is shown to exist and not be vacuously open.

## Boundary with neighbors

- For **who the principal is** (signup, login, sessions, account bootstrap)
  defer to `auth`; do not restate it here. This concern consumes the principal
  and decides what it may do.
- For **is the record even in the caller's tenant** defer to `multi-tenancy`;
  that predicate precedes — and never replaces — the permission check here.
- For general hardening (injection, CSRF, secrets, TLS) defer to
  `security-owasp`; missing/broken authorization is its Broken Access Control
  case, given a concrete model and per-handler discipline here.

## Quality Gates

- Permission **model recorded in an ADR** (RBAC / ABAC / ReBAC or a named
  combination) with its selection-criteria justification and **PDP/PEP
  placement** — not defaulted implicitly.
- **Deny-by-default**: verifiable in review that no state-changing or
  data-returning handler is reachable without passing a permission decision; a
  handler with no check is a defect, not a public endpoint.
- **Every privileged handler authorizes** server-side at a **central decision
  point**; no path acts or returns data without a permission decision, and UI
  hiding never stands in for a server check.
- **Tenant predicate precedes permission**: the `multi-tenancy` scope holds
  before the authorization check; neither substitutes for the other.
- **Least privilege**: default roles are narrow; broad/superuser grants are
  deliberate and recorded; rules are not encoded as role explosion.
- A **negative authorization guard test** exists and ran green against the real
  enforcement path: an unauthorized principal calling a state-changing /
  data-returning handler is refused (403/404), not served the effect or the
  data — ties to the it.39 guard-branch gate and the handler-authz defect family.
