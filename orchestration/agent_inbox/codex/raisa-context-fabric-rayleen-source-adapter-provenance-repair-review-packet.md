# Independent veto packet: Rayleen source-adapter provenance repair

Date: 2026-08-06

Review only the exact immutable candidate below. Do not edit or implement.

## Exact candidate

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r3`.
- Branch: `codex/review-context-fabric-rayleen-source-adapter-12fbab15`.
- Required HEAD: `12fbab157551954018e781810e4b100f05698dfb`.
- Frozen planning source: `1f008abf806c27c7e37251384f846a4a513dbad5`.
- First rejected candidate: `3edbe828fa1f261e59b8478db79d80e4c291cbbc`.
- Second rejected candidate: `1663d6d1cc79ebc8f2cb15446d6fa61196bd4fe8`.
- The worktree must remain tracked-clean and unchanged.

## Protected-safe exact path allowlist

This corrected attempt follows rejected AER-0041. Do not use `rg --files`,
`git ls-files`, recursive directory listing, broad repository search, globbed
discovery or any command that can enumerate an unnamed path. Read only these
exact paths:

- `AGENTS.md`;
- `docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter-plan.md`;
- `docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter-design.md`;
- `docs/security/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter-threat-model-delta.md`;
- `scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter.py`;
- `scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter_acceptance.py` (read only; never execute);
- `orchestration/continuity/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter/adapter-result.schema.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter/acceptance-evidence.schema.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter/authored-synthetic-waiting-room-frame.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter/provider-free-acceptance-evidence.json`;
- the eight exact test paths named below; and
- this packet, its exact-worktree preflight, the sanitized AER-0041 failure
  receipt and the corrected predispatch receipt in the primary task worktree.

Do not read any other path. Imports exercised by the exact pytest commands are
allowed to execute normally, but do not open or search their source manually.

## Prior vetoes to reproduce

1. The nominal result schema described only evidence, so a resealed unknown
   envelope property crossed the direct nested handoff.
2. The first repair compared duplicated provenance fields only; fully resealed
   source-frame, binding, grant and digest-derived-id detachment crossed the
   extractor. It also blocked elapsed-only and threshold-only grants.

## Exact repair under review

The handoff now receives the original authoritative frame, binding, grant and
alias manifest, runs the pure adapter again, requires canonical equality with
the supplied result and returns only a deep copy of the recomputed envelope.
Direct validation additionally binds envelope id/revision to the source-frame
digest suffix. Elapsed and threshold are independently optional; when both
exist their deterministic relationship is checked. A 16-subset parameter
matrix covers every combination of practitioner/status/elapsed/threshold.

Adversarially verify:

- fully resealed detachment of source-frame, binding, grant, alias-manifest,
  session, envelope id/revision, output entry values and limits rejects before
  parent handoff;
- changing the caller-supplied authoritative objects cannot be sourced from the
  result/candidate itself and still passes all original authority/seal/source
  validation;
- canonical recomputation is deterministic, non-recursive and cannot extend
  TTL, cardinality or byte limits;
- all sixteen waiting-field grant subsets compose, especially elapsed-only and
  threshold-only, without leaking an ungranted practitioner/status/derived
  field;
- nested output schemas remain recursively closed and Python booleans cannot
  satisfy integer positions;
- the positive extractor-built envelope alone replaces the hand-authored
  waiting source and the unchanged parent proofreader returns `RELEASE`;
- committed evidence is 18/18, byte/hash reproducible and schema-bound; and
- Current-weave source/evidence are byte-identical and no app/API/UI/database/
  watcher/provider/command/deployment/Pages/protected-ref surface was added.

Using `C:\Users\sarashera\emr4\.venv\Scripts\python.exe`, run only
non-regenerative provider-free tests/static checks. At minimum collect and run:

- focused source adapter: expected 36;
- exact seven-file inherited A4/Context Fabric packet: expected 195;
- agent-error register at the immutable candidate: expected 43.

Use exactly these test paths, without discovery:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter.py tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py tests/test_raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py tests/test_raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_rehearsal.py tests/test_model_required_bureau_a4_product_read.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_ariadne_agent_error_register.py -q
```

The first command must run 36 tests, the second 195 and the third 43 at
candidate HEAD `12fbab157...`. The primary task worktree now contains one new
AER-0041 regression, so a primary-tree register run has 44 tests; do not
substitute that mutable primary count for the immutable candidate count.

The first corrected reviewer run exposed AER-0042: the packet had accidentally
named the three-test Context Fabric direction file where the accepted 31-test
Fabric/Memory contract file belonged. The observed 167 count was therefore
exactly `195 - 31 + 3`, not a candidate or pytest discrepancy. The command
above is the corrected immutable seven-file packet; its required count remains
195.

Do not execute the acceptance generator in the review worktree. Do not inspect
`docs/branding/`, ADC/cloud/provider/product/patient/protected data, deploy,
release, rebuild Pages or move refs. Report exact before/after HEAD/status,
machine counts, findings by severity, claims not established, and exactly one
terminal decision: `pass` or `revision_required`.
