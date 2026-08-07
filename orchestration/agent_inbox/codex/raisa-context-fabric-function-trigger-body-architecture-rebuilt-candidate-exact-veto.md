# Fresh exact-HEAD veto: rebuilt durability function/trigger bodies

Date: 2026-08-07

Reviewer role: fresh native candidate-independent read-only veto

Exact candidate:
`5ea59e14184b26dfa0b8d3a6ebaf28b39c04fb9d`

Review branch:
`codex/review-durability-function-trigger-body-r5`

Decision: `revision_required`

## Findings

### P1 — coordinator receipt replay suppresses retained conflicts

`has_receipt` selects `receipt_replay` before the conflict state machine. The
replay integrity branch contains neither a `conflict_set == 0` proof nor
canonical rederivation of `receipt_digest`. An in-memory AST challenge confirmed
zero conflict references and zero `CANONICAL_DIGEST` operations in that branch.
A PRIMARY can acquire a later mismatch conflict through admission, yet the
coordinator would return `RECEIPT_REPLAYED` rather than the required atomic
rebase.

### P1 — registration head creation and replay baseline are incomplete

`register_observer_generation_v1` locks an existing head but has no head insert
effect. Its replay branch reloads only `context_observer_generation`, compares
only controlling digests, and ignores the requested initial key interval,
checkpoint, two frames, two watermarks, initial key, baseline anchor and head
position. This violates create-or-reload head semantics and complete
registration replay equality.

### P1 — retention census identity and per-generation key coverage are incomplete

The generation set excludes `CONSUMED`, but aggregate checkpoint, anchor, pin
and key reads are scoped only to practice/source/stream. The slowest checkpoint
can therefore include a consumed generation. Global key eligibility compares
key count with generation count, while the per-generation key read has no
non-empty cardinality assertion. Multiple overlaps for one generation can mask
no overlap for another and authorize an unsafe eligibility result.

### P2 — critical signature/declaration semantics depend on canonical section equality

The decisive enforcement for owner, security-definer, volatility, trigger
timing and trigger deferrability values remains the
`effective_parent_summary` digest comparison. Resealed hostile mutations of
those fields produced only `normative_section_mismatch`; no independent
field-semantic issue was emitted. This fails the requirement that critical
fields close independently of canonical baseline equality.

## R1–R4 assessment

- R1 failed for receipt/conflict replay and registration lifecycle closure.
  The apply branch does represent the major lifecycle, audit, receipt, frame,
  watermark, obligation and checkpoint effects.
- R2 failed. `SERIALIZABLE`, barrier locking, seconds-based grace, REC19 enum
  closure, bounded source-only purge and purge rederivation are present, but
  census identity and per-generation key proof are incomplete.
- R3 passed. Non-temporal event and alias sets are current-XID constrained;
  outbox joins the exact event, alias, revision, predecessor and stream; head
  proof binds current-XID movement to that outbox; historical/unrelated rows
  remain harmless; and the second-update guard remains.
- R4 failed for canonical-hash dependence. Enum NULL handling rejects non-null
  out-of-enum values, frozen empty arrays validate, operand-derived effects and
  call graph are present, and direct outbox-delete privilege widening has an
  independent check.

## Verification and postflight

- Builder `--check`: passed at
  `sha256:8871663b121dedff089b7517406f8223a3df2153bce66716d624b2f321e20dde`.
- Prescribed pytest command: 128/128 passed; only the two recorded dependency
  deprecation warnings.
- Ruff: passed. A reviewer-only `RUFF_NO_CACHE=1` invocation was rejected before
  analysis; the corrected `RUFF_NO_CACHE=true` invocation passed and changed
  nothing.
- `git diff --check`: passed.
- Final `git status --short`: empty.
- Final HEAD remained
  `5ea59e14184b26dfa0b8d3a6ebaf28b39c04fb9d`.
- Exactly the packet's 28 allowlisted paths were inspected. No unrelated,
  branding, protected-holdout, prior-review or other inbox path was inspected.

## Boundary

GraphQL remains read-only, REST commands remain unchanged and events remain
observation-only. The candidate grants no SQL/DDL, migration, database/source,
runtime, provider, product/patient data, deployment, production, release,
Pages or protected-ref authority and must not advance to inert DDL rehearsal.

DECISION: revision_required
