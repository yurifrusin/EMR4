# DeepSeek native Harness agent-creation boundary — paired closeout

Date: 2026-08-22

Timestamp: 2026-08-22T02:48:06.6590250+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

The one native attempt did not prove agent creation. It started cleanly, reached
the point where our custom runner was mounted, then stopped before it could
write the small typed receipt that would tell us its exact internal stage. The
important safety controls worked: there was no retry, model call, network use,
file target, lingering process or leftover temporary installation.

This exposed the next control weakness honestly: the Harness can still fail in
a gap between "runner mounted" and "typed stage recorded". Two automatically
generated summaries also spoke as if the intended success had occurred even
though the evidence said failure; those claims are preserved but formally
rejected.

The next tranche closes that gap with a minimal wrapper that can report only a
finite stage/error choice. It will make package loading and factory progress
observable without retaining raw error text. That is a small but material step
toward giving the orchestrator dependable control of native DeepSeek workers.

## Technical summary

- Native attempt: one process, consumed, zero retry/resume.
- Observed: exact two-event readiness, one HMR mutation, exit 2 before sidecar.
- Unknown: factory invocation, setup, private Agent/Session preparation, preset
  composition, model selection, commit and publication veto.
- Containment: broker/model/provider/network all zero; target absent; package
  seed unchanged; process and disposable root absent.
- Prelaunch defect: wrong typed contract family at preset assembly, repaired by
  an owner-contract pre-root guard; 28 focused and 205 inherited tests pass.
- Rejected output: unconditional success prose and factory-control efficacy
  claim, both hash-bound and superseded by the typed failure interpretation.
- Clockwork recovery: its first check caught a manually edited canonical latch
  before publication; the selected generation was restored byte-for-byte and
  canonical transitions are now left exclusively to the clockwork.
- Next: one separately frozen provider-free closed-subcoordinate diagnostic
  transaction using dynamic imports and a finite failure vocabulary.

Still deliberately closed: published agents/sessions, turns, DeepSeek/model or
provider requests, target edits, product/configuration/API/database/route/
adapter/flag/allowlist/grammar/client/waiting-area changes, ordinary-practice or
generic `Arrived` change, all patient/product/clinical data, production,
deployment, release, Pages and protected refs.
