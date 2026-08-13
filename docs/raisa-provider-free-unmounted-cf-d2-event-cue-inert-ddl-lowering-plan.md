# Provider-free unmounted CF-D2 event and cue inert-DDL lowering plan

Date: 2026-08-13

Timestamp: 2026-08-13T18:14:01+10:00 (Australia/Brisbane)

Status: `frozen_for_deterministic_inert_ddl_execution`

Planning baseline: `bc21d637632f239243d384811781b8ca9b539cb8`

Accepted representation source: `16ec7993ee3c46d83772f47aa7dab61fc1fcb7ed`

Accepted representation contract SHA-256:
`sha256:ff72cb2b6458193fb723b19209ac0ca487d3fdda5846d43ccdfafb6986957f64`

Target result: `raisa_provider_free_unmounted_cf_d2_event_cue_inert_ddl_lowering_pass`

## Objective

Mechanically lower the exact accepted seven-relation CF-D2 representation into
one byte-stable PostgreSQL-16 DDL text artifact and prove its structural
coverage without opening a SQL parser, database driver, connection, process or
migration path. The output is inert evidence, not an applied schema.

Events and cues remain acceleration hints. The DDL may describe storage for
opaque coordinates, receipts and refresh obligations, but none becomes Diary
truth, a Context Frame, confirmation evidence, command authority or a command
receipt. Display still requires a fresh authorised read; mutation still uses
the existing backend command plane and rechecks current authority and truth.

## Frozen lowering

The renderer accepts no caller-selected input or output. It reads only the
hash-bound accepted representation contract and one new closed lowering
contract, then writes only these fixed continuity artifacts:

- `event-cue-schema.sql.inert`;
- `inert-ddl-manifest.json`; and
- `provider-free-unmounted-inert-ddl-evidence.json`.

The SQL text contains exactly:

1. one dedicated `emr4_context_fabric_cue` schema declaration;
2. three scalar domains for exact SHA-256 digests, non-empty opaque IDs and
   positive 64-bit integers;
3. seven `CREATE TABLE` statements in accepted relation order, with the exact
   fifty fields, nullability, seven primary keys, three unique keys and closed
   allowlists/truth-table checks; and
4. seven named foreign-key additions, including the accepted nullable,
   initially-deferred terminal-receipt-to-obligation reference.

All identifiers and literals are repository-owned constants. There is no raw
SQL input, environment-selected path or runtime value.

## Enforcement honesty

Every one of the representation contract's nineteen relation check labels has
one exact lowering disposition. Eighteen are represented by a named SQL check
constraint (sometimes redundantly reinforcing a scalar domain); the semantic
label `coordinate_is_non_authoritative` is emitted only as a verified inert
annotation because no row constraint can make a coordinate non-authoritative.

The seven exact `mutable_fields` lists are also preserved as inert manifest and
SQL-comment declarations. They are not described as update enforcement.
Enforcing pending-only coalescing, immutable rows or generation-fenced updates
requires the separately closed transaction/privilege layer. No trigger,
function, rule, role, grant, revoke or procedure is invented in this tranche.

The five accepted transaction protocols and all external-authority facts are
bound into the manifest as unlowered requirements. A candidate that claims
they were proved by DDL fails admission.

## Static admission

The standard-library recognizer independently checks UTF-8/LF shape, exact
header and phase order, statement inventory, object/field/key/reference/check
census, accepted source hash, artifact digest and the absence of all forbidden
statement families. It also requires byte equality with the deterministic
canonical render. This proves exact closed-subset structural lowering only; it
does not prove that PostgreSQL parses or accepts the text.

At least 64 independently generated hostile candidates must fail closed,
covering removed or renamed relations, domains, keys, references and checks;
changed types/nullability/allowlists; added payload columns; reordered or extra
statements; DML, transaction control, functions, triggers, roles, privileges,
extensions and database-connect metacommands; and false transaction/runtime
claims. Canonical input and output bytes must remain unchanged throughout.

## Acceptance

- The lowering contract passes its closed JSON Schema and semantic gate.
- The accepted representation source, contract path and SHA-256 bind exactly.
- Two isolated renders are byte-identical.
- Exactly seven relations and fifty exact columns are covered.
- Seven primary keys, three unique keys, seven references and all nineteen
  check labels receive their frozen, honestly classified disposition.
- The exact mutability declarations survive without an enforcement claim.
- The canonical SQL and manifest pass the static recognizer.
- At least 64 hostile variants fail closed without changing canonical bytes.
- Evidence records zero database/source connections, executions, migrations,
  runtimes, provider calls, commands/writes and product/patient data.
- Focused lineage tests, Ruff, canonical fast verification and Git whitespace
  pass.

## API Spine classification

This remains an internal non-invasive async architecture artifact. GraphQL is
unchanged and read-only. REST/OpenAPI remains the sole command plane. No route,
subscription, acknowledgement endpoint, source read or mutation is added.

## Worker and recovery decision

The parent binding, renderer, recognizer and tests are small and tightly
coupled, so Sol owns implementation and acceptance under the worker-economy
rule. No subagent, external worker, independent verifier or provider is
selected. A mechanical defect may be repaired inside this frozen boundary.
Any need to connect to PostgreSQL, execute SQL, add transaction semantics or
choose an operational persistence policy stops this tranche rather than
broadening it.

## Next descendant

If accepted, the next dependency-satisfied tranche is a provider-free
disposable PostgreSQL-16 parse-and-catalogue admission rehearsal. It may apply
the exact inert artifact only inside a newly created isolated disposable
server and inspect catalogue shape, then destroy it. Transaction behavior,
concurrency, restart, delivery, retention, product wiring and migration remain
closed even there.

## Closed surfaces

No protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient client or real identity, database/source access, SQL or
migration execution, persistence, operational retention, watcher/listener/
worker runtime, provider/ADC, credential/IAM/network, executable tool,
command/write, GraphQL/OpenAPI route, deployment, production, release, Pages
or protected-ref movement is authorised. `docs/branding/` and every unrelated
untracked file remain preserved and excluded; staging is explicit-path only.
