# Independent veto packet: C5 Windows endpoint-ownership recovery

Date: 2026-08-06

You are the independent Gemini 3.6 Flash/high veto reviewer. Review only the
exact committed candidate below. Do not edit any file and do not implement a
repair.

## Exact candidate

- Worktree: `C:\\Users\\sarashera\\EMR4-worktrees\\model-required-bureau-c5-windows-endpoint-review`
- Branch: `codex/review-model-required-bureau-c5-windows-endpoint`
- Required HEAD: `88b330870bd559b5276ae8191a41d152c48e9d7b`
- Candidate branch is non-protected and must remain clean and unchanged.
- Protected local/origin `master` and `handoff/current` must remain:
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.
- Earlier reviewed C5 live-source ancestor: `7a8c4e2bdd3251458fb08a9afc2c4b6780aa26b1`.

## Review objective

Determine whether the repaired C5 source safely and truthfully replaces the
invalid Windows TCP-refusal absence assumption while preserving every closed
pre-execution and live-rehearsal boundary. Look for any material defect that
could permit a wrong/stale source state, shared or stolen endpoint, premature
port release, unowned process, unsafe retry, missed accounting, model text to
become authority, false occupied pass, incomplete rollback/cleanup, stale
Ariadne authority, or an API/product surface to open.

Inspect at least:

- `scripts/model_required_bureau_c5_rehearsal.py`
- `scripts/model_required_bureau_c5_live.py`
- `scripts/model_required_bureau_c5_contract.py`
- `scripts/model_required_bureau_c5_acceptance.py`
- `docs/emr4-model-required-bureau-c5-disposable-live-development-recovery-plan.md`
- `docs/emr4-model-required-bureau-c5-live-preexecution-orchestration-boundary.md`
- `docs/emr4-model-required-bureau-c5-windows-endpoint-ownership-recovery.md`
- both corresponding C5 threat-model deltas under `docs/security/`
- `docs/api-spine/openapi/technical-control-live-development-recovery-commands.yaml`
- the C5 policy, examples, schemas and provider-free evidence under
  `orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/`
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`
- `docs/ariadne-agent-error-correction-register-revision-24.md`
- C5 live, rehearsal, contract, readiness-continuity and error-register tests.

Adversarially verify:

1. Windows post-termination evidence requires exact owned-process absence and
   successful exclusive reacquisition of the exact `127.0.0.1:port`; it does
   not pretend that a TCP exception or timeout proves listener absence.
2. Every Windows bind sets `SO_EXCLUSIVEADDRUSE` before `bind`, no path sets
   `SO_REUSEADDR`, and retry is restricted to EADDRINUSE/WinError 10048 within
   the bounded two-second startup interval.
3. The exact reservation is retained rather than closed during generation-2
   inherited-socket handoff; process handles, endpoint identity, fresh
   readback, rollback and final cleanup cannot be confused.
4. All real bind and HTTP-readiness attempts are counted, while cleanup and
   terminal evidence prove no owned process, listener, socket, task directory,
   open ledger or reusable capability remains.
5. The provider-visible v2 field is exactly
   `loopback_endpoint_disposition`, the truthful postfault value is
   `exact_port_reacquired`, and schemas/examples/policy/catalog/digest chains
   are mutually consistent.
6. Historical failed occupied evidence remains failed and immutable; the
   provider-free Windows lifecycle can pass while a fake provider still fails
   the outer occupied classifier because `is_live_capability` is false.
7. A fresh Ariadne runtime state is now mandatory when building the custom
   pre-execution receipt. It must bind exact event/action, all five named
   rehydration sources, current branch/HEAD/protected refs, a maximum 30-minute
   authority interval and its own digest; stale, time-less, mismatched or
   subsequently altered state must fail before any live capability.
8. Runtime admission re-hashes and revalidates the generic receipt plus runtime
   state immediately before ADC/provider/target/socket/directory capability.
9. AER-0028 truthfully records the repository defect and AER-0029 separately
   records the orchestrator's ADC-versus-gcloud credential-store guidance
   error; neither shifts responsibility to the user.
10. The Sydney Vertex, authored-synthetic, positive-thinking, no-retention,
    one-primary-plus-at-most-one-ticketed-correction, USD 0.50, deterministic
    proofreader/authority, one-use evidence and no-fallback contracts remain
    closed and unchanged.
11. `servers: []`, `paths: {}`, `security: []`, documentation-only unmounted
    status, no `app.main` mount, no GraphQL/product/database/runtime wiring, no
    patient/product data, no deployment, release, Pages or protected-ref move.

Provider-free tests are permitted. If useful, run:

`C:\\Users\\sarashera\\emr4\\.venv\\Scripts\\python.exe -B -m pytest tests/test_model_required_bureau_c5_live.py tests/test_model_required_bureau_c5_contract.py tests/test_model_required_bureau_c5_rehearsal.py tests/test_model_required_bureau_c5_plan.py tests/test_model_required_bureau_c5_implementation_readiness_continuity.py tests/test_ariadne_agent_error_register.py -q`

You may also run the repository's provider-free C5 acceptance checker. Do not
access ADC or cloud configuration; do not call Vertex; do not start any C5
target; do not open a socket/port or create a task directory; do not inspect
protected holdouts, historical diary material, patient/clinical/product data
or `docs/branding/`; do not deploy, release, rebuild Pages or move any Git ref.

## Decision contract

Report concise evidence and every material finding with file and line. If any
material uncertainty remains, require revision. End with exactly one terminal
decision line, using only `DECISION: pass` or
`DECISION: revision_required`. Do not emit a second decision line or any later
follow-up.
