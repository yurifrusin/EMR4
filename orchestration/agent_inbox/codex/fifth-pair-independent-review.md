# Fifth-pair independent code/security/acceptance review

Date: 2026-08-03

Reviewer scope: fresh read-only review of the complete fifth-pair candidate and
the AER-0010 serial-pytest correction. GPT Sol retains acceptance, integration,
protected-ref and baton authority.

## Findings

### High — the Diary API fixture allowlist is path-only and can admit an unexpected command method

Path: `scripts/raisa_provider_free_native_diary_application_session_route_intercepted_browser_acceptance.py:278`

The dispatcher sends every non-`OPTIONS` request for an allowlisted API path to
`_fixture_for()` without validating the HTTP method. Consequently, an
unexpected `POST`, `PUT`, `PATCH` or `DELETE` to an otherwise allowlisted path
such as `/api/v1/appointments` is fulfilled as a successful fixture response.
It is not added to `unknown_api_paths`. The summary then collapses admitted API
traffic to paths at lines 391-399, and the claimed `closed_api_fixture_allowlist`
check at lines 694-697 tests only whether an unknown path was observed.

This means a Diary regression that attempts a scheduling command can still
produce `closed_api_fixture_allowlist=true`,
`no_unexpected_external_or_provider_hosts=true` and an all-green evidence
record. That invalidates the frozen no-command/no-write and exact-fixture
acceptance claim even though the intercepted request cannot reach a real
backend.

Required correction: define an exact `(host, method, path)` allowlist; reject
and record every other tuple; preserve method in the evidence ledger; and add a
negative regression showing that a mutating method on an allowlisted read path
fails the acceptance run. The exact admitted request tuple set should also be
asserted per case.

### High — the AER-0010 wrapper is cooperative, not an OS-enforced gate for every repository pytest process

Paths:

- `scripts/ariadne_serial_pytest.py:118`
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json:384`
- `orchestration/harness_settings/sprint_worker_policy.yaml:84`

The lock is acquired only inside the new wrapper before that wrapper starts its
pytest child at lines 121-135. A direct `python -m pytest ...` process never
executes this code and therefore never contends on the lock. The two preserved
collision receipts themselves show direct pytest invocations, so the
correction still relies on every future agent obeying `required_launcher`.
That is instruction-level compliance around a capable wrapper, not an
OS-enforced serialization invariant covering “every pytest process loading
repository tests/conftest.py”.

This matters because AER-0010 arose after instruction-only serialization proved
insufficient. The register's claim that an OS-enforced launcher “replaces” that
control, and the incident's `corrected` status, are broader than the current
mechanism supports.

Required correction: acquire the shared-schema lock automatically from the
repository pytest lifecycle (for example, a session-level conftest/plugin gate),
or make direct repository pytest fail closed unless it can prove the wrapper
owns the lock. Add a cross-process regression in which one process uses the
approved wrapper and a second uses direct pytest entry; the second must wait or
fail before shared-schema setup. Then narrow or refresh the AER-0010 correction
narrative and status to match the enforced result.

## Scope and authority assessment

- Diary: the candidate is correctly labelled
  `route_intercepted_browser` / `authored_synthetic`, uses an ephemeral
  loopback static server, keeps `app.main`, database and providers out of the
  harness, exercises visible Refresh/modal controls, covers stale-result
  invalidation, enabled failure and feature-off legacy behavior, and expressly
  disclaims live/default-on/production authority. The method-admission gap
  prevents acceptance of its exact no-command/no-write network evidence.
- Davida: within this bounded static review, the separate `.invalid` OpenAPI
  artifact remains architecture-only and API-Spine-aligned. It keeps GraphQL
  read-only, makes the proposal non-mutating, derives authority from the
  authenticated application session, reserves confirmation for an authorized
  human manager/owner, defines version/freshness/replay checks, and keeps the
  future aggregate/audit/outbox/idempotency unit atomic. No mounted route,
  migration, database service, provider/model path, current permission grant or
  apply/write authority was found or claimed. No additional actionable Davida
  defect was confirmed before the parent-directed review stop.
- Agent-error register: AER-0008 and AER-0009 match their preserved failed and
  corrected preflight receipts. AER-0010 accurately records the two inadmissible
  PostgreSQL schema collisions and the later serial reruns as context; only its
  asserted durable prevention control and resulting `corrected` posture fail
  review for the reason above. Revision-3 counts and the unique AER-0010
  recurrence signature are internally consistent with the ten recorded rows.
- Closed gates remain closed by the reviewed candidate: protected evidence and
  refs, `docs/branding/`, real identity/data, patient/clinical/document data,
  providers/models, memory/RAG, arbitrary API access, runtime administrative
  writes, cloud/IAM, deployment, production and release.

## Exact review binding

The fresh receipt
`orchestration/agent_inbox/codex/fifth-pair-independent-review-rehydration-receipt.json`
passed with settings fingerprint
`sha256:6097cbd3b168e4260cfe3dfaa68993d30047a2a65647706c16b9b08e4b4ac6d5`.
Review HEAD was `ec7af55d58997ed967abce05af5fa5bbe3bbb3dd`; local/origin
`master` and local/origin `handoff/current` were all
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Core reviewed file hashes at the final binding check:

- Diary plan `sha256:7b619d2e7ad0a8f89e34ce8fdfc21dbca8bae041e03f9e0d51bb76a9bd1533c8`
- Diary harness `sha256:b9cf160a9d90207708819f07ac2daa3bd16f533c7f8e0fdc7d17e431dd13c338`
- Diary evidence `sha256:5427e11182d4031dce962ce5bcba64f9bf1771eac6bc1af5e2bde3a2f3c6a6e7`
- Diary tests `sha256:49a5efdd9c406bf36ef97065beea168cd4152593f9ed60ff0935208d7ff66b66`
- Davida plan `sha256:84f020690cf1ef97b202b2e7bc1ae8987c647213ebfd5599a7afb9ca3769bf00`
- Davida design `sha256:d4ebee3933fa119f82206cf9175beedccf059300f9eda805530b8d1b607eaa44`
- Davida OpenAPI `sha256:491978f28e07c569bb19410edf0f811533960aca3081b108a84c135a6a8404e8`
- Davida contract `sha256:7dd69acea94447b69fd2c96c798ff03b28fb9f188cc1e44a39c3d69d181643a4`
- Davida acceptance evidence `sha256:e65451530d3e16e075efc293c239603ff91c1a0e1f22872221aa60696a350022`
- Davida tests `sha256:eeeb3d43c93f7cad2f6e96c623940880556fdb2d1e26486eb520a134fe6904fc`
- Agent-error register `sha256:21d7513ff9e22ae854e4fb8a503a7acdcf61fc37fb641440d4541ba6dc531ee7`
- Serial-pytest wrapper `sha256:006f1373f0beeb8048f1d622fd6e1e6bae150e081a9b5275d45d559d1e2e8869`
- Serial-pytest tests `sha256:5bb81ec0141922f0eba3bace2de1f2d312c6cf3c15d51477c03cb1e7c76dee1c`
- Sprint-worker policy `sha256:055c23bc0b385e7bc609ccd09ec9bb49e89328deb4bbc969c99d20c060d29dbe`
- Verifier policy `sha256:c92036755d16e1255e384fbb02a773febbb8fcb5561f14f162902cd077af4fb1`

No pytest, browser, database, provider, network/external-system, staging,
commit, push or protected-ref action was performed during the candidate review.
The root-reported deterministic 130-test pass was treated as context only.

## Reviewer-local receipt incident

Before candidate inspection, the first receipt-generator invocation used
`uv run --python 3.12`. `uv` rebuilt the ignored repository `.venv`, changed
`uv.lock`, and then failed before producing a receipt because PyYAML was absent.
No package/network fallback was attempted. The tracked `uv.lock` change was
immediately restored byte-for-byte to its pre-review content, and the passed
receipt was generated with an already-installed separate interpreter. The
ignored `.venv` rebuild remains a disclosed local-environment side effect; it
did not alter any reviewed candidate artifact. Root should classify this
exact-command/scope failure under the standing incident-learning rule before
accepting a corrected review attempt.

DECISION: revision_required
