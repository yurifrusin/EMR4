# Review — Claude — Sprint 201 API Spine Audit / Read-Model Continuity

| Item | Value |
|---|---|
| Sprint | 201 (read-only review) |
| Programme | Programme 2G / EMR4 API Spine |
| Agent | Claude (`claude/current`) |
| Worktree | `C:\Users\sarashera\EMR4-worktrees\claude` synced to `handoff/current` @ `a96392c4` |
| Date | 2026-07-08 |
| Kind | Read-only review + smallest-next-artifact recommendation. No production code touched. |
| Gate posture | All runtime/provider/GraphQL-mutation/H15/trove/memory gates remain closed. |

## Scope Performed

Read-only inspection of:

- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `docs/api-spine/graphql/appointment-diary-read.graphql`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `docs/api-spine/idempotency-continuity-index.md`
- `orchestration/api_spine_appointment_command_alignment_inventory.md`
- `tests/test_api_spine_artifacts.py`

No routers imported, no routes executed, no DB/provider/H15/trove/memory/RAG/GraphRAG touched, no GraphQL mutations proposed.

## Finding: the open continuity seam after Sprint 200

Sprint 200 (`docs/api-spine/idempotency-continuity-index.md`) closed the **idempotency**
seam: a static markdown index + parser test binding OpenAPI command paths to their
runtime idempotency status, validated by parsing only the index md and the OpenAPI
yaml. The **audit / correlation** seam is the next unbridged declaration pair:

- **GraphQL read side** (`appointment-diary-read.graphql`) declares audit *read models*
  that name a specific audit vocabulary but nothing binds it to the command side:
  - `AppointmentAuditAction` enum: `PROPOSAL_STAGED`, `CONFIRMED_CREATE`,
    `CONFIRMED_UPDATE`, `CONFIRMED_STATUS_CHANGE`, `CONFIRMED_WAITING_AREA_MOVE`,
    `CONFIRMED_CANCEL`, `DIRECT_COMPATIBILITY_WRITE`, `READ`.
  - `AuditEvent` / `AppointmentAuditEvent` both carry `correlationId: String`,
    `outcome: AuditOutcome`, `evidenceMode: EvidenceMode`.
  - `AuditFilter` filters by `correlationId`; `AuditTargetType` =
    `{APPOINTMENT, PATIENT, DIARY, PRACTICE, ACCESS_AI, DIRECTORY}`.
- **OpenAPI command side** (`appointment-commands.yaml`) declares audit/correlation
  *command metadata* with a different vocabulary and no cross-reference back:
  - `AuditIntent.audit_action` enum: `appointment_proposal_prepared`,
    `appointment_created`, `appointment_updated`, `appointment_status_changed`,
    `appointment_deleted`, `slot_search_normalized`, `slot_search_proposed`,
    `slot_selected_for_proposal`.
  - `AuditIntent.target_kind` = `{appointment, slot_search, proposal}`;
    plus `expected_audit_event`, `audit_tags`.
  - `X-Correlation-Id` parameter (`CorrelationId`, line 419) is attached to every
    command path and described as "propagated into audit and event records";
    `correlation_id` is a required field in the command `meta` envelope.

Nothing today asserts these two vocabularies stay consistent, and no artifact records
which mismatches are *intentional plane asymmetry* versus accidental drift. This mirrors
exactly the gap Sprint 200 closed for idempotency.

## Recommended smallest artifact for Sprint 201

**A static audit/correlation continuity index plus a parser-only test** — same shape and
safety envelope as the Sprint 200 idempotency index. Nothing runtime.

Recommended files:

1. `docs/api-spine/audit-correlation-continuity-index.md` — a static markdown index
   with three mapping tables and a closed-gates section:
   - **Audit-action bridge**: each GraphQL `AppointmentAuditAction` value → its
     corresponding OpenAPI `AuditIntent.audit_action` value(s) → status label.
   - **Correlation bridge**: GraphQL `correlationId` surfaces (`AuditEvent`,
     `AppointmentAuditEvent`, `AuditFilter.correlationId`) ↔ OpenAPI `X-Correlation-Id`
     parameter + `correlation_id` command-meta field, noting both sides describe the
     same propagated id.
   - **Target-kind bridge**: GraphQL `AuditTargetType` ↔ OpenAPI `target_kind`, marking
     `appointment` as the shared target, `slot_search`/`proposal` as command-plane-only,
     and `patient`/`diary`/`practice`/`access_ai`/`directory` as read-plane-only.
2. `tests/test_api_spine_audit_correlation_continuity_index.py` — a deterministic parser
   test that reads **only** the index md, the GraphQL SDL, and the OpenAPI yaml (no
   imports of `app/`, no yaml execution beyond `safe_load`), asserting the invariants
   below.

Status labels to use (parallel to Sprint 200's `ledger_wired` / `documented_gap` /
`read_no_idempotency`):

- `bridged` — GraphQL audit-action value has a declared OpenAPI counterpart.
- `read_model_only` — GraphQL audit value with no command counterpart by design
  (e.g. `READ`, `DIRECT_COMPATIBILITY_WRITE`).
- `command_plane_only` — OpenAPI audit value with no GraphQL `AppointmentAuditAction`
  counterpart by design (e.g. `slot_search_normalized`, `slot_search_proposed`,
  `slot_selected_for_proposal`, whose targets are `slot_search`/`proposal`, not
  appointments).

## Deterministic invariants the test should assert

1. Every GraphQL audit-action token listed in the index exists verbatim as a value in
   the `AppointmentAuditAction` enum block of `appointment-diary-read.graphql`.
2. Every OpenAPI audit-action token listed in the index exists verbatim in the
   `AuditIntent.audit_action` enum of `appointment-commands.yaml`.
3. Every `target_kind` token in the index exists in the OpenAPI `target_kind` enum;
   every GraphQL target token exists in the `AuditTargetType` enum.
4. The correlation bridge row references both `X-Correlation-Id` (present in the yaml)
   and `correlationId` (present in the SDL) — assert both literals appear in their
   respective source files.
5. Every index row carries exactly one status label from the allowed set
   `{bridged, read_model_only, command_plane_only}`.
6. The index contains a "Closed Gates" section naming the same closed gates as the
   Sprint 200 index (no proposal-idempotency enforcement, no GraphQL mutations, no
   provider/FGA/external-client/H15/trove/memory-RAG-GraphRAG/model-to-DB-write opening).
7. No forbidden-pattern leakage — reuse the `BANNED` set / `_check_no_forbidden` style
   already in `tests/test_api_spine_artifacts.py` so the index cannot smuggle provider
   prompts, raw model output, or H15/trove fragments.
8. Index is self-describing: it names the exact two source files it validates against
   (so drift in either source is caught, matching the Sprint 200 index self-reference).

## Closed gates (unchanged — this artifact must not open any)

- proposal-only route idempotency enforcement;
- GraphQL mutations / any write root;
- runtime FGA clients; live provider runtime; external patient clients;
- H15 / H-series runtime imports; broad historical diary trove mining;
- memory / RAG / GraphRAG runtime wiring;
- model-to-database writes outside REST command handlers.

The recommended artifact is documentation + a parser test only. It proves *declaration
continuity*, not runtime audit-log append-only semantics, correlation-id propagation
behaviour, or database durability — the index must say so explicitly (as the Sprint 200
index does in its Boundary section).

## Risks / ambiguities

- **Vocabulary is genuinely two-sided, not 1:1.** GraphQL confirm-family names
  (`CONFIRMED_CREATE`…) map to OpenAPI past-tense `appointment_created`… while the
  proposal stage maps `PROPOSAL_STAGED` ↔ `appointment_proposal_prepared`. The index
  should encode a many-to-one/deliberate-rename mapping, not assume identical strings,
  or the test will be brittle. Recommend an explicit mapping table rather than a
  set-equality assertion.
- **`CONFIRMED_WAITING_AREA_MOVE` has no distinct OpenAPI audit_action** — waiting-area
  writes fold into `appointment_status_changed` on the command side (consistent with the
  alignment inventory, which routes waiting-area proposals through the status family).
  Mark it `bridged` to `appointment_status_changed`, not a gap, and note the fold.
- **`DIRECT_COMPATIBILITY_WRITE`** corresponds to the compatibility writes
  (`POST/PUT/PATCH/DELETE /appointments`) that are deliberately outside the OpenAPI
  command envelope; mark `read_model_only` and cross-reference the alignment inventory's
  compatibility-write rows so it is not mistaken for accidental omission.
- Keep the index parser tolerant of enum formatting (leading `-`, indentation) but strict
  on token identity, to avoid false green if an enum value is later renamed.

## Verification commands (for the implementer, when Sprint 201 is approved)

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_audit_correlation_continuity_index.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe -m py_compile tests\test_api_spine_audit_correlation_continuity_index.py
```

## Reason to pause Ariadne?

**No pause required.** This is a bounded, static, documentation + parser-test artifact
that continues the Sprint 199→200 continuity-index track without opening any closed gate
or touching runtime. It is the smallest artifact that bridges the GraphQL audit/read-model
declarations to the OpenAPI audit/correlation command metadata. Ariadne may dispatch it as
an ordinary bounded implementation lane (Claude/DeepSeek) with the plan gate and
Ariadne-run verification. Sprint engine can continue.

## Completion Notes

- Files changed: this review packet only (no production code).
- Verification run: read-only inspection only; no tests executed (review packet, not
  implementation). Recommended verification commands listed above for the implementation
  sprint.
- Remaining risks: the two-sided audit vocabulary (see Risks) must be encoded as an
  explicit mapping table, not string equality, or the parser test will be brittle.
