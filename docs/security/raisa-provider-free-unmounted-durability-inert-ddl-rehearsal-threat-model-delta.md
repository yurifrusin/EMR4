# Threat-model delta: durability inert DDL rehearsal

Date: 2026-08-07

Status: PostgreSQL-representability recovery active after rejected worker
implementation

Normative PostgreSQL-representability recovery:
`docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-postgresql-representability-recovery.md`

## Scope and assets

This delta covers deterministic repository-local lowering of the accepted
durability structural and body contracts into inert PostgreSQL-16 text. It does
not cover a PostgreSQL parser, a database, migration execution, runtime wiring
or product data.

Protected assets are the immutable parent contracts; exact effective
catalogue; tenant/source/stream and principal separation; security-definer
search path; product-table read-only ceiling; exact body effects and failures;
trigger totality; revoke/grant order; byte-stable artifact provenance; and the
separation between rendered evidence and executable authority.

## Trust boundaries

The boundaries are accepted parent JSON to effective-catalogue derivation;
typed body IR to closed lowering; typed render plan to inert text; inert text
and manifest to an independent static recognizer; and accepted static evidence
to a later separately authorised disposable PostgreSQL gate. No boundary in
this tranche crosses into a database, product service, provider product path or
runtime credential.

## Threats and mitigations

| Threat | Mitigation | Residual risk |
|---|---|---|
| Renderer uses a different or modified parent | Exact fixed paths, source bindings and canonical hashes are verified before and after rendering; effective recovery is rederived and reconciled to child summaries. | Git history authenticity and protected integration remain separate controls. |
| Prose or summary causes executable invention | Every SQL expression/statement descends from a closed typed render node and exact body operand; unknown/missing semantics fail. | The correctness of each lowering template requires independent review. |
| Identifier or literal injection | Identifiers come only from position-closed catalogues and deterministic quoting; constants have type-specific literal renderers; no raw SQL/fragments or caller strings. | PostgreSQL parser behavior remains unproved until the next gate. |
| Output is accidentally treated as a migration | Fixed continuity-directory path, `.sql.inert` suffix, non-execution header, no Alembic artifact/import and tests forbidding database/subprocess paths. | A human could manually rename/run evidence outside this authority. |
| Static validation silently contacts PostgreSQL | Standard-library-only imports, monkeypatched connection/process/socket sentinels and no external parser/dependency. | Static recognition is deliberately weaker than a server parse. |
| Canonical digest is ambiguous or environment-dependent | Exact profile/type tuples; UTF-8 type-tagged byte-length framing; distinct null marker; locale-free scalars; UTC microsecond timestamps; fully qualified core SHA-256 functions. | Cross-language/server execution vectors require a later database-backed gate. |
| Digest helper widens body/call authority | Digest expression is inlined; no helper, extension or new callable surface is introduced. | Inlining increases artifact size and review burden. |
| Unique race is swallowed or changes a row | Only `INSERT_OR_RELOAD_COMPARE` admits exact `unique_violation` translation; expected winner is reloaded and compared; no `DO NOTHING`, no-op update or broad exception handler. | Real concurrent behavior remains unproved. |
| Unique handler catches the wrong constraint or invents an error | The renderer proves one effective-catalogue unique constraint exactly matches the ordered conflict columns, checks PostgreSQL `CONSTRAINT_NAME`, rethrows every other violation and maps a missing/mismatching winner only to registered value-free `F_CARDINALITY`/`CF004`. | Actual concurrent catalogue behavior remains for the disposable database gate. |
| Declared and observed opcode populations are conflated | Admission fixes 22 declared/21 observed instruction opcodes with only `DERIVE_BINDING` absent, and 34 declared/34 observed expression opcodes; any drift or encountered unobserved form fails before emission. | A later parent revision requires a new descendant rather than compatibility lowering. |
| Parent omission flags are treated as broad implementation authority | An exact descendant activation delta requires both immutable hashes and all 22 accepted programs, and opens only fixed-path inert rendering; neither parent is mutated and execution remains closed. | Any later migration/application requires fresh separately bounded authority. |
| Retry marker becomes internal retry/catch | Exact constant-false marker shape and SQLSTATE set are verified then erased; renderer emits no retry loop or catch. | Caller retry behavior remains a later integration gate. |
| Security-definer resolves attacker objects | Qualified identifiers, fixed search path, no dynamic SQL, non-login owners and exact public revocation. Static recognizer rejects search-path drift. | Actual `proconfig`, ownership and RLS behavior require catalogue readback later. |
| Application product DML or object DDL is introduced | `public.*` is reference-only; typed statement inventory forbids application create/alter/DML and grants owner only exact accepted SELECT. | Existing application schema compatibility requires later parse/catalogue rehearsal. |
| Trigger function gains runtime execute | Exact grant manifest contains no trigger-function runtime execute; any added grant or missing revoke is hostile-test rejected. | Live role membership is not assessed. |
| RLS or owner privilege is weakened | Exact forced-RLS/policy inventory and role matrix are compared from both typed plan and independent tokenized text. | Runtime owner/RLS semantics need PostgreSQL. |
| Extra statement hides in comments/dollar body | State-aware tokenizer, exact byte spans, balanced dollar tags and top-level statement inventory; control/meta tokens rejected. | This is a closed-subset recognizer, not a general SQL parser. |
| Top-level transaction/DML creates side effects if run | These statement families are forbidden at top level; body DML is bound only inside exact functions. | The artifact still represents definitions and must not be run in this tranche. |
| Renderer writes outside evidence directory | Output constants resolve beneath one exact continuity directory; caller path/environment selection is absent; path-escape tests fail closed. | Filesystem compromise is outside this model. |
| Manifest/hash is trusted instead of semantics | Independent recognizer and digest-resealed hostile plan/text mutations test structure after evidence refresh. | Exhaustiveness of adversarial tests remains reviewable. |
| Render order creates transient broad authority | Objects/bodies/triggers precede revocations/grants; `PUBLIC` revocation precedes exact runtime grants; migration-only installation authority is not a runtime grant. | A real migration needs transaction/rollback and lock planning in a later gate. |
| Static success is overclaimed as PostgreSQL validity | Evidence and result labels explicitly say closed-subset static rehearsal only. PostgreSQL parse/catalogue/behavior are separate gates. | Server-specific grammar or semantic failures may still be found later. |
| Empty complete sets are miscounted | `COUNT` lowers to `coalesce(array_length(set, 1), 0)::bigint`; hostile tests require zero for a typed empty array and forbid bare `array_length`. | Server execution remains for the later disposable database gate. |
| Policy creation references a missing helper | Relations precede the support helper and the helper precedes every dependent RLS policy; manifest dependency edges and statement order are exact. | Live dependency resolution is not yet executed. |
| Deferred trigger syntax is only superficially trigger-shaped | Every deferrable row fence emits PostgreSQL-16 `CREATE CONSTRAINT TRIGGER` order; immediate guards emit ordinary `CREATE TRIGGER`. Static hostile tests reject swapped forms and deferrability placement. | PostgreSQL parse remains a later gate. |
| Trigger row images are treated as if they contain `xmin` | Immediate guards reselect system `xmin` by exact primary key before effect. The appointment gets a new immediate guard. Deferred delete fences record only the narrow same-table guard dependency because deleted-row `xmin` cannot be recovered from `OLD`. No emitted body contains `OLD.xmin` or `NEW.xmin`. | The paired-trigger behavior still requires later database-backed rehearsal. |
| Appointment durability blocks unrelated appointment writers | Both appointment triggers use the same exact producer applicability classifier: zero bindings is inert, one is applicable, duplicate is fail-closed. | Operational binding lifecycle remains deferred. |
| Fabric objects retain the migration executor as owner | Schema authorization, exact fabric type/relation owner transfers, signature-specific function owners and typed catalogue assertions are mandatory. Application owners remain unchanged and runtime principals receive no ownership or schema `CREATE`. | A future migration executor must have separately reviewed installation authority. |

## Residual risks deliberately deferred

PostgreSQL parsing and PL/pgSQL compilation; actual domains, enums, composites,
tables, indexes, foreign keys, RLS, security-definer, ownership, role and trigger
catalogues; application-schema compatibility; migration transaction and lock
behavior; concurrent insert/reload, producer and trigger semantics; rollback,
unknown commit and caller retry; key custody; operational credentials;
performance/capacity; deployment, production and incident response remain
later gates.

## Forbidden openings

This delta grants no SQL execution/application, Alembic migration, database
object, role or credential creation, database/source/outbox/feed/watcher/
listener/network contact, application/API/Diary change, patient/product/
protected data, product read, provider product call, command/write authority,
runtime wiring, deployment, production, release, Pages rebuild or protected-ref
movement. `docs/branding/` and unrelated untracked artifacts remain preserved
and excluded.
