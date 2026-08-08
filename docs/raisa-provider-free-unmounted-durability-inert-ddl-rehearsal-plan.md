# Provider-free unmounted durability inert DDL rehearsal plan

Date: 2026-08-07

Status: accepted after PostgreSQL-representability recovery and fresh
exact-HEAD independent veto

Normative PostgreSQL-representability recovery:
`docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-postgresql-representability-recovery.md`

Structural parent result:
`raisa_provider_free_unmounted_durability_migration_transaction_architecture_pass`

Structural parent source HEAD:
`c55d25d6c9704ae4612ef2d123158f71302ab411`

Structural parent contract:
`sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8`

Body parent result:
`raisa_provider_free_unmounted_durability_function_trigger_body_architecture_pass`

Body parent source HEAD:
`a93d07405ad35d7d6c0603065625c17ec14ab23e`

Body parent contract:
`sha256:b3eaa041dc96a6117957b9dd9bde0205afd1023fc521b3183410e7b3c4b8b1b1`

## Objective

Mechanically lower the two immutable accepted durability contracts into one
deterministic, repository-local PostgreSQL 16 DDL rehearsal without executing,
applying or connecting the output. The result must close the last translation
boundary between the accepted structural catalogue and the accepted typed body
programs: exact types, relations, constraints, forced RLS, roles, support
helper, nine entry points, thirteen trigger functions, thirteen trigger
declarations, revocations, grants and static catalogue/privilege expectations.

The intended result is
`raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_pass`.

This is a renderer and static-admission tranche only. The rendered text is an
inert evidence artifact with a non-runnable `.sql.inert` suffix outside
`alembic/**`. It is not a migration and is never sent to PostgreSQL in this
tranche.

## API Spine classification

This remains internal async durability implementation evidence. GraphQL stays
read-only and unchanged. REST/OpenAPI remains the sole command plane and gains
no operation. The existing signed update-confirm transaction remains the only
future producer command boundary. Events, outbox rows, admissions, receipts,
anchors, checkpoints and rendered DDL are never current truth, command evidence
or command authority. No route, subscription, acknowledgement, fresh product
read, provider call or product write is added.

## Exact inputs

The renderer accepts no caller-selected contract or output path. It reads only:

1. the exact accepted structural parent JSON and Schema;
2. the exact accepted body parent JSON and Schema;
3. the existing accepted body validator and effective-parent derivation; and
4. one new closed lowering contract and Schema created by this tranche.

It verifies both parent contract hashes before deriving anything. Both parent
directories, builders, schemas, validators and tests are immutable inputs. The
new lowering contract binds their repository paths, source HEADs, hashes,
PostgreSQL major 16, exact observed opcode populations and exact output paths.

The accepted structural parent deliberately omitted executable function and
trigger bodies, while the accepted body child deliberately emitted no renderer
or DDL. This descendant may supersede only those two omission flags, and only
after both immutable hashes and the complete child body contract pass. The
supersession permits rendering the already accepted definitions solely into the
fixed inert evidence artifact. It does not alter either parent, create a
migration or grant execution/application authority.

## Allowed artifacts

This tranche may add only:

- this plan, one design and one threat-model delta;
- one closed lowering contract and whole-contract JSON Schema under
  `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/`;
- one deterministic standard-library-only renderer/static recognizer;
- one canonical `durability-schema.sql.inert` artifact and one closed JSON
  render manifest in that same continuity directory;
- authored-synthetic static and hostile-mutation tests;
- bounded worker/reviewer packets and receipts; and
- closeout, acceptance, error-register and Continuity/Compass artifacts.

No parent artifact may change. No new dependency, package download, external
parser, subprocess, shell, socket, database driver or environment-selected path
is permitted.

## Effective catalogue derivation

The renderer must independently derive one `EffectiveCatalogueV1` by applying
the accepted child's exact ordered 26-operation
`structural_feasibility_recovery_v1` to the immutable structural parent. It
must reconcile the result against the child's effective signatures, roles,
trigger declarations and qualified identifier catalogue. A missing, additional,
reordered-with-effect or unknown recovery operation fails before output.

The immutable parent catalogue contains exactly:

- PostgreSQL major 16 and the accepted isolation/XID rules;
- one `emr4_context_fabric` schema;
- six accepted builtin type references, four domains, seventeen enums and the
  effective composite population;
- eighteen fabric relations with exact columns/defaults, named keys, indexes,
  foreign keys, delete actions and checks;
- eight roles/principals with exact login/inheritance/ownership ceilings;
- forty-four forced-RLS policies;
- the one stream-scoped `session_binding_allows_v1` support helper;
- nine entry-point signatures and programs;
- thirteen trigger-function signatures and programs;
- thirteen exact trigger declarations; and
- twenty-five invariant-enforcement bindings.

The four existing `public.*` application relations are evidence references,
not objects created or altered by the artifact. The renderer may grant the
accepted exact owner `SELECT` ceiling on them only in the frozen privilege
phase; it may not emit application DDL or DML.

## Closed lowering contract

The renderer is a total closed lowering over the accepted candidate, not a
general SQL generator. The accepted vocabulary declares 22 instruction opcodes
and 34 expression opcodes. The immutable body population actually uses 21 of
the instruction opcodes and all 34 expression opcodes; `DERIVE_BINDING` is the
sole declared but unobserved instruction. The renderer must explicitly
reconcile those exact populations before lowering. It implements the 21
observed instruction forms and all 34 expression forms; an encountered
`DERIVE_BINDING`, unknown, newly introduced, malformed or differently typed
node fails because the parent hash-bound programs contain no such occurrence.

### Identifiers and literals

- Every schema, object, role, column, type, policy, constraint, trigger and
  function identifier comes from the effective catalogue and is emitted with
  deterministic PostgreSQL identifier quoting.
- No raw identifier, SQL fragment, format string or interpolation value comes
  from a body node.
- Constants use one closed renderer per accepted type. Text/domain/enum values
  are single-quoted with doubled quotes; UUID, timestamp, Boolean, integer,
  JSONB and array values receive explicit qualified casts.
- No value derived from a patient, product row, environment variable,
  credential or runtime source can enter the artifact.

### Canonical digest primitive

`CANONICAL_DIGEST` receives one exact lowering rather than an invented helper.
The lowering contract enumerates every accepted digest profile and exact
ordered operand type tuple. The preimage is UTF-8 and contains the profile plus
each operand as an unambiguous type-tagged, byte-length-prefixed value. Null has
one distinct marker. UUID is lowercase canonical text; integers and Boolean are
locale-free; enums/domains use their exact text; `timestamptz` is UTC with six
fractional digits. The expression uses only qualified PostgreSQL-16 core
`convert_to`, `octet_length`, `sha256` and `encode`, and returns exact
`sha256:<64 lowercase hex>` text cast to the accepted digest domain. No
extension, helper function, locale, `DateStyle`, `TimeZone` or search-path
choice may change the preimage.

### Expressions and instructions

- Each accepted expression opcode has one precedence-safe parenthesized SQL
  expression template with fixed arity and type rules.
- `REF`, `FIELD`, `SYSTEM_XMIN`, `CURRENT_XID32`, `SESSION_USER`, JSON key
  extraction, exact JSON-key sets, arrays, composites, complete-set operations,
  `MIN_FIELD`, timestamp arithmetic and the sole UUID generator are explicit
  mappings; generic calls are impossible.
- Each accepted instruction opcode has one PL/pgSQL statement template.
  Select/lock cardinality, ordering and output shapes are preserved. Complete
  sets have deterministic ordering and a typed empty representation.
- Every `EXACTLY_ONE` read, lock, write or reload has one implicit value-free
  failure mapping: zero or non-unique cardinality raises registered
  `F_CARDINALITY`, SQLSTATE `CF004`, with its stable reason code and no row
  value. PostgreSQL's default `NO_DATA_FOUND`, `TOO_MANY_ROWS`, `P0002`,
  `P0003`, `P0001` or class `42` errors are not accepted substitutes.
- `INSERT_OR_RELOAD_COMPARE` may translate only exact `unique_violation` for
  the one effective-catalogue unique constraint whose ordered columns equal its
  named conflict key. The handler reads `CONSTRAINT_NAME`, rethrows every other
  violation unchanged, and reloads the expected winner using both the conflict
  key and accepted `winner_predicate`. A missing or mismatching winner raises
  `F_CARDINALITY`/`CF004`. It must not use `ON CONFLICT DO NOTHING`, perform a
  no-op update, swallow any other error or hide a missing/mismatching winner.
- `PROPAGATE_RETRYABLE` is an inert control assertion, not an exception handler.
  The renderer may eliminate only the accepted canonical constant-false retry
  marker wrapper after proving its exact `40001`/`40P01` set and
  `internal_retry: false`; it may not add a catch/retry path.
- `RAISE` emits only the registered five-character SQLSTATE and stable
  value-free reason/body metadata. No row value, identifier, UUID, digest,
  packet or credential is interpolated.
- Trigger programs receive only exact legal `TG_OP`, `OLD` and `NEW` row-image
  access and the accepted `RETURN NEW`, `RETURN OLD` or `RETURN NULL` terminal.

The renderer must prove all 22 immutable parent programs are consumed exactly once and every
node/expression is lowered exactly once or is the one formally eliminated
constant-false retry marker. No prose, derived-effect summary or invariant
label supplies executable semantics.

The normative PostgreSQL-representability recovery is the sole permitted
effective-body delta. It adds one typed immediate appointment guard, making
the effective population nine entry points, fourteen trigger functions,
fourteen trigger declarations and twenty-three programs. It also replaces six
unrenderable trigger-row `xmin` references with exact keyed pre-effect
reselections or a recorded paired-guard dependency. Neither the immutable body
parent nor its historical thirteen-function population is edited.

## Canonical render phases

The `.sql.inert` artifact has exactly six ordered phases:

1. exact role/schema/type/relation/constraint/index/forced-RLS catalogue and the
   sole support helper;
2. the nine entry-point functions in accepted renderer order;
3. the fourteen effective trigger functions in recovered renderer order;
4. the fourteen effective trigger declarations in recovered order;
5. `PUBLIC` revocation followed by the exact owner, receiver and runtime grants,
   with migration-only trigger-install authority absent from runtime grants;
6. non-executed catalogue and privilege expectation comments whose exact facts
   are also present as typed JSON manifest assertions.

There is no top-level `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`, `DO`, `COPY`,
`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `SET ROLE`, psql meta-command,
extension creation, external/file/network access or conditional installer.
Body-local DML is admitted only when derived from the accepted typed program.

Every security-definer function has its exact owner, language, strictness,
volatility, parallel safety and fixed `pg_catalog, emr4_context_fabric` search
path. `PUBLIC` execute is revoked before any exact runtime execute grant. Trigger
functions have no runtime execute grant. Forced RLS, owner and privilege
assertions must reconcile exactly with the effective catalogue.

## Static grammar and admission

No database or external SQL parser is used. A second standard-library-only
static recognizer, separate from the emission methods, tokenizes the canonical
artifact and validates the closed generated subset:

- UTF-8/LF encoding, one fixed header, no NUL/control characters and balanced
  quotes, dollar tags, parentheses and statement terminators;
- exact six phase markers and exact statement-kind/order inventory;
- no unrecognized top-level token sequence or forbidden statement family;
- exact function headers, bodies, terminators and trigger declarations;
- no unqualified fabric/application identifier and no attacker-controlled
  search-path component;
- exact object, column, constraint, policy, body, trigger, revoke and grant
  inventory against the typed render manifest; and
- artifact SHA-256, parent hashes, effective-catalogue digest, renderer version,
  byte count, statement count and per-phase spans.

This recognizer proves conformance to the renderer's closed PostgreSQL-16
subset, not equivalence to a PostgreSQL server parse. Actual PostgreSQL parsing,
catalogue creation and behavior remain later gates.

## Acceptance

Acceptance requires all of the following:

1. both parent hashes and parent source bindings are exact and parent artifacts
   remain byte-unchanged;
2. effective-parent recovery is complete, deterministic and equal to the
   accepted child summaries/catalogues;
3. the lowering contract and Schema position-close every phase, statement
   family, digest profile, observed opcode/type combination and output path;
4. two isolated renders produce byte-identical SQL and manifest artifacts;
5. the static recognizer accepts the canonical artifact and rejects any unknown
   token, unbalanced delimiter, extra/missing/swapped statement or phase;
6. all exact types, eighteen fabric relations, constraints/indexes, forty-four
   RLS policies, roles and the sole support helper reconcile with the effective
   catalogue, while no `public.*` object is created or altered;
7. exactly nine entry-point and fourteen effective trigger-function bodies are
   emitted in recovered order, every immutable and recovered body node is
   accounted for and no helper/overload beyond the one recovery-owned guard is
   introduced;
8. exactly fourteen effective trigger declarations bind the accepted or
   recovered table/timing/level/events/deferrability/function tuple, including
   the one immediate appointment guard;
9. every function header, owner, security mode, strictness, volatility,
   parallel safety and fixed search path matches the accepted signature;
10. revocations and grants match the exact effective role matrix, with no
    application DML, direct runtime durability DML, trigger-function execute,
    ownership, inheritance, bypass-RLS or broad `PUBLIC` authority;
11. digest lowering is profile/type position-closed, locale/timezone independent
    and rejects delimiter ambiguity, null/text collision and operand reorder;
12. exact unique-race reload/compare, retry propagation, value-free failures,
    trigger row-image legality and branch terminals survive static challenge;
13. digest-resealed hostile lowering/SQL mutations reject raw/dynamic SQL,
    unqualified identifiers, search-path widening, `SECURITY INVOKER`, missing
    revoke, added grant, application DML, `ON CONFLICT DO NOTHING`, swallowed
    error, internal retry, wrong SQLSTATE, wrong `OLD`/`NEW`, altered digest
    profile, omitted body/trigger/policy/constraint, added helper/overload,
    reordered phase, top-level DML/transaction control, psql meta-command,
    extension/file/network operation or output-path escape;
14. imports and monkeypatched sentinels prove no subprocess, socket, database,
    SQLAlchemy/psycopg, HTTP, provider, environment-selected output or Alembic
    path is reachable;
15. Ruff, JSON Schema, deterministic artifact regeneration and explicit Git
    pre/postflight pass; and
16. one fresh exact-HEAD independent veto reports no material finding and leaves
    its bounded review worktree unchanged.

## Data, provider, cost and licence posture

- Data: accepted repository-authored architecture metadata and newly authored
  synthetic hostile mutations only.
- Patient/product/protected/historical-PHI data: none.
- Provider/model during implementation: DeepSeek may receive only the frozen
  repository-local packet; final Gemini review receives only exact allowed
  repository paths. No provider product path or patient/product data.
- Database/source/network/browser contact: none.
- Cloud/provider cost: zero product/cloud-runtime cost; ordinary bounded worker
  and verifier use only the already allocated development harness.
- Licence: no external corpus, source or dependency.

## Worker allocation

Sol owns this plan, architecture meaning, recovery and acceptance. After plan
admission, DeepSeek V4 Flash/high through Claude Code `--bare` may own the
separable mechanical renderer, lowering contract/Schema, inert artifacts and
focused tests in one exact task worktree. Gemini 3.6 Flash/high through a fresh
Antigravity project owns read-only independent veto only. Neither worker may
self-accept, change parent artifacts, write the primary worktree, push, move a
protected ref or broaden any boundary.

## Recovery and stop

One deterministic mechanical implementation defect may receive one bounded
same-lane correction. Any conceptual ambiguity in canonical digest encoding,
effective-parent derivation, instruction semantics, uniqueness handling,
cardinality, privilege order, security-definer behavior, trigger totality or
static-grammar claim invokes Sol's recovery lease and a fresh independent veto.
No rejected renderer or SQL artifact may be silently admitted.

Pause for Yuri only if recovery exposes a genuinely non-inferable product,
privacy, security, licence or operational outcome outside this plan. A routine
plan revision, worker failure, transport failure, test failure or exact
architecture-strengthening correction is not a user gate.

## Claim boundary and next dependency

Passing proves only that one deterministic renderer can lower the two accepted
contracts into a byte-stable inert SQL artifact conforming to a closed static
PostgreSQL-16 subset and exact catalogue/privilege manifest. It does not prove
that PostgreSQL parses or accepts it; create any schema/object/role/function/
trigger/grant; execute transaction or trigger behavior; establish live
privileges, concurrency, rollback, retry, performance or migration safety;
contact a database/source; process patient/product data; wire runtime; add a
command; deploy or establish production safety.

Only after this tranche passes may a separate provider-free disposable local
PostgreSQL parse/catalogue rehearsal be considered. An applied Alembic
migration, application transaction integration, operational credentials,
database-backed behavior/concurrency, live source/product access, deployment
and production remain later separately bounded gates.
