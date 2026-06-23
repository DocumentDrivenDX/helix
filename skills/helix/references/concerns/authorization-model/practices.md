# Practices: Authorization Model

These practices govern the **permission model and its enforcement** — *what* an
authenticated principal may do, and the discipline that every privileged handler
asks and refuses by default. For the family ownership table (auth /
authorization-model / multi-tenancy / security-owasp) see
[README-auth-family.md](../README-auth-family.md). Their one job is to make the
**missing / mis-placed authorization check** unreachable and
**reviewer-checkable**. Each MUST/SHOULD below is written so a reviewer can
confirm or refute it against the diff and the running system.

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
