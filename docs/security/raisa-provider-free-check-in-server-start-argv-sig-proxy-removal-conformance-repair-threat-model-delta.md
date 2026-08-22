# Threat-model delta — check-in server start argv sig-proxy removal conformance repair

Date: 2026-08-23

Timestamp: 2026-08-23T02:37:52.8034054+10:00 (Australia/Brisbane)

Status: `frozen`

Reasoning level: `high`

## Scope

This delta covers one exact unsupported Docker start-argv token deletion,
historical-source rebinding for accepted diagnosis tests, deterministic Popen
and teardown fakes, and optional object-free CLI help/version metadata. It
adds no Docker object, PostgreSQL process, SQL/database attempt, provider,
product, ordinary-practice, production, deployment, release, Pages or
protected-ref surface.

## Threats and controls

| Threat | Control | Fail-closed result |
|---|---|---|
| Repair changes more than the diagnosed token | AST and exact-diff test admits one list-element deletion only | Reject candidate |
| Removing signal option silently changes cleanup authority | Bind Docker attach help semantics, zero normal-path signals and the unchanged bounded stdin-close plus terminate/wait/kill teardown owner through static/fake tests | Reject repair |
| Stdin closes early or credentials are buffered | Deterministic Popen stream records exact write/flush order and open-until-teardown state | Reject repair |
| Historical diagnosis is weakened to fit new source | Verify old contract/evidence against exact historical Git source; current closed diagnostic refuses source drift | Reject historical reclassification |
| Test fakes call real Docker or PostgreSQL | Dependency injection plus zero-process counters and fixed metadata-only command manifest | Stop before process |
| Metadata command names an object | Exact command tuples admit only version and start-help | Reject command |
| Repair smuggles in attempt 007 or product authority | Contract/schema fix repair implemented=true while attempt_007_authorized=false and all product/provider counts zero | Reject attestation |
| Dynamic output leaks object or credential data | Closed schema stores fixed booleans, digests and enum relations only | Reject evidence |
| Unrelated worktree data is altered | Exact one-token diff, explicit-path staging and preservation checks | Stop before commit |

## Residual boundary

Deterministic conformance can prove the repaired command is inside the
installed CLI's advertised option surface and preserves the source-owned
attachment, stdin and cleanup relations. It cannot prove a container starts,
PostgreSQL becomes ready, a transaction runs or an unknown response is
recovered. Those remain a separately planned one-run attempt-007 question.
