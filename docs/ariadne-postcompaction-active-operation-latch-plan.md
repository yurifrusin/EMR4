# Ariadne post-compaction active-operation latch plan

Date: 2026-08-13

Timestamp: 2026-08-13T09:14:16+10:00 (Australia/Brisbane)

Status: frozen

Source HEAD: `17add9baf2cc3616f7ee4fb8eda3481e2eb13715`

## Incident and objective

After automatic context compaction, the retained chronological last user prompt
was incorrectly treated as the controlling objective even though the durable
summary and live baton said an authorised tranche remained in progress. The
assistant answered the older side question with a terminal response and stopped.

Add the narrowest repository-enforced continuity control that makes unfinished
operation precedence explicit. A typed active-operation latch must survive
compaction, be included in every new Ariadne continuation receipt, and forbid a
terminal handback while authorised work is in progress unless Yuri explicitly
pauses, redirects or a genuine user-attention condition is present.

## Exact accepted inputs

| Path | SHA-256 |
|---|---|
| `AGENTS.md` | `01a29bd44b82a5348b61d87433bcb190bd3a481741d92da8ef7e8efd3d7c5d9b` |
| `orchestration/harness_settings/autonomous_continuation.yaml` | `c42094e894423cee662eb72fac5e3514ee6fcd3942dbad0ccb6e96dd7de083d0` |
| `orchestration/harness_settings/orchestrator_requirements.yaml` | `0ab1b894e659578e7d665d536ae232bc8325d64bdd2729b6d9a4d99910238270` |
| `docs/ariadne-autonomous-continuation.md` | `c245ca396361bfd44ad987c06cac57df80eab98e96dccc983d3ff3c5f8e60ff9` |
| `orchestration_harness/orchestrator_preflight.py` | `a960b4f4dcd4b330f93726aa54d83f1229303d7862080f23844decebc2b523cf` |
| `scripts/ariadne_orchestrator_preflight.py` | `0c69d713a8577e23db20b93623413d89f3da0d10a28ebf3aef498599e88cdf45` |
| `tests/test_ariadne_orchestrator_preflight.py` | `9d4e5bec330ea611396c096ba83656c7cc34bd705c9519cf6662982491549d8c` |
| `tests/test_ariadne_autonomous_continuation.py` | `1f7917b9b048a6c10315bce6cbaec89b47d7e17bb0d3699a37f9cd11c764b5d2` |
| `tests/fixtures/ariadne_harness/orchestrator_runtime_state.json` | `9afebbcccd3277644685c4f12703a8f6329c5a710768a6d0aff0c1e789454841` |
| `docs/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview-plan.md` | `32fa85843ccad824185b9a71e3829113776f828289d72904c9843fb66c440702` |

## Frozen contract

The latch records:

- one stable operation identifier and active tranche;
- `in_progress`, `complete`, `blocked`, `paused` or `replaced` status;
- exact source HEAD and authority source;
- completed checkpoint and next executable stage;
- retry counters and settings fingerprint;
- whether resumption after compaction is required;
- whether Yuri's attention is required and why;
- whether a terminal response is permitted and why; and
- the interruption rule that chronological recency alone, side questions and
  status requests do not replace an unfinished operation.

For `in_progress`, resumption is mandatory, Yuri attention is false, a next
stage is non-empty and terminal response permission is false. A terminal intent
against such a latch fails closed. Explicit pause/replacement and genuine
blocked/complete states must carry their own reason.

Every configured Ariadne continuation event must include the validated latch in
its runtime state and emit its exact operation/status/checkpoint/next-stage and
terminal-handback decision in the receipt. Missing or malformed latch state
returns `revision_required`.

## Artifacts

- one JSON Schema and one current latch under
  `orchestration/continuity/ariadne-active-operation-latch/`;
- one pure validator/decision module plus CLI;
- orchestrator preflight admission and receipt projection;
- policy and handover updates;
- focused hostile-mutation and policy tests; and
- closeout, Sol acceptance, Yuri paired summary and continuity update.

All newly authored tranche documents must place an Australia/Brisbane ISO 8601
timestamp alongside the date at the top. This applies to plans, threat-model
deltas, reports, closeouts, Sol acceptances and Yuri lay/technical summaries.

The current latch must preserve the suspended status-confirm route-mounting
readiness re-review checkpoint. On workflow closeout it changes directly to
that review as the next `in_progress` operation; it must not mark the programme
complete or await acknowledgement.

## Acceptance

Pass only if:

1. the exact latch schema and validator reject unknown keys and malformed types;
2. `in_progress` can never admit terminal handback, missing resume, missing next
   stage or user-attention ambiguity;
3. side-question and status-request classifications return
   `answer_then_resume`, never replacement or terminal permission;
4. explicit pause/redirect remains possible and distinct;
5. every configured continuation event fails without a latch and passes with a
   valid exact latch, emitting the terminal-handback decision;
6. at least 30 hostile mutations fail closed;
7. the durable current latch names the exact status-confirm re-review checkpoint;
8. focused, canonical, baton and whitespace gates pass; and
9. protected refs, `docs/branding/` and every unrelated untracked file remain
   unchanged, with explicit-path staging only.

## Non-authority

This is workflow metadata only. It cannot grant product, route, database,
provider, credential, IAM, browser, network, tool, command, deployment,
production, release, Pages, protected-evidence or protected-ref authority. It
does not decide whether a prompt is semantically a redirect; it makes the
conductor record that classification and fails closed when the resulting state
contradicts unfinished-work precedence.
