# DeepSeek bounded work packet — delete-confirm composition/product adapter

Worker: DeepSeek V4 Flash/high through Claude Code `--bare`

Exact worktree: `C:\Users\sarashera\EMR4-worktrees\deepseek-delete-confirm-adapter-eac9846e`

Exact branch: `codex/worker-delete-confirm-adapter-eac9846e`

Required worktree HEAD: `eac9846ee77b4f2621897c1efa84c5ce76c63f59`

## Rehydrate before editing

Read `AGENTS.md` completely. Then read completely:

- `docs/raisa-provider-free-unmounted-delete-confirm-composition-product-adapter-implementation-plan.md`;
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-composition-product-adapter-implementation/implementation-contract.json`;
- the twelve exact input paths and verify every canonical-LF SHA-256 in the contract; and
- the active latch.

Verify the exact branch/HEAD and clean worker worktree. Verify local/origin
`master` and `handoff/current` remain
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Report the five rehydration
sources, actual parallelism, checks and exact commit in the final result.

## Sole owned package

Create and commit exactly these four paths:

- `app/services/appointment_delete_composition.py`;
- `app/services/appointment_delete_product_adapter.py`;
- `tests/test_appointment_delete_composition.py`; and
- `tests/test_appointment_delete_product_adapter.py`.

Do not edit, stage or commit any existing file. Use explicit-path staging only.
Do not push.

## Required composition semantics

Implement an unmounted pure composition closely following the structural
precedent in `appointment_status_composition.py` but preserving the accepted
delete differences:

- immutable server ingress includes practice, actor, role, positive authority
  generation, HMAC session reference, authority-current posture, current state,
  freshness, evidence status/purpose/binding;
- admitted kernel request is exact `raisa.delete_kernel_request.v1`, operation
  `confirmAppointmentDeleteProposal`, route family `delete-confirm`, lock plan
  `user, appointment, idempotency_record`, and `effect_authority: false`;
- default transaction is only `delete_confirm_locked_transaction` and receives
  the positive signed authority generation;
- new-command flow repeats admission using the locked appointment, requires an
  identical request digest, stages the injected delete effect, then completes
  the exact private six-field receipt on the physical record;
- replay validates stored digest, JSON and exact private canonical bytes and
  performs no effect;
- success projects public bytes only from validated private bytes, never from
  a current appointment or `AppointmentOut`;
- committed and replay public bytes are byte-identical for the same private
  receipt; and
- closed errors are 403 current authority, 404 indistinguishable unavailable,
  409 idempotency missing/conflict/in-progress/legacy, and 503 wait/scaffold/
  integrity/projection/physical failure. Admission stops are typed 200 blocked.

Private receipt validation must require exact object key order and exact compact
UTF-8 bytes for:

`appointment_id,status,status_reason_code,cancellation_reason,waiting_area_id,warning_codes`.

Require status `Cancelled`, waiting area null, one of the physical module's ten
reason codes, nullable <=500-character cancellation text, and sorted unique
warning codes drawn only from `waiting_area_cleared`.

Public success is sorted-key compact UTF-8 JSON with:

- schema `raisa.delete_confirm_public_envelope.v1`;
- receipt schema `appointment.delete_confirmation_receipt.v1`;
- exact intent/safe/requires-confirmation/autonomy/summary constants from the
  machine contract;
- exact warning registry projection; and
- audit labels in exact frozen order:
  `delete_product_adapter_v1`,
  `delete_signed_confirmation_evidence_verified`,
  `delete_current_authority_rechecked`.

It must contain no appointment, patient, practitioner, schedule, notes, reason,
audit identity or live projection field.

## Required product-adapter semantics

Implement the application-owned unmounted adapter closely following the
structural precedent in `appointment_status_product_adapter.py`, with these
delete-specific requirements:

- bearer minimization is a domain-separated HMAC bound to authenticated bearer,
  actor and practice;
- version binding schema is `raisa.delete_proposal_version_binding.v1`; its HMAC
  covers exactly positive `source_version` and signed evidence signature;
- accept only actual `AppointmentDeleteProposalOut` inside
  `AppointmentDeleteProposalConfirmationIn`;
- proposal intent is `delete_appointment`; evidence purpose is the existing
  `SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE`;
- current state is exactly appointment id, status, waiting-area id,
  cancellation reason, status reason code and positive source version;
- signed payload excludes source version and matches the existing delete
  payload contract; version remains separately HMAC-bound;
- warning requirement is exactly `waiting_area_cleared` iff current waiting
  area is non-null; proposal and confirmed warnings must already equal the
  exact sorted unique requirement;
- pre-command and locked admission require exact target, source version,
  non-Cancelled status, waiting-area/clear flag, reason, cancellation text,
  freshness and signed evidence;
- authenticated role and positive authority generation come only from the
  server-loaded user; client fields grant nothing;
- the command session is distinct and closed after use; and
- effect staging sets status Cancelled, waiting area null, exact reason/text,
  creates one delete audit with every v1 private field expected by the physical
  seam, refreshes the database-owned adjacent state version, and returns only
  the audit identity to composition. The composition writes the private receipt.

Do not add a capability callback: the physical seam owns the hardcoded grant
and its two current checks.

## Tests and verification

Use authored-synthetic in-memory doubles only. Test success projection, exact
bytes, first/replay parity, hostile private/public mutations, warning registry,
server-owned identity/generation/session, version-binding tampering, evidence/
freshness/warning/state failures, locked re-admission, effect/receipt staging,
all decision/error mappings, command-session closure and route/source isolation.

Run only provider-free tests through:

`C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.ariadne_provider_free_pytest --repo-root C:\Users\sarashera\EMR4-worktrees\deepseek-delete-confirm-adapter-eac9846e tests/test_appointment_delete_composition.py tests/test_appointment_delete_product_adapter.py`

Also run Ruff on the four owned paths, Python compilation on both new service
modules, `git diff --check`, `git diff --cached --check`, and `git show --check`
after the commit. Do not use ordinary pytest and do not open a database,
Docker, SQL, route, provider, credential, network, browser, product data,
protected evidence, deployment, release, Pages or protected ref.

Return the full commit SHA, exact changed paths, check results, any scope breach
or blocker, and an advisory `pass` or `revision_required`. Sol retains all
reconciliation and acceptance authority.
