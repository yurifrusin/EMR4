# Threat-model delta: durability function-and-trigger-body architecture

Date: 2026-08-07

Status: exact candidate rejected by fresh independent veto; second exact-veto
recovery pending replacement implementation

Normative implementation recovery:
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-implementation-recovery.md`

Normative second exact-veto recovery:
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-second-exact-veto-recovery.md`

## Scope and assets

This delta covers the machine-readable bodies for the nine entry points and
thirteen trigger functions in the accepted durability architecture, after the
one closed `structural_feasibility_recovery_v1` is applied to the immutable
parent. It specifies no executable SQL or deployed control.

It also covers the normative implementation recovery from the rejected
label-only candidate digest
`sha256:c16930c2d6c400c93ea2c2b413ccf084ceb38c4f980fa4edae032b74e3112622`.
That candidate is not an implementation source: its semantic labels, free
predicate leaves, relation-wide profiles and asserted call-graph properties
could not determine executable meaning. The recovered boundary requires
discriminated typed instruction and expression ASTs plus mechanically derived
semantics.

The subsequent typed-but-misbound candidate digest
`sha256:f8afd0ce97169b0fae926dbe7999b9961d9be7506f711de579a3c035f75b2064`
is also negative evidence only. Its typed surface did not prevent wrong-relation
writes, source-free derivations or cross-relation trigger images. Acceptance
therefore combines structural typing with operand-derived semantics and an
independent exact-body hostile-mutation envelope.

Protected assets are practice/source/stream isolation; authenticated binding
and exact binding revision; the signed update-confirm transaction boundary;
product-table privilege separation; opaque alias confidentiality and
immutability; payload-free gap-free outbox order; immutable admission and
receipt evidence; truthful coordinator outcomes; monotonic checkpoints,
watermarks and retirement; baseline and recovery anchors; generation-local key
continuity; complete retention census; minimized value-free failure metadata;
and the separation between observations, current truth and command authority.

## Trust boundaries

The boundaries are: authenticated REST producer to owner-mediated projection;
product tables to the owner-private alias/outbox plane; observer login to the
distinct admission receiver; retained source/admission evidence to the
coordinator; lifecycle principal to independent anchors and key intervals;
retention principal to a serialized database-derived census; machine contract
to a later inert renderer; and all durability evidence to a separately
authorised fresh application read. `session_user`, not a caller GUC, locator or
packet, is the identity root at every entry point.

Runtime logins are mutually non-inheriting and non-owning. The schema owner and
admission receiver are non-login security-definer owners with exact privilege
ceilings. Migration installation is a separate future boundary and does not
survive as runtime authority.

## Threats and mitigations

| Threat | Mitigation | Residual risk |
|---|---|---|
| Cross-practice, cross-source or cross-stream access | One active login/capability/practice/source/stream/revision/epoch binding is rederived from `session_user`; all stream-bearing locators, keys, RLS and entry-point checks compare it. Alias and retention coordinates include stream. Ambiguity fails before effect. | Operational pool/login isolation and credentials require a later gate. |
| Security-definer privilege escalation | Non-login `NOINHERIT`/`NOBYPASSRLS` owners, fixed qualified search path, no dynamic SQL, `PUBLIC` execute revoked, exact execute roles and mechanically rederived effects. `context_schema_owner` gets only `SELECT` on four qualified product tables; receiver gets only its closed reads plus admission `INSERT`. | A later rendered privilege catalogue and live PostgreSQL behavior remain unproved. |
| Product-table DML is invented to reacquire locks | Bodies rely on existing route-held locks/current inserts and use owner `SELECT` only; effects reject product insert/update/delete/truncate and unused product-field reads. | Actual SQL lowering and ORM transaction interaction remain later tests. |
| Shared-row discriminator adoption or escape | Claim and event guards classify both `OLD` and `NEW`; changing into or out of exact operation/route or reschedule type/schema fails. Deferred fences reload final state. | Only the exact v1 discriminators are covered; future families need new review. |
| Audit guard classifies command family from an audit row that lacks operation/route | For each potentially exact `OLD`/`NEW` audit image, the guard performs an exact-cardinality read of the corresponding qualified `public.appointment_command_idempotency` row and only `practice_id`, `id`, `operation_id` and `route_family`. That read is present in the guard's derived effect summary. | Broader audit families require their own discriminator contract. |
| Check-in is captured as reschedule durability | Event guards/fences require exact reschedule type and schema. Check-in remains outside the stream, feed and body family even though it shares `public.diary_committed_events`. | No claim is made for check-in durability. |
| Alias reuse is rejected or accepted with false current-XID proof | A newly inserted alias requires current-XID provenance and one current outbox reference; an older immutable exact practice/source/stream/product mapping is reused without current `xmin`. Winner reload/compare resolves races. | Opaque UUID collision still fails the entire command; no probabilistic collision-free claim. |
| Alias mapping is changed, deleted or reused across products/streams | Forward/reverse uniqueness plus immutable guard, qualified stream coordinate and no direct runtime bridge privilege. The sole producer body generates the opaque UUID and returns only the outbox row. | Future erasure or epoch reuse remains a separately reviewed design. |
| Same appointment is updated twice in one top-level transaction | The appointment fence rejects an exact producer update when `OLD.xmin` is already current-XID, preventing conflicting queued temporal/non-temporal obligations. | A no-write savepoint is not database-observable; the application contract separately forbids savepoints. |
| Required member is inserted then deleted before commit | Immediate guards and queued deferred trigger events retain visibility; final-state fences prove bidirectional current-XID membership. | Actual PostgreSQL trigger semantics require later database rehearsal. |
| Product-event retention is blocked or treated as outbox purge | Older exact product-event deletion is inert and does not require outbox deletion; the outbox has no persistent product-event foreign key. Current-XID event deletion still fails. | Product retention policy itself is outside this contract. |
| Producer or arbitrary principal deletes outbox | Outbox delete is accepted only for an older row, exact retention binding, enabled policy and sole path through `purge_source_rows_v1`; producer/current/other deletion fails. Current policy disables execution. | Later enablement requires a separate operational gate. |
| Fabricated receipt on rebase, gap or missing primary | Coordinator returns closed `durability_transition_result_v1`; only receipt kinds carry stored receipt digest. Rebase/terminal kinds carry checkpoint integrity digest and never fabricate `PRIMARY` or receipt. | Consumer handling of the composite is not implemented here. |
| Coordinator terminal replay depends on an unavailable caller reason | The coordinator has no terminal-reason input. `TERMINAL_REPLAYED` is derived only from stored terminal generation, checkpoint and result-integrity state. Same-reason comparison belongs exclusively to `consume_observer_generation_v1`, which has the typed `closed_reason` input. | Runtime consumer behavior remains unimplemented. |
| Observer guesses binding revision from a Boolean helper | Admission receiver has exact binding-table read, derives the active row/revision atomically and stores it. The Boolean helper remains an RLS/allow check, not revision evidence. | Credential issuance and channel authentication remain later gates. |
| Missing initial key material, missing stream head or missing baseline anchor | Registration takes typed `initial_key_interval`, requires start at checkpoint plus one, creates/reloads position-zero head and atomically creates checkpoint/frames/watermarks/key plus independently lifecycle-authored baseline anchor. Replay compares the complete baseline. | Real key-store availability and anchor execution are unproved. |
| Registration falsely gains recovery-pin authority | Pin relation remains ungrantable and mutation-inert; no body creates/releases pins. Retention only honours valid existing rows. | Pin lifecycle requires a separately accepted future gate. |
| Key, anchor or rotation replay rewrites history | Rows are immutable; anchor append independently reverifies full committed state. Rotation checks exact replay before the new-effect anchor fence, rejects mismatch, permits only future-fenced gap-free generation-local intervals and advances one lifecycle revision. | Cryptographic key bytes and external key custody are outside scope. |
| Key rotation in one generation affects another | All rotation locators, locks, schedules and effects include exact generation and stream; cross-generation effects are not in the effect allowlist. | Concurrency/performance needs database-backed testing. |
| Filtered or caller-supplied retention census authorizes purge | At `SERIALIZABLE`, evaluation/purge lock the common registry barrier and derive the complete non-consumed-generation set, slowest checkpoint, pins, key overlap and grace from qualified relations. Caller cannot supply filters, minima, count, time result or digest. Ambiguity fails. | Operational retention duration/capacity decisions remain open. |
| Concurrent registration is omitted from purge | Registration/rebaseline and retention acquire the same practice/source/stream registry barrier in the same order. Purge rederives eligibility inside its own transaction. | Lock behavior is architectural until live PostgreSQL rehearsal. |
| Trigger firing order becomes an invariant | Every deferred fence is read-only, lock-free, sibling-call-free and independently validates final transaction state. No fence consumes another fence's result or mutates state. | Later renderer must preserve constraint-trigger timing exactly. |
| Stream-head guard gains an unreachable or authority-widening INSERT path | `cf_guard_stream_head_v1` is closed to `BEFORE UPDATE, DELETE` and contains no INSERT arm or terminal. Registration's position-zero insert is checked only by the deferred `cf_fence_stream_head_v1`. | Actual declaration/body consistency still requires later catalogue rehearsal. |
| Trigger signature is confused with branch return behavior | Every full trigger-function signature returns exactly `pg_catalog.trigger`. `RETURN_NEW`, `RETURN_OLD`, `RETURN_NULL` and `RAISE` exist only as typed terminals in event-specific branches and must agree with the return matrix. | PostgreSQL compilation is deferred. |
| A trigger reads the wrong or unavailable row image | The trigger declaration closes relation/timing/level/events; its typed `TG_OP` arms expose only the legal `OLD`/`NEW` shape. Column refs are body- and arm-scoped, all declared operations are total and the unexpected-context arm raises. | Actual trigger invocation remains a later PostgreSQL rehearsal. |
| Label-only steps or free expression leaves make the renderer invent meaning | Every program is an ordered tree of discriminated instruction nodes with opcode-specific operands, typed symbols, exact children, convergence and terminals. Expressions are separately discriminated with fixed arity/types. Prose labels, arbitrary strings and generic operations have no schema branch. | The later mechanical lowering implementation still requires independent review. |
| Raw SQL, dynamic SQL or arbitrary identifier escapes the contract | `body_program_v1` contains only qualified catalogue refs, typed instructions/expressions and exact allowlisted support calls. SQL strings, interpolation, generic execute/call, exception swallowing, transaction control, DDL and role/config mutation are unrepresentable. | A future lowering implementation must itself be reviewed and tested. |
| A body widens reads, locks, calls, writes, delete surface or failures | Each reachable node has a column-minimal local footprint derived from opcode and operands. Deterministic traversal rederives branch and aggregate effects, lock order/mode, failures, terminals and output, then compares one frozen body-specific summary and the effective-parent privilege ceiling. | Static equivalence does not prove runtime performance or lock safety. |
| A valid relation or column is transplanted to the wrong body | The structural schema position-closes the exact body/signature/declaration populations without freezing body objects as constants. The semantic validator derives relation/column effects from operands, and the independent exact-body acceptance envelope rejects transplanted operands or AST drift after evidence and schema resealing. Global catalogue membership alone is insufficient. | The later renderer implementation remains a separately reviewed gate. |
| A stored call-graph assertion conceals a sibling call or cycle | Structured `{from,to}` edges are derived only from typed call nodes. Tests compute edge equality, acyclicity, no entry-point sibling calls and no trigger sibling calls; trusted graph Booleans are absent. | Future additions require a new closed graph and review. |
| Uniqueness races disappear behind `ON CONFLICT DO NOTHING` | Alias and admission races reload the immutable winner and compare exact identity/digest; equality is inert and inequality fails or appends/returns the sole conflict sentinel. | Deadlock/serialization retry remains caller-owned. |
| A first cross-position digest-reuse conflict is persisted before source authentication | Admission branches are ordered: retained exact primary replay; retained-primary mismatch append/reload or retained-conflict replay without source; authenticated source and generation-local key membership only when no locator admission exists; then cross-position reuse detection and new conflict/primary persistence. Only retained evidence is source-independent. | Source availability for a genuinely new admission remains operationally necessary. |
| Retry logic duplicates partial effects or swallows a failure | Bodies cannot catch/retry or control transactions. `40001` and `40P01` propagate for whole-transaction retry; other unexpected failures propagate and roll back. | Caller retry bounds and unknown-commit operations need later integration testing. |
| Failure metadata leaks patient, practice or control identifiers | Closed custom SQLSTATE/reason registry; metadata names only reason/body and forbids row values, UUIDs, digests, credentials and packets. | Database/server logging configuration remains operational work. |
| Aggregate revision is invented from Appointment state or becomes ordering authority | Producer rederives it only as the same-practice/appointment audit-row count after insert and compares event/outbox equality. It remains anomaly/freshness metadata, never durability position. | Concurrent route correctness remains a database-backed acceptance item. |
| Current-XID evidence is retained, caller-supplied or overclaimed | Exact PostgreSQL-16 low-XID32 expression and system `xmin` are used only during the active top-level producer transaction with transaction-start and zero-legacy/no-committed-in-progress controls. XID is never stored, digested, exposed or ordered. | No-write savepoints and later PostgreSQL-version changes require separate controls. |
| Effective-parent recovery silently widens parent authority | Parent hash is verified first; one typed delta with exact operation set derives the effective parent. Unknown/missing/additional operations, product DML/runtime product read, extra helper/overload or changed unrelated invariant fail even if resealed. | The derived contract still needs independent veto before acceptance. |
| Renderer reorders grants before objects or invents executable semantics | Renderer order is frozen: derived schema/helper, nine bodies, thirteen trigger bodies, trigger declarations, revocations/exact grants, assertions. Mechanical lowering only; no prose inference or extra helper/body. | Renderer and PostgreSQL grammar are a later tranche. |
| Event or durability state is used as command/current truth | API Spine classification is invariant: GraphQL remains read-only; mutations remain explicit REST commands; events/outbox/admissions/receipts only invalidate or preserve continuity and cannot trigger a fresh read or command. | Runtime wiring is not authorised or assessed here. |

## Residual risks deliberately deferred

Executable DDL and PostgreSQL grammar; actual security-definer, RLS, trigger and
constraint behavior; migration lock/install sequencing; live role/catalogue
privileges; connection pooling and operational credentials; real concurrency,
crash recovery and retry behavior; key custody; monitoring; capacity and
retention duration; privacy assessment; product/source load; deployment,
production and incident response remain later gates. Digest chains establish
integrity/tamper evidence only, not cryptographic authenticity against a
compromised database owner.

## Forbidden openings

This delta grants no SQL/DDL, migration, database object, role, trigger,
function or grant creation; no database/source/feed/watcher/listener/network or
provider contact; no application/API/Diary change; no patient, product,
protected or historical-PHI data; no operational persistence or credential;
no fresh product read; no command/write authority; no runtime wiring,
deployment, production, release, Pages rebuild or protected-ref movement.
