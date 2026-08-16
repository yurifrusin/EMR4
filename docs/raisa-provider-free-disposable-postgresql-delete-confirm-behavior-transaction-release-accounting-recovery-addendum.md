# Delete-confirm response-release accounting recovery addendum

Date: 2026-08-16

Timestamp: 2026-08-16T14:09:56.6831899+10:00 (Australia/Brisbane)

Source HEAD: `9bb094e88076d4fe601d5a10ac4ce2d38512ef62`

Status: `explicitly_authorized_one_repair_one_fresh_attempt`

## Authority and retained failure

After the fail-closed `TX-S09_disclosed_bytes` stop published at exact task
source `9bb094e88076d4fe601d5a10ac4ce2d38512ef62`, Yuri explicitly answered yes to
the recommended narrow continuation: one candidate-versus-release accounting
repair and exactly one fresh occupied PostgreSQL attempt.

AER-0355 identifies a harness-only classification defect. The transaction
constructed canonical candidate bytes before its context manager finished. The
context manager then correctly detected a mismatched write set, raised
`DeleteConfirmScaffoldIncomplete` and rolled the transaction back, but the
harness retained the local candidate in the field it later treated as released
response evidence. The accepted product service remains byte-bound and
unchanged.

## Exact state boundary

The harness must represent these states separately:

1. `candidate_response_bytes` may exist only as a local transaction candidate;
2. successful exit from `delete_confirm_locked_transaction` is the sole point
   at which that candidate may be promoted to `released_response_bytes`; and
3. only `released_response_bytes` may populate response-disclosure evidence.

The promotion must occur after the transaction context exits successfully and
inside the surrounding `try`, so a context-exit exception cannot reach it.
New-command and replay results may be promoted only through this common
post-context boundary. Scaffold-incomplete, outer-abort, timeout, authority
denial, conflict and other non-release outcomes retain no released bytes.
Candidate bytes, bodies and values must never enter durable evidence.

## Exact repair and tests

Only these semantic files may change:

- `scripts/raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal.py`; and
- AER-0355, semantic-freeze, latch, receipt and generated pass/failure metadata.

Focused tests must prove:

- a clean new command promotes its candidate only after successful context exit;
- an exact replay promotes stored canonical bytes only after successful context exit;
- cross-artifact mismatch may construct a candidate but releases no bytes when
  the context exits with `DeleteConfirmScaffoldIncomplete`;
- a complete staged set followed by the fixed outer abort releases no bytes; and
- the AER-0353 semantic-authority wrapper is restored on every outcome.

No migration, model, product service, route, public contract or API schema may
change. In particular,
`app/services/appointment_delete_physical.py` remains bound to raw SHA-256
`8e0f0e06471560b328e5ab7af6cc9981c20ca4a58ec9eec74dbd412979f85533`.

## Admission, attempt and stop rule

Before runtime, the affected focused tests, Ruff, maintained-source
compilation, schema/whitespace checks, API Spine invariants, the canonical
196-test profile, exact product-service hash, semantic freeze and fresh
five-source preexecution receipt must pass.

Exactly one fresh occupied attempt may then run inside the unchanged owned
internal-only network, portless tmpfs PostgreSQL 16 container and fixed
loopback-relay boundary. It must pass all nine authority groups, all eleven
transaction groups and exact cleanup. Any failure or cleanup ambiguity stops
without another repair or retry. An occupied pass admits exactly one fresh
Gemini 3.7 Flash/high final veto; it does not admit a provider call during the
database rehearsal.

## Parallelism efficacy

- DeepSeek V4 Flash/high: `not_applicable`; the worker lane is closed and this
  is a tiny already-diagnosed serial repair.
- Gemini 3.7 Flash/high: `reserved`; exactly one post-pass independent veto.
- Native subagents: `declined`; the repair and single mutable database lifecycle
  are tightly coupled and delegation adds no useful independent leverage.

## Protected boundaries

Only authored-synthetic serial delete-confirm evidence is admitted. Product,
patient, clinical, historical-diary and protected data; provisioning; mounted
routes; public API/GraphQL/UI changes; providers, ADC, credentials, IAM and
external networks; concurrency, restart and unknown commit; deployment,
production, release, Pages and protected-ref movement remain closed. Preserve
`docs/branding/` and every unrelated untracked file; use explicit-path staging
only.
