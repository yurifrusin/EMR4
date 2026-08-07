# Durability function-and-trigger-body implementation recovery

Date: 2026-08-07

Status: normative Sol recovery frozen before corrected implementation

Rejected uncommitted candidate digest:
`sha256:c16930c2d6c400c93ea2c2b413ccf084ceb38c4f980fa4edae032b74e3112622`

Immutable parent digest:
`sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8`

## Rejection

The first implementation candidate is rejected before candidate commit or
independent-review admission. Its twenty-two programs point to one step each;
the steps contain ordered enum labels, separately declared relation effects and
predicates whose leaves are untyped strings. The whole-contract digest and
section seals prevent accidental drift, but they do not make those labels into
machine-lowerable bodies. A renderer would still have to invent operands,
cardinality, branch children, assignments, predicate-leaf meaning and terminal
behavior. Relation-wide read profiles are also not column-minimal for each
instruction, and stored call-graph booleans are assertions rather than derived
facts.

No SQL, DDL, migration, database/source/provider contact, product/patient data,
runtime wiring, commit, deployment, Pages action or protected-ref movement
occurred. The rejected files are an untrusted implementation source only.

## Corrected representation

The corrected contract must replace label-only substeps with ordered,
discriminated `instruction_node_v1` objects. Every node has one closed opcode
and the exact operands required by that opcode. The finite opcode family is:

- trigger-context and isolation assertions;
- binding derivation;
- exact-cardinality read and stable-key lock;
- typed assignment and digest derivation;
- typed predicate assertion and branch;
- bounded complete-set iteration;
- exact insert, immutable-winner reload/compare, exact update and the sole
  source-row delete;
- allowlisted support call;
- typed row/composite/trigger return; and
- value-free failure raise with retryable propagation only.

There is no generic instruction, statement, expression, call or identifier.
Each node must carry, as applicable:

- exact qualified relation and column refs;
- input and output symbol refs with declared types;
- cardinality and lock mode/order;
- a typed expression or predicate ref;
- exact branch-child node IDs and convergence/terminal rule;
- inserted/updated/deleted column-to-expression bindings;
- allowlisted call target and arguments;
- return source and cardinality or exact trigger terminal; and
- one closed failure ID.

Expressions are discriminated nodes, never free strings. `REF` selects only an
in-scope typed symbol, qualified row column, trigger system field or exact
primitive output. `CONST` carries a declared allowlisted type and closed value.
Every other operator has schema-fixed arity and operand types. `OLD` and `NEW`
column access is permitted only when the exact trigger event matrix admits that
row image. Fixed JSON keys, casts, current-XID32, system `xmin`, transaction
timestamp, `IS DISTINCT FROM`, timestamp-plus-minutes, canonical digest
profiles and UUID generation use their own typed nodes.

## Exact signature and trigger binding

The effective-parent derivation must emit full ordered signature objects, not
names or summary strings. Each of the nine entry points and thirteen trigger
functions binds exact input modes/types, output type/cardinality, language,
owner, executor, strictness, volatility, parallel safety, security-definer,
fixed search path, public-execute denial and invariant IDs. Every trigger
declaration additionally binds qualified relation, timing, row level, events,
deferrability, initially-deferred state and function.

All trigger functions have the uniform function signature result
`pg_catalog.trigger`. Operation-specific `RETURN_NEW`, `RETURN_OLD`,
`RETURN_NULL` and raise behavior exists only in typed terminal instructions and
the exact per-event return matrix; it is never substituted for the function
signature.

## Derived effects and graphs

Every instruction declares only its own exact column-minimal reads, locks and
writes. The validator walks the typed AST in deterministic order and derives:

- per-body read/lock/insert/update/delete column sets;
- stable lock order and modes;
- call edges;
- reachable failures and terminals;
- trigger row-image use; and
- output source/cardinality.

The derived body summary must equal one separately frozen body-specific
summary. Relation-wide profiles are forbidden unless the instruction actually
references every listed column. Adding an otherwise valid catalogue ref to the
wrong node or body fails.

Call edges are structured `{from,to}` objects with fully qualified enum-bound
IDs. Acyclicity, no entry-point sibling calls and no trigger sibling calls are
computed by tests; trusted Boolean declarations are removed.

## Exact semantic corrections discovered in implementation audit

- Admission separates exact primary replay, existing conflict replay,
  authenticated first-source handling, cross-position digest-reuse detection
  and new primary/conflict persistence. A new cross-position conflict cannot be
  persisted before the exact source row and key membership are authenticated;
  only already retained exact evidence is source-independent.
- The audit guard classifies both audit images by exact command membership. It
  therefore performs an exact-cardinality read of the matching qualified
  `public.appointment_command_idempotency` row and only the columns needed for
  practice, command identity, operation and route classification. An audit row
  alone cannot prove the command family.
- `cf_guard_stream_head_v1` is UPDATE/DELETE-only and contains no INSERT arm.
  Registration's position-zero insert is validated only by
  `cf_fence_stream_head_v1`.
- Coordinator terminal replay is derived from stored terminal generation,
  checkpoint and result integrity. It has no caller terminal-reason symbol.
  Terminal-reason equality remains exclusive to
  `consume_observer_generation_v1`.

## Whole-contract schema closure

The schema must use ordered `prefixItems` or body-specific `const` definitions
for all twenty-six recovery operations, twenty-two signatures, thirteen
trigger declarations, twenty-two programs, instruction nodes, branches,
symbols, exact summaries and terminals. Global membership enums alone are not
sufficient. Digest-resealed mutations must fail even when they reuse an
otherwise valid instruction, relation, column, predicate, return or program ID
in the wrong body or position.

Adversarial acceptance must include unknown expression op/leaf, invented or
removed symbol, swapped instruction/body, missing provenance proof, changed
OLD/NEW column, lock removal/reorder, widened product read, changed owner/output,
swapped trigger function/declaration/return, invented recovery operation, call
edge cycle and a refreshed top-level digest/schema digest.

## Recovery ownership and next review

This is a conceptual implementation defect, so Sol owns recovery under
`docs/ariadne-orchestrator-recovery-lease.md`. The rejected worker artifacts
cannot self-pass or be silently admitted. Separable implementation lanes may
author the typed body IR/schema and independent derived-effect/adversarial
tests, but Sol reconciles them. The corrected exact candidate requires fresh
deterministic acceptance and a candidate-independent exact-head veto.

All original plan, structural-feasibility recovery, API Spine, data, provider,
cost, runtime, deployment, release, Pages and protected-ref boundaries remain
unchanged.
