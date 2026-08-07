# Durability function-and-trigger-body second exact-veto recovery

Date: 2026-08-07

Status: normative Sol recovery preserved; its replacement candidate was
rejected by a later exact-HEAD veto and the third recovery now controls

Rejected candidate source HEAD:
`5ea59e14184b26dfa0b8d3a6ebaf28b39c04fb9d`

Independent veto:
`orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-rebuilt-candidate-exact-veto.md`

Rejected candidate contract:
`sha256:8871663b121dedff089b7517406f8223a3df2153bce66716d624b2f321e20dde`

Immutable parent contract:
`sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8`

## Recovery classification

The fourth candidate remains rejected even though its prescribed static packet
passed 128/128. A fresh exact-HEAD reviewer found three P1 semantic gaps and
one P2 normative-closure gap. This is a conceptual recovery under Sol's
orchestrator lease, not a same-lane mechanical retry. The rejected candidate is
untrusted implementation source except where the independent veto explicitly
accepted R3 and named already-closed subproperties.

This recovery changes neither the accepted migration/transaction parent nor
the API Spine, data, provider, runtime, command, deployment or claim boundary.
It replaces only the four under-closed child semantics below.

## R5A — conflict-safe, integrity-rederived receipt replay

`apply_durability_transition_v1` must never select receipt replay from receipt
count alone.

- Receipt replay requires exactly one retained receipt, exactly one retained
  matching PRIMARY and zero retained CONFLICT entries at the exact admission
  locator.
- Any retained conflict wins over receipt replay and follows the explicit
  atomic rebase path; it may not be hidden by an older receipt.
- Replay must reconstruct `classified_receipt_digest_v1` from the exact locator,
  stored source position, retained PRIMARY `admission_digest` and stored
  lifecycle revision, then compare that derived digest to the stored receipt.
- The existing field-by-field receipt/PRIMARY/checkpoint comparisons remain;
  digest comparison is additional and cannot be replaced by section equality.
- Zero, duplicate or mismatched receipt/PRIMARY evidence fails closed or
  rebases only through the already frozen explicit state machine.

Hostile acceptance must reseal and reject conflict-blind routing, removal or
substitution of the canonical digest node, a digest comparison against the
wrong input, or replay with duplicate/missing PRIMARY evidence.

## R5B — create-or-reload head and complete registration replay

`register_observer_generation_v1` must establish one usable stream head and
compare the complete baseline on exact replay.

- Under the already locked registry barrier, read the exact head coordinate.
  Zero rows creates or reloads one position-zero head for the requested stream
  epoch; one row locks and uses the existing head; ambiguity fails. A missing
  row can never be sent directly to an `EXACTLY_ONE` lock.
- Head creation is represented by an operand-derived insert effect. It creates
  no producer event, alias or outbox effect and grants no new runtime role.
- Both the inserted and existing branches converge with one definitely assigned
  typed `head` row before generation logic.
- Exact generation replay independently reloads: generation, checkpoint, the
  two exact CURRENT frame types, the two exact watermarks, the requested
  initial key interval, the lifecycle-revision-zero baseline anchor and the
  controlling head.
- Replay compares lifecycle/terminal state, all seven controlling digests,
  checkpoint position/state/revision/digests, exact frame-type coverage and
  positions, exact watermark coverage and positions, exact initial key
  start/end/key/attestation, exact anchor position/state/controlling and
  integrity digests, and head stream epoch/position. UUID frame identifiers
  need not equal caller material because none is supplied, but their two exact
  typed rows must be unique and complete.
- Any missing, duplicate or unequal baseline member raises the closed
  registration failure; replay never repairs a partial baseline.

Hostile acceptance must reject omission of head insertion and omission or
substitution of every baseline member/proof after contract and schema resealing.

## R5C — identity-joined retention sets and per-generation key coverage

Retention continues under `SERIALIZABLE` and the shared registry barrier. The
complete all-except-`CONSUMED` generation set remains the authoritative census.

Two exact typed expression primitives are added because count equality cannot
express this closed database-derived proof without ambiguity:

- `SET_CONTAINS_KEY(set, source_row, key_pairs)` is a Boolean predicate used
  only inside a typed set read. It includes a source row iff one member of the
  already selected complete set has equal values for every ordered, same-typed
  key pair. The set relation, source relation and key columns are explicit;
  empty pairs, unknown symbols, mismatched types, incomplete generation identity
  and generic/arbitrary predicates are invalid.
- `SET_COVERS_KEYS(required_set, evidence_set, key_pairs)` is true iff every
  member of the required complete set has at least one evidence member matching
  every ordered same-typed key pair. Duplicate evidence for one generation
  cannot compensate for an uncovered generation.

The checkpoint, anchor and key aggregate sets must be filtered through
`SET_CONTAINS_KEY` against the exact generation set using all six generation
coordinates. Pins use every generation identity coordinate their parent table
contains; omission of unavailable `stream_epoch` is explicit, not a generic
scope shortcut. Generation-keyed receipt and audit grace sets use the same
exact census identity where their catalogues permit it.

The slowest checkpoint remains `MIN_FIELD` over this newly identity-joined
checkpoint set. Exact one-checkpoint-per-generation and current-anchor coverage
remain independently proved. Key overlap uses `SET_COVERS_KEYS` between the
generation set and the through-position overlapping-key set; total key-row
count equality is forbidden. The existing per-generation complete key reads
remain corroborating branch evidence, not the sole coverage claim. Eligibility
and REC19 reason selection use the same coverage predicate, and purge rederives
the same joined census and key proof in its transaction.

Hostile acceptance must prove that consumed-generation checkpoints cannot
change the minimum, out-of-census pins/anchors/keys cannot change eligibility,
duplicate overlaps for one generation cannot mask another generation's missing
key, and removal/scope-widening of either new primitive fails semantically after
resealing.

## R5D — independent exact signature and trigger-declaration semantics

Canonical section digests remain tamper evidence only. The validator must carry
candidate-independent exact field maps for the support signature, nine
entry-point signatures, thirteen trigger-function signatures and thirteen
trigger declarations.

For every signature, independently validate exact position/id, ordered inputs,
output type/cardinality, language, owner, executor, strictness, volatility,
parallel safety, security-definer value, fixed search path, PUBLIC execute
denial and invariant IDs. For every trigger declaration, independently validate
exact position/function/relation/timing/row level/ordered events/deferrability/
initially-deferred values. Each mismatched critical field emits a field-specific
semantic issue in addition to any normative-section digest mismatch.

The exact maps are static validator authority derived from the frozen parent and
closed recovery, not read from the candidate under review. A mutation of owner,
security-definer, volatility, timing or deferrability must therefore produce at
least one issue other than `normative_section_mismatch` after contract and schema
digests are regenerated.

## Lane allocation

- **State/retention program lane:** coordinator receipt replay, registration
  lifecycle, joined retention bodies, the two exact set primitives in the
  builder DSL and focused body tests.
- **Semantic-validator lane:** validator semantics for the two set primitives,
  independent exact signature/declaration maps and focused hostile tests.
- **Structural-schema lane:** structural schema branches for the two set
  primitives, exact positional scalar closure and focused resealed schema tests.
- **Sol:** integrate shared vocabulary, rebuild generated contract/schema,
  reconcile effect summaries and hashes, run the complete packet, preserve all
  incidents, and commission a new candidate-independent exact-HEAD veto.

Owned files are disjoint except that Sol alone resolves any necessary shared
test or generated-artifact changes. Repository pytest remains serial.

## Acceptance and unchanged boundary

The replacement must pass all earlier plan/recovery tests plus new hostile
proofs for R5A–R5D, the AER packet, scoped API Spine checks, Ruff, builder
`--check`, `git diff --check`, explicit-path worktree guards and a new fresh
exact-HEAD independent veto. Candidate
`5ea59e14184b26dfa0b8d3a6ebaf28b39c04fb9d` cannot become accepted source.

Its replacement at `5a3c5b5118f80153d545bf30ae9db99acb187cd7`
also remains rejected. The binding continuation is
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-third-exact-veto-recovery.md`.

This remains pure, provider-free, unmounted and repository-local. It renders or
executes no SQL/DDL; creates no migration, database object or operational state;
opens no source/feed/watcher/listener, product/patient read, provider, command,
runtime, deployment, production, release, Pages or protected-ref authority.
