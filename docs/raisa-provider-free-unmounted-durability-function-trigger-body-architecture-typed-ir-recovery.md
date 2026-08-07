# Durability function-and-trigger-body typed-IR recovery

Date: 2026-08-07

Status: normative Sol recovery frozen before replacement candidate generation

Rejected typed candidate content digest:
`sha256:f8afd0ce97169b0fae926dbe7999b9961d9be7506f711de579a3c035f75b2064`

Immutable parent digest:
`sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8`

## Reason for replacement

The second uncommitted candidate is structurally typed in appearance but not
mechanically lowerable. Whole-object schema constants freeze contradictions
instead of detecting them. Instruction effects are copied from body-wide
summaries rather than derived from operands; DML nodes target or bind the wrong
relations; trigger predicates use illegal row-image relations; branch terminals
are unreachable or apply to the wrong `TG_OP`; and opaque profile and whole-row
derivation labels leave SQL meaning to a future renderer.

The candidate is rejected in
`orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-typed-candidate-sol-rejection.md`.
It is negative evidence only. No body, predicate, effect or graph element from
it is presumed correct.

## Replacement construction boundary

The replacement retains only independently checked static envelopes:

- exact immutable parent binding and the twenty-six closed recovery operations;
- full support, nine entry-point and thirteen trigger-function signatures;
- thirteen complete trigger declarations;
- qualified identifier and column-type catalogues;
- closed value-free failure registry;
- exact trigger applicability/return matrix; and
- unchanged API Spine, role, data, provider and runtime boundaries.

Predicates, derivation profiles, body programs, effects and call graph are
rebuilt from zero. The following repository-local implementation support is now
permitted inside this tranche:

- one deterministic offline contract builder under `scripts/`;
- one importable deterministic semantic validator under `scripts/`;
- the generated contract and structural JSON Schema; and
- focused static/adversarial tests.

The builder and validator may read only the accepted parent, the closed
repository-authored body manifest embedded in the builder, and the generated
candidate. They may not render SQL or contact a database, source, provider,
network service or product path.

## Closed typed IR

The replacement IR has no `PROFILE_EVAL`, `DERIVE_COLUMN_VALUE`, unproduced
control fact, semantic step label, authored node effect or authored graph fact.
It consists only of discriminated typed nodes whose operands determine their
meaning:

- `ASSERT_ISOLATION(required)`;
- `DERIVE_BINDING(capability, arguments, output)` through the one allowlisted
  support helper;
- `SELECT_EXACT` and `SELECT_SET` with qualified relation, selected columns,
  exact predicate AST, cardinality, stable ordering and explicit output row
  type;
- `LOCK_EXACT` with qualified relation, exact predicate, key columns, mode and
  ordinal;
- `LET` with an explicit typed expression and definitely assigned output;
- `ASSERT` with explicit predicate and one closed failure;
- `IF` and `SWITCH_TG_OP` with inline child nodes, convergence and complete
  terminal coverage;
- `INSERT` and `INSERT_OR_RELOAD_COMPARE` with ordered target-column/value
  bindings and exact winner predicate/cardinality;
- `UPDATE` with exact key/predicate, set bindings and affected cardinality;
- the sole `DELETE_SOURCE` with exact source relation, key predicate, bound and
  cascade false;
- exact allowlisted support call;
- typed row/composite/trigger return; and
- value-free raise plus propagate-only `40001`/`40P01` behavior.

Composite results are never opaque constants. `COMPOSITE_CONSTRUCT` binds every
field, in the catalogue's exact order, to a typed operand expression. The sole
`DELETE_SOURCE` also assigns its bounded affected-row count as
`pg_catalog.bigint`, so the purge result is mechanically constructed from the
actual delete effect rather than authored summary text.

Expression leaves are only typed input/local/row-column/trigger-column/system
references or typed constants. Every row-column reference identifies symbol,
qualified relation, column and type. Exact operators close equality/order/null,
Boolean composition, `IS DISTINCT FROM`, arithmetic, timestamp interval,
fixed-key JSON extraction/cast, current-XID32/`xmin`, count, canonical digest,
UUID generation, closed composite construction, closed case expressions and a
typed `MIN_FIELD` over one already selected complete relation set. A
`SELECT_SET` assigns `<qualified-relation>[]`; `MIN_FIELD` identifies one of
that set's selected columns and returns exactly its catalogued type. Each
operator has fixed arity and result typing. Complex outcomes are expressed as
nested typed expressions and branches, never named profiles.

## Non-authorable derived evidence

The validator walks operands and control flow to derive:

- node and body relation/column reads;
- inserts, updated columns and the one allowed delete relation;
- locks, modes and acquisition order;
- support-call edges;
- reachable failures and terminals;
- definite symbol assignment and use;
- per-`TG_OP` legal `OLD`/`NEW` access;
- path-sensitive effects and output cardinality; and
- graph acyclicity and sibling-call absence.

The generated contract stores body summaries only as reproducible evidence.
Those summaries and the stored call edges must equal validator output exactly.
No local effect field exists on an instruction node. Stored graph Boolean facts
are absent.

## Construction cohorts

Replacement generation is admitted only in this order:

1. typed IR grammar, type/identifier catalogues, validator and digest/schema
   mechanics;
2. producer and admission bodies, including exact command proof, retained-first
   replay and authenticated first cross-position conflict;
3. coordinator plus lifecycle, key, consumption and retention bodies;
4. thirteen trigger bodies with complete `TG_OP` control flow and legal row
   images; and
5. aggregate summaries, exact positional schema, resealed adversarial packet
   and fresh candidate-independent veto.

Each cohort must pass the semantic validator before the next is generated. A
cohort failure cannot be concealed by regenerating a schema constant or digest.

### Admission lock feasibility correction

The earlier plan wording requiring the admission receiver to lock retained
admission and receipt rows is superseded. PostgreSQL row-locking selection
requires target-table update privilege, which would contradict the frozen
receiver ceiling of exact reads plus admission `INSERT`. Admission therefore
performs retained-first exact `SELECT_SET`/`SELECT_EXACT`, then relies on the
accepted unique coordinates and `INSERT_OR_RELOAD_COMPARE` with full immutable
winner comparison for concurrency. It acquires no admission or receipt row
lock and receives no `UPDATE` privilege. The coordinator, under its distinct
security-definer owner and role boundary, retains its separately ordered locks.

## Mandatory reproduced attacks

The final adversarial packet must reject, after refreshing candidate and schema
digests:

- an outbox insert retargeted to the alias relation;
- a missing stream-head update effect as derived from operands;
- any `DERIVE_COLUMN_VALUE`, `PROFILE_EVAL` or unproduced control symbol;
- an appointment or stream-head trigger reading a diary-event row image;
- an event-specific return placed before its proof or outside its `TG_OP` arm;
- UPDATE returning `OLD`, an incomplete trigger switch or an unreachable proof;
- coordinator terminal replay from input non-nullness or an unassigned result;
- source/conflict persistence before first-source/key authentication;
- audit classification without independent OLD and NEW command lookups;
- any authored effect/graph fact, swapped body, lock removal/reorder, widened
  product read, call cycle, signature/declaration/terminal swap, raw SQL,
  transaction control, DDL, runtime/product authority or unknown opcode.

## Unchanged authority and claim ceiling

This recovery remains pure, provider-free, unmounted and repository-local. It
creates no SQL, DDL, migration, function, trigger, grant, role, relation,
database object, source/feed/watcher/listener, operational state, credential,
application/API/Diary change, product/patient read, command/write path, runtime
wiring, deployment, production, release, Pages rebuild or protected-ref
movement.

Passing the replacement proves only a machine-readable body architecture. SQL
lowering, PostgreSQL parsing, inert DDL rehearsal, database-backed execution and
operational use remain later gates.
