# Provider-free unmounted authored-synthetic shadow-comparison rehearsal plan

Date: 2026-08-12

Source HEAD: `fb899b26966c1a171528306ae5ab49b80bacc947`

Status: `frozen_for_provider_free_unmounted_execution`

## Purpose

Exercise the accepted default-off shadow-comparison architecture as a pure,
authored-synthetic state table. The rehearsal proves that useful adapter-gap
diagnostics can be classified without importing or executing an application
route and without allowing observation to change a sealed primary result.

## Exact boundary

The evaluator receives only:

- one synthetic sealed primary result kept outside the observer input;
- one exact 24-field `ShadowRouteProjection` containing only `syn-` labels,
  closed role/purpose/shape labels, presence bits and nulls;
- one immutable generation/configuration binding;
- the accepted four-way admission controls; and
- one closed fault selector used only to rehearse failure containment.

It may call the accepted pure route-adapter function over a derived digest-only
raw envelope. It may not call the conditional-command kernel. Its only possible
observable output is zero or one 15-field `ShadowComparisonRecord` held in the
committed authored-synthetic evidence fixture.

## Frozen scenario population

Exactly eighteen scenarios are required:

1. six default-denial cases: global disabled, practice disabled, route absent,
   stale generation, missing generation state and external disable;
2. four exact-intersection admitted cases, one for each raw adapter, reproducing
   the three accepted current gaps;
3. one admitted unexpected two-gap set;
4. one admitted unexpected candidate from a complete raw projection;
5. one admitted candidate equivalent to an independently supplied semantic
   expectation;
6. one admitted candidate divergent only on `command_digest`;
7. one contained observer failure with one bounded failure record;
8. one timeout drop with no record;
9. one overflow drop with no record; and
10. one sink-failure drop after at most one record candidate, with no emitted
    record.

The four current expected-gap scenarios must cover `raw_compat_create`,
`raw_compat_update`, `raw_compat_status` and `raw_compat_delete`. Every admitted
normal scenario must use the exact current-generation/global/practice/route/no-
external-disable intersection.

## Primary-result invariant

For every scenario the evaluator canonicalizes the five primary components to
bytes before shadow admission and again after the scenario completes. The
observer is never passed the primary object. Acceptance requires equal bytes
and equal SHA-256 digests in all eighteen cases, including every simulated
failure and drop.

The synthetic primary body and headers are test values only. They contain no
patient, person, product, clinical, financial or free-text material and are
never copied into a diagnostic record.

## Failure and record semantics

- disabled observation emits no record;
- timeout and overflow stop before adapter comparison and emit no record;
- observer failure may emit one minimized `observer_failed` record;
- sink failure drops the single record candidate and emits no record;
- no scenario retries;
- no record is audit, truth, command evidence or a correctness dependency; and
- no result or failure has a return path to admission, authorization, response,
  transaction, mutation, audit, retry, latency budget, kernel eligibility or
  client behavior.

## Owned files

- this plan;
- `docs/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-design.md`;
- `docs/security/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-threat-model-delta.md`;
- `orchestration/continuity/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal/provider-free-authored-synthetic-shadow-comparison-evidence.schema.json`;
- its exact authored-synthetic evidence fixture;
- `scripts/raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal.py`;
- `tests/test_raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal.py`;
- the preplanning receipt pair; and
- exact closeout, acceptance, Yuri mailbox, Continuity/Compass updater and
  lifecycle-test artifacts if the tranche passes.

## Forbidden surfaces

- no import, execution, edit, wrapping or instrumentation of an application
  route;
- no runtime hook, observer, feature flag, thread, process, queue, sink,
  persistence, retention or aggregation;
- no database, source, watcher, event, transaction, response writer, audit
  writer or current product read;
- no network, provider call, credential, IAM or metadata access;
- no product-derived, patient, person, clinical, financial or free-text data;
- no executable tool, kernel invocation, command, write or mutation;
- no client change, header change, deployment, production, release, Pages
  rebuild or protected-ref movement; and
- no broad staging, `docs/branding/`, protected evidence or unrelated untracked
  file.

## Acceptance

The tranche passes only when:

1. one closed schema validates one exact source-bound evidence fixture;
2. the fixture contains exactly the eighteen frozen scenarios and all required
   case classes;
3. the six denied cases do not call the adapter and emit no record;
4. the four admitted current cases reproduce the exact three parent gap codes;
5. unexpected gap, unexpected candidate, equivalent and divergent candidate
   classifications match the independently frozen expectations;
6. observer failure, timeout, overflow and sink failure follow the exact
   contained dispositions above without retry;
7. all eighteen primary results remain byte-for-byte unchanged;
8. every emitted record has exactly the accepted 15 minimized fields, no
   forbidden material and no command outcome, and every scenario emits at most
   one record;
9. the evaluator imports no application/database/network/provider/process
   module and performs no runtime effect;
10. at least thirty independent hostile evidence mutations fail closed;
11. focused parent/API Spine, canonical repository-profile, source-state,
    lifecycle and Git whitespace checks pass; and
12. protected refs and every pre-existing untracked file remain unchanged.

## Recovery and next work

One bounded mechanical correction may repair a schema, fixture, pure evaluator
or assertion defect without changing the scenario population, admission
intersection, primary-result invariant, failure dispositions, minimized record
or no-feedback boundary. Any need for an application import, route execution,
runtime hook/queue/sink, persistence, product/source data, kernel call or command
is conceptual and stops this tranche.

After acceptance, the next architecture-strengthening gate in the frozen
sequence is a separately reviewed default-off runtime-instrumentation plan. It
must first freeze the narrowest possible application seam and prove default-off
behavior, dependency exclusion and primary-result independence before any
route instrumentation is implemented.
