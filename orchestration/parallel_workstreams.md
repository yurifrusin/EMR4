# EMR4 Parallel Workstreams

This is the live board for Codex-orchestrated parallel work. `AGENTS.md` remains the
single source of truth for durable project state; this file tracks active branch work.
For the layer between long phases and tactical sprints, use
`orchestration/phase_programmes.md`.

## Sprint H64: Bernie Interpretation Harness Independent Review Integration

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification pending |
| Product Goal | Integrate a non-Ariadne adversarial review of the interpretation readiness/gate stack and turn findings into bounded follow-up sprints |
| Worker Shape | DeepSeek Flash read-only reviewer; Ariadne integration |
| In Scope | Source-safe review artifact, artifact guard tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; readiness CLI sample; H64 review artifact tests plus interpretation readiness guard cluster (306 passed); leakage lint; `git diff --check` |

## Sprint H63: Bernie Interpretation Harness Independent Review Brief

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Make the next non-Ariadne review lane explicit and bounded before any larger runtime/provider/trove proposal |
| Worker Shape | Ariadne implementation of review brief; future independent reviewer consumes the brief |
| In Scope | Source-safe review brief, guard tests, protocol alert, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; readiness CLI sample; independent-review/readiness/protocol-alert/release-gate/review/runtime-gate/runtime-isolation guard cluster (303 passed); leakage lint; `git diff --check` |

## Sprint H62: Bernie Interpretation Harness Readiness Snapshot Assertion

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Make the readiness CLI fail closed unless generated readiness matches the committed blocked snapshot |
| Worker Shape | Ariadne implementation |
| In Scope | Snapshot assertion in readiness CLI, mismatch/missing snapshot tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; readiness CLI sample; interpretation/report/protocol-alert/readiness/snapshot/release-gate/review/runtime-gate/runtime-isolation/manifest/route-contract guard cluster (300 passed); leakage lint; `git diff --check` |

## Sprint H61: Bernie Interpretation Harness Combined Readiness Fail-Closed Tests

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Ensure the combined readiness command itself rejects unblocked gates and invalid fixture inputs |
| Worker Shape | Ariadne implementation |
| In Scope | Combined readiness negative tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; readiness CLI sample; interpretation/report/protocol-alert/readiness/snapshot/release-gate/review/runtime-gate/runtime-isolation/manifest/route-contract guard cluster (297 passed); leakage lint; `git diff --check` |

## Sprint H60: Bernie Interpretation Harness Readiness Protocol Alert

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Put the interpretation readiness gate in worker-facing protocol alerts so future agents see it during handin |
| Worker Shape | Ariadne implementation |
| In Scope | Protocol alert, static alert guard tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; readiness CLI sample; interpretation/report/protocol-alert/readiness/snapshot/release-gate/review/runtime-gate/runtime-isolation/manifest/route-contract guard cluster (294 passed); leakage lint; `git diff --check` |

## Sprint H59: Bernie Interpretation Harness Blocked-Readiness Snapshot

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Commit an aggregate-only golden snapshot of the blocked readiness status so changes are explicit and reviewable |
| Worker Shape | Ariadne implementation |
| In Scope | Blocked readiness snapshot fixture, snapshot tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; readiness CLI sample; interpretation/report/readiness/snapshot/release-gate/review/runtime-gate/runtime-isolation/manifest/route-contract guard cluster (292 passed); leakage lint; `git diff --check` |

## Sprint H58: Bernie Interpretation Harness Readiness/Gate Review

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Record a bounded adversarial review of the readiness/gate stack so blocked readiness remains explicit |
| Worker Shape | Ariadne local adversarial review |
| In Scope | Review artifact, artifact guard tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; readiness CLI sample; interpretation/report/readiness/release-gate/review/runtime-gate/runtime-isolation/manifest/route-contract guard cluster (289 passed); leakage lint; `git diff --check` |

## Sprint H57: Bernie Interpretation Harness Runtime Isolation Guard

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Prove production app code has not started importing the provider-free interpretation harness tooling or historical diary gate materials |
| Worker Shape | Ariadne implementation |
| In Scope | Runtime source isolation tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; readiness CLI sample; interpretation/report/readiness/release-gate/runtime-gate/runtime-isolation/manifest/route-contract guard cluster (287 passed); leakage lint; `git diff --check` |

## Sprint H56: Bernie Interpretation Harness Readiness Release Gate

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Make the combined readiness command part of Bernie release-gate protocol before runtime/provider/trove wiring can be proposed |
| Worker Shape | Ariadne implementation |
| In Scope | Release-gate doc hook, static protocol tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; readiness CLI sample; interpretation/report/readiness/release-gate/runtime-gate/manifest/route-contract guard cluster (284 passed); leakage lint; `git diff --check` |

## Sprint H55: Bernie Interpretation Harness Combined Readiness Check

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Provide one provider-free command showing the harness is coherent while still blocked from runtime/provider/trove access |
| Worker Shape | Ariadne implementation |
| In Scope | Combined readiness CLI/helper, safe status output, tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; readiness CLI sample; interpretation/report/readiness/runtime-gate/manifest/route-contract guard cluster (282 passed); leakage lint; `git diff --check` |

## Sprint H54: Bernie Interpretation Harness Runtime Gate Checker

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Provide a reusable provider-free CLI/importable check for the blocked runtime/provider gate |
| Worker Shape | Ariadne implementation |
| In Scope | Runtime gate checker script, safe status output, negative drift tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; gate-check CLI sample; report CLI sample; interpretation/report/runtime-gate/manifest/route-contract guard cluster (279 passed); leakage lint; `git diff --check` |

## Sprint H53: Bernie Interpretation Harness Runtime Gate

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Add a blocked-by-default gate before interpretation harness work can move toward runtime routes or providers |
| Worker Shape | Ariadne implementation |
| In Scope | Runtime/provider gate JSON, blocked-scope tests, pause trigger tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; interpretation/report/runtime-gate/manifest/route-contract guard cluster (274 passed); leakage lint; `git diff --check` |

## Sprint H52: Bernie Interpretation Harness Report Input Guards

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Make alternate report fixture inputs fail closed when missing, empty, or structurally incomplete |
| Worker Shape | Ariadne implementation |
| In Scope | Report input guards, temporary-directory negative tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; report CLI sample; interpretation/report/manifest/route-contract guard cluster (270 passed); leakage lint; `git diff --check` |

## Sprint H51: Bernie Interpretation Harness Report Safety Assertion

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Make the safe aggregate report fail closed if report fields drift toward payload, runtime authority, or contract mismatch |
| Worker Shape | Ariadne implementation |
| In Scope | Report safety assertion, CLI assertion hook, negative tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; report CLI sample; interpretation/report/manifest/route-contract guard cluster (266 passed); leakage lint; `git diff --check` |

## Sprint H50: Bernie Interpretation Harness Safe Aggregate Report

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Provide a provider-free aggregate report over harness fixtures without exposing authored utterance text |
| Worker Shape | Ariadne implementation |
| In Scope | Safe report CLI/helper, report tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; report CLI sample; interpretation/report/manifest/route-contract guard cluster (263 passed); leakage lint; `git diff --check` |

## Sprint H49: Bernie Interpretation Harness Bounded Contract Review

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Review the fixture-backed frame contract surface and harden concrete invariant escape hatches |
| Worker Shape | Ariadne local adversarial review |
| In Scope | Bounded review artifact, unknown-dispatch assertion hardening, regression test, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; interpretation/manifest frame-shape/route-contract guard cluster (260 passed); leakage lint; `git diff --check` |

## Sprint H48: Bernie Interpretation Harness Frame Contract Matrix

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Make projected frame expectations fixture-backed so future utterance additions cannot silently loosen provider-style contracts |
| Worker Shape | Ariadne implementation |
| In Scope | Authored projected-frame contract fixture, dispatch coverage tests, per-frame contract assertions, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; interpretation/manifest frame-shape/route-contract guard cluster (259 passed); leakage lint; `git diff --check` |

## Sprint H47: Bernie Interpretation Harness Clarify-Frame Dispatch

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Exercise the remaining fake-provider frame kind with provider-free clarification dispatch for explicit ambiguity |
| Worker Shape | Ariadne implementation |
| In Scope | `request_clarification` dispatch, patient-context and reason-code clarify projections, authored synthetic fixtures, positive/negative tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database reads/writes, live patient matching, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; interpretation/manifest frame-shape/route-contract guard cluster (213 passed); leakage lint; `git diff --check` |

## Sprint H46: Bernie Interpretation Harness Provider-Style Copy Contract

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Make projected interpretation frames carry safe receptionist-facing copy before richer fake-provider scenario expansion |
| Worker Shape | Ariadne implementation |
| In Scope | Provider-style copy on proposal/read_request/refusal projections, copy invariants, positive/negative tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database writes, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; interpretation/manifest frame-shape/route-contract guard cluster (195 passed); leakage lint; `git diff --check` |

## Sprint H45: Bernie Interpretation Harness Projected Frame Invariants

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Guard the interpretation harness's own dispatch-to-frame contract before richer fake-provider scenarios consume it |
| Worker Shape | Ariadne implementation |
| In Scope | Projected frame invariant helper, positive/negative tests, docs/handover updates |
| Out Of Scope | Runtime routes, UI, providers, database writes, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; interpretation/manifest frame-shape guard cluster (152 passed); leakage lint; `git diff --check` |

## Sprint H44: Reviewer-Informed Interpretation Phrase Coverage

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Make frame-kind expectations fixture-driven and add realistic receptionist phrase/safety coverage from external review |
| Worker Shape | Ariadne implementation with external reviewer input |
| In Scope | Fixture `expected_frame_kind`, receptionist phrase fixtures, deterministic rule expansion, unsafe phrase fixes, docs/handover updates |
| Out Of Scope | Runtime dispatch, routes, UI, live providers, database writes, memory persistence, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG |
| Verification | `py_compile`; interpretation/manifest frame-shape/route-contract guard cluster (148 passed); leakage lint; `git diff --check` |

## Sprint H43: Bernie Interpretation Harness Frame-Shape Preparation

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Project deterministic interpretation results into fake-provider-compatible frame shapes without calling providers |
| Worker Shape | Ariadne implementation |
| In Scope | Result-to-frame projection, manifest frame-shape validation tests, docs/handover updates |
| Out Of Scope | Runtime dispatch, routes, UI, live providers, database writes, memory persistence, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG |
| Verification | `py_compile`; interpretation/manifest frame-shape/route-contract guard cluster (97 passed); leakage lint; `git diff --check` |

## Sprint H42: Bernie Interpretation Harness Result Invariants

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Make interpretation harness result shapes self-checking so dispatch and route authority cannot drift apart |
| Worker Shape | Ariadne implementation |
| In Scope | Result invariant helper, positive/negative tests, docs/handover updates |
| Out Of Scope | Runtime dispatch, routes, UI, live providers, database writes, memory persistence, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG |
| Verification | `py_compile`; interpretation/route-contract/action-grammar guard cluster (91 passed); leakage lint; `git diff --check` |

## Sprint H41: Adversarial Bernie Interpretation Harness Coverage

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Make the provider-free interpretation harness fail closed on unsafe or boundary-bypassing receptionist utterances |
| Worker Shape | Ariadne implementation |
| In Scope | Unsafe-instruction dispatch, adversarial authored fixtures, harness tests/docs/handover updates |
| Out Of Scope | Runtime dispatch, routes, UI, providers, database writes, memory persistence, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG |
| Verification | `py_compile`; leakage lint; interpretation/route-contract/action-grammar guard cluster (89 passed after static-scan correction); `git diff --check` |

## Sprint H40: Provider-Free Bernie Interpretation Harness Scaffold

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Start the Bernie Interpretation Harness with authored synthetic utterance-to-grammar mapping and no runtime authority |
| Worker Shape | Ariadne implementation |
| In Scope | Pure interpretation harness, authored synthetic fixture, tests, docs, handover updates |
| Out Of Scope | Runtime dispatch, routes, UI, providers, database writes, memory persistence, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG |
| Verification | `py_compile`; interpretation/route-contract/action-grammar guard cluster (82 passed); leakage lint; `git diff --check` |

## Sprint H39: Planned Action Promotion Checklist

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Define the gates required before planned native Diary grammar verbs can become executable |
| Worker Shape | Ariadne implementation |
| In Scope | Static promotion checklist, tests, docs, handover updates |
| Out Of Scope | Runtime dispatch, routes, UI, providers, database writes, memory persistence, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG |
| Verification | `py_compile`; planned-action/route-contract/action-grammar guard cluster (71 passed); leakage lint; `git diff --check` |

## Sprint H38: Read-Only Vs Mutating Route Boundary Tests

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Prove route contracts keep read-only/meta verbs away from proposal/confirm/raw mutation surfaces and keep mutating verbs behind signed confirmation |
| Worker Shape | Ariadne implementation |
| In Scope | Route-contract boundary tests, handover updates |
| Out Of Scope | Runtime dispatch, routes, UI, providers, database writes, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; route-contract/action-grammar guard cluster (64 passed); leakage lint; `git diff --check` |

## Sprint H37: Grammar-To-Route Contract Inventory

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Map every native Diary grammar verb to current backend route authority without adding dispatch or write power |
| Worker Shape | Ariadne implementation |
| In Scope | Pure route-contract inventory, tests, docs, handover updates |
| Out Of Scope | Runtime dispatch, routes, UI, providers, database writes, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; route-contract/action-grammar/replay guard cluster (75 passed); leakage lint; `git diff --check` |

## Sprint H36: Native Diary Action Alias Coverage

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Keep the public free-string action bridge explicit for all current grammar verbs, including planned-not-implemented aliases |
| Worker Shape | Ariadne implementation |
| In Scope | Test-only alias matrix and planned-action non-executable assertions |
| Out Of Scope | Runtime dispatch, routes, UI, providers, database writes, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; action grammar/replay/H15 fixture guard cluster (71 passed); leakage lint; `git diff --check` |

## Sprint H35: Action-Grammar Replay Fixture Schema Hardening

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Keep authored synthetic replay fixtures as grammar-shape evidence only, without payload-like route/identity/evidence fields |
| Worker Shape | Ariadne implementation |
| In Scope | Test-only replay loader schema allowlist and negative tests |
| Out Of Scope | Runtime routes, UI, providers, database writes, local trove processing, H-series profile consumption, H15 runtime wiring, RAG/GraphRAG/memory |
| Verification | `py_compile`; action-grammar replay/grammar/H15 fixture guard cluster (50 passed); leakage lint; `git diff --check` |

## Sprint H34: H15 Read-Only Explanation Preview Endpoint

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Expose a dev-only/auth-gated static preview of the H15 read-only explanation boundary without adding runtime authority |
| Worker Shape | Ariadne implementation |
| In Scope | Bernie dev endpoint, route tests, source-safe doc, handover updates |
| Out Of Scope | Runtime H15 fixture import, provider calls, Access AI/RAG/GraphRAG/memory persistence, route/UI/database writes, broad full-trove processing |
| Verification | `py_compile`; leakage lint; dev fixture and route/advisory guard cluster (65 passed); `git diff --check` |

## Sprint H33: H15 Route Explanation Boundary

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Prove H15 advisory frames remain read-only at the reception-context/route boundary |
| Worker Shape | Ariadne implementation |
| In Scope | Route-boundary tests and source-safe doc |
| Out Of Scope | New endpoint, runtime H15 adapter wiring, RAG/GraphRAG, provider calls, memory persistence, route/UI/database writes, broad full-trove processing |
| Verification | `py_compile`; route/advisory boundary tests; leakage lint; focused guard cluster (44 passed); `git diff --check` |

## Sprint H32: H15 Advisory-Only Adapter Proposal

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Prove H15 read-only candidates can map to advisory-only practice knowledge in tests without runtime wiring |
| Worker Shape | Ariadne implementation |
| In Scope | Test-only adapter, advisory-frame tests, boundary proposal doc |
| Out Of Scope | Runtime adapter wiring, RAG/GraphRAG, provider calls, memory persistence, route/UI/database writes, broad full-trove processing |
| Verification | `py_compile`; leakage lint; H15 advisory/practice-knowledge boundary tests (42 passed); `git diff --check` |

## Sprint H31: Access-AI and Read-Only Memory Boundary Review

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Define and guard the boundary before any historical-diary RAG, GraphRAG, Access AI, or memory work |
| Worker Shape | Ariadne review and static guard tests |
| In Scope | Boundary doc, runtime import/source guards for Access AI/practice-knowledge/Diary/Bernie modules |
| Out Of Scope | RAG/GraphRAG implementation, provider calls, runtime memory integration, route/UI/database writes, broad full-trove processing |
| Verification | `py_compile`; boundary tests; leakage lint; focused historical-diary/practice-knowledge guard cluster (92 passed); `git diff --check` |

## Sprint H30: H15 Read-Only Candidate Replay Wiring

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Prove hand-authored H15 read-only candidates consume the deterministic action-grammar replay harness |
| Worker Shape | Ariadne implementation |
| In Scope | Test-only replay wiring from H15 candidates to R30 action grammar replay |
| Out Of Scope | Generated local payload commits, broad full-trove processing, provider calls, RAG/GraphRAG/memory, route/UI/database writes |
| Verification | `py_compile`; H15 candidate replay tests; leakage lint; focused guard cluster (56 passed); `git diff --check` |

## Sprint H29: Hand-Authored H15 Semantic Candidate Fixtures

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Add a committed synthetic fixture family from the reviewed read-only H28 shape without copying local derived payloads |
| Worker Shape | Ariadne implementation |
| In Scope | Small authored fixture JSON, read-only grammar guards, no-local/no-mutating/no-H-series tests |
| Out Of Scope | Generated local payload commits, broad full-trove processing, provider calls, RAG/GraphRAG/memory, route/UI/database writes |
| Verification | `py_compile`; leakage lint; H15/H28/H29 guard cluster (55 passed); `git diff --check` |

## Sprint H28: Semantic Candidate Builder Adversarial Review

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Review H27 candidate semantics before any committed semantic fixture promotion |
| Worker Shape | Ariadne adversarial review and bounded repair |
| In Scope | Review doc, mutating-action downgrade to read-only explanation candidate, synthetic test update, local ignored candidate regeneration |
| Out Of Scope | Broad full-trove processing, committed generated local payloads, provider calls, RAG/GraphRAG/memory, route/UI/database writes |
| Verification | `py_compile`; ignored candidate regeneration/validation; leakage lint; neutral aggregate validation; focused H15/H28 pytest cluster (52 passed); `git diff --check` |

## Sprint H27: Bounded H15 Semantic Prototype

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Run the approved tiny local-only H15 semantic prototype and commit only source-safe tooling/docs/tests |
| Worker Shape | Ariadne implementation and local run |
| In Scope | Semantic candidate builder, synthetic tests, one ignored local 80-sample run, source-safe summary |
| Out Of Scope | Broad full-trove processing, committed generated local payloads, provider calls, RAG/GraphRAG/memory, route/UI/database writes |
| Verification | `py_compile`; H5 neutral validation on ignored aggregate; semantic fixture validation on ignored candidates; leakage lint; focused H15/H27 pytest cluster (52 passed); `git diff --check` |

## Sprint H26: H15 Approval Recording

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Record Yuri's H15 approval exactly within the drafted bounded scope |
| Worker Shape | Ariadne implementation |
| In Scope | Approved gate payload, decision note, tests proving draft remains blocked and approved payload passes, handover updates |
| Out Of Scope | Running semantic extraction, raw `local_data`, ignored JSON, broad full-trove processing, provider calls, route/UI/database writes, memory/RAG/GraphRAG |
| Verification | `py_compile`; gate validation on default template, draft, and approved payload; leakage lint over `tests docs`; focused H15/H23/H-series pytest cluster (47 passed); `git diff --check` |

## Sprint H25: H15 Approval-Payload Draft

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Draft a concrete H15 approval-payload packet for Yuri's decision without approving H15 |
| Worker Shape | Ariadne implementation |
| In Scope | Blocked draft JSON, review doc, H15 validator scope/expiry hardening, tests proving draft remains blocked |
| Out Of Scope | Approving H15, raw `local_data`, ignored JSON, semantic fixture promotion, full-trove processing, provider calls, route/UI/database writes |
| Verification | `py_compile`; draft/template gate validation; leakage lint over `tests docs`; focused H15/H23/H-series pytest cluster (46 passed); `git diff --check` |

## Sprint H24: Semantic Guardrails Adversarial Review

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Review and tighten the H23 validator/leakage-lint surface before any H15 approval-payload draft |
| Worker Shape | Ariadne adversarial review |
| In Scope | Source-safe review doc, grammar-drift guard, approval-expiry shape guard |
| Out Of Scope | Raw `local_data`, ignored JSON, semantic fixture promotion, H15 approval, full-trove processing, provider calls, route/UI/database writes |
| Verification | `py_compile`; leakage lint over `tests docs`; blocked H15 gate validation; focused H23/H15/H-series pytest cluster (43 passed); `git diff --check` |

## Sprint H23: Semantic Validator and Leakage Lint Extensions

| Item | Value |
|---|---|
| Status | Integrated locally; focused verification passed |
| Product Goal | Implement the synthetic validator and leakage-lint extensions required by the H22 gate-review packet while H15 stays blocked |
| Worker Shape | Ariadne implementation |
| In Scope | Semantic-mode validator, source/doc/test leakage lint, synthetic fail-closed tests, CI workflow hook |
| Out Of Scope | Raw `local_data`, ignored JSON, semantic fixture promotion, reviewed approval payload approval, full-trove processing, provider calls, route/UI/database writes |
| Verification | `py_compile`; leakage lint over `tests docs`; H15 blocked gate validation; `pytest tests/test_historical_diary_output_safety.py tests/test_historical_diary_leakage_lint.py tests/test_historical_diary_deidentification_gate.py tests/action_grammar_replay tests/test_h_series_profile_consistency.py -q`; `git diff --check` |

## Sprint H22: Semantic Gate-Review Packet

| Item | Value |
|---|---|
| Status | Integrated locally; source-safe verification passed |
| Product Goal | Define the smallest reviewable surface before Yuri may consider opening H15 semantic fixture promotion |
| Worker Shape | Ariadne packet draft with DeepSeek sidecar adversarial criteria |
| In Scope | Source-safe documentation, tiny local-only prototype plan, validator-extension requirements, leakage-lint requirements, approval payload shape, sprint-engine pause points |
| Out Of Scope | Raw `local_data`, ignored JSON, broad full-trove processing, semantic fixture promotion, provider calls, route/UI/database writes, RAG/GraphRAG memory |
| Verification | H15 gate validator on committed blocked template; `.venv\Scripts\pytest.exe tests\test_historical_diary_deidentification_gate.py tests\action_grammar_replay tests\test_h_series_profile_consistency.py -q`; `git diff --check`; sidecar review inspection |

## Sprint R30: Deterministic Synthetic Action Replay Consumer

| Item | Value |
|---|---|
| Status | Integrated locally; verification passed |
| Product Goal | Prove the R29 action grammar has a deterministic synthetic replay consumer before any H15 semantic work or full-trove mining |
| Worker Shape | Claude implementation-plan lane, Codex/DeepSeek adversarial review lane, Antigravity/Gemini receptionist acceptance review |
| In Scope | Synthetic-only replay fixture/test design, grammar consumption invariants, no-write/no-provider/no-trove boundaries |
| Out Of Scope | Raw `local_data`, ignored JSON, H15 semantic fixtures, broad full-trove processing, route/UI/provider changes, autonomous writes |
| Verification | `py_compile`; `pytest tests/action_grammar_replay tests/test_diary_action_grammar.py tests/test_h_series_profile_consistency.py -q`; `git diff --check` |

### Workstream R30-A - Claude Action Grammar Replay Consumer Plan

| Item | Value |
|---|---|
| Owner | Claude |
| Branch | `claude/action-grammar-replay-consumer` |
| Task Packet | `orchestration/agent_inbox/claude/claude-r30-action-grammar-replay-consumer.md` |
| Goal | Produce an implementation-ready plan for the smallest deterministic synthetic replay consumer over the R29 grammar |
| In Scope | Synthetic fixtures/tests/helpers, existing scenario/replay patterns, R29 grammar contracts |
| Out of Scope | Code edits before plan approval, raw trove, semantic fixtures, UI/routes |
| Verification | Plan packet inspection |
| Status | Plan_ready (Claude session-limited; plan in codex/r30-grammar-replay-consumer-plan) |

### Workstream R30-B - Codex/DeepSeek Replay Consumer Adversarial Review

| Item | Value |
|---|---|
| Owner | Codex/DeepSeek Flash |
| Branch | `codex/r30-replay-consumer-adversarial-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-r30-replay-consumer-adversarial-review.md` |
| Goal | Challenge tautology, hidden write authority, semantic leakage, and weak no-write replay assertions |
| In Scope | Source-safe adversarial review artifact or plan packet |
| Out of Scope | Production implementation, UI, raw trove, semantic labelling |
| Verification | Review artifact inspection |
| Status | Integrated |

### Workstream R30-C - Gemini Replay Consumer Receptionist Review

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-r30-replay-consumer-receptionist-review.md` |
| Goal | Define receptionist-domain acceptance criteria for synthetic fake day/action replay |
| In Scope | `docs/receptionist_review_r30.md` after plan approval |
| Out of Scope | Code/tests, UI edits, raw trove, semantic H-series mapping |
| Verification | Source-safe review artifact |
| Status | Integrated |

## Sprint R29: Native Bernie/Diary Action Grammar Foundation

| Item | Value |
|---|---|
| Status | Integrated locally; verification passed |
| Product Goal | Define the smallest native backend/domain action grammar foundation before replay consumers, H15 semantic work, or broad full-trove mining |
| Worker Shape | Claude implementation-plan lane, Codex/DeepSeek adversarial review lane, Antigravity/Gemini receptionist acceptance review |
| In Scope | Plan-gated backend/domain action vocabulary, envelopes, confirmation/write-authority invariants, focused test strategy, source-safe review artifacts |
| Out Of Scope | Production code before plan approval, frontend UI, taskpane, raw `local_data`, H15 semantic fixtures, provider calls, broad trove processing, autonomous writes |
| Verification | `py_compile`; `pytest tests/test_diary_action_grammar.py -q`; adjacent envelope/confirm/manifest/domain pytest cluster; `git diff --check` |

### Workstream R29-A - Claude Native Action Grammar Plan

| Item | Value |
|---|---|
| Owner | Claude |
| Branch | `claude/native-action-grammar-foundation` |
| Task Packet | `orchestration/agent_inbox/claude/claude-r29-native-action-grammar-foundation.md` |
| Goal | Produce an implementation-ready plan for the smallest backend/domain native action grammar contract |
| In Scope | Existing Bernie/Diary backend contracts, proposal/confirm routes, schemas, tests, R28 Fable recommendation |
| Out of Scope | Code edits before plan approval, UI, raw trove, semantic fixtures |
| Verification | Plan packet inspection |
| Status | Integrated |

### Workstream R29-B - Codex/DeepSeek Action Grammar Adversarial Review

| Item | Value |
|---|---|
| Owner | Codex/DeepSeek Flash |
| Branch | `codex/r29-action-grammar-adversarial-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-r29-action-grammar-adversarial-review.md` |
| Goal | Challenge overreach, hidden write authority, compatibility risks, and H-series/full-trove boundary mixing |
| In Scope | Source-safe adversarial review artifact or plan packet |
| Out of Scope | Production implementation, UI, raw trove, semantic labelling |
| Verification | Review artifact inspection |
| Status | Integrated |

### Workstream R29-C - Gemini Receptionist Acceptance Review

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-r29-action-grammar-receptionist-review.md` |
| Goal | Define receptionist-domain acceptance criteria for the first action grammar foundation without changing visible UI |
| In Scope | `docs/receptionist_review_r29.md` after plan approval |
| Out of Scope | Code/tests, UI edits, raw trove, semantic H-series mapping |
| Verification | Source-safe review artifact |
| Status | Integrated |

## Sprint R27: H-Series Profile Consumption Tests

| Item | Value |
|---|---|
| Status | Integrated locally; verification passed |
| Product Goal | Consume the R26 H-series profile layer in deterministic no-write/non-semantic test coverage |
| Worker Shape | Claude implementation lane, DeepSeek Flash adversarial test-design review, Antigravity/Gemini receptionist acceptance review |
| In Scope | Focused tests over `tests/fixtures/h_series_profiles/`, profile schema docs, review artifacts |
| Out Of Scope | Raw `local_data`/ignored JSON, semantic appointment labelling, Bernie executable scenario insertion, frontend UI, production routes, live providers |
| Verification | Profile pytest, py_compile for touched Python, review artifacts, `git diff --check` |
| Integration Note | Ariadne integrated the narrow R27 guard locally after a source-safe DeepSeek adversarial review artifact was present in the integration worktree; queued external lanes were not required for this small boundary-hardening slice |

### Workstream R27-A - Claude H-Profile No-Write Test Consumption

| Item | Value |
|---|---|
| Owner | Claude |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-r27-h-profile-no-write-test-consumption.md` |
| Goal | Add focused deterministic tests that consume H-series profiles as no-write/non-semantic invariants |
| In Scope | `tests/test_h_series_profile_consistency.py` or a narrow new focused test; profile fixtures/docs only if needed |
| Out of Scope | Raw trove, Bernie scenario corpus insertion, production code, frontend |
| Verification | `py_compile`; `pytest tests/test_h_series_profile_consistency.py -q`; `git diff --check` |
| Status | Superseded by Ariadne-local schema/isolation guard implementation |

### Workstream R27-B - DeepSeek Profile Consumption Adversarial Review

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via `deepseek-worker` |
| Branch | subagent fork / `codex-r27-deepseek-profile-consumption-adversarial-review` packet |
| Task Packet | `orchestration/agent_inbox/codex/codex-r27-deepseek-profile-consumption-adversarial-review.md` |
| Goal | Challenge tautologies, semantic leakage, weak no-write assertions, and schema drift |
| In Scope | `docs/adversarial/h_series_profile_consumption_review_r27.md` or narrow non-overlapping tests |
| Out of Scope | Raw trove, semantic labels, production code, frontend, live providers |
| Verification | Review artifact inspection; tests if added |
| Status | Integrated locally as source-safe adversarial artifact |

### Workstream R27-C - Gemini Receptionist Acceptance Review

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-r27-h-profile-receptionist-acceptance-review.md` |
| Goal | Define receptionist-facing acceptance criteria for H-profile tests without semantic overreach |
| In Scope | `docs/receptionist_review_r27.md` only after plan approval |
| Out of Scope | Code/tests, raw trove, semantic mapping, live providers |
| Verification | Tangible source-safe acceptance review artifact |
| Status | Superseded by Ariadne-local source-safe receptionist acceptance note |

## Sprint R28: Fable Full-Trove Readiness Review

| Item | Value |
|---|---|
| Status | Integrated locally |
| Product Goal | Use Claude Fable before its July 7 access deadline to decide when EMR4 should utilise the full local diary trove |
| Worker Shape | Claude Fable 5 plan/review consult on disposable branch `claude/fable-full-trove-readiness` |
| In Scope | Read committed R27/H-series docs and produce a source-safe readiness recommendation |
| Out Of Scope | Production code, tests, raw `local_data`, ignored JSON, semantic labelling, provider calls, frontend UI, migrations, broad trove processing |
| Verification | Plan/review artifact inspection; worker `git diff --check` |
| Result | Fable recommends native Bernie/Diary action grammar first, deterministic replay consumer second, H22 gate-review packet third, and one-time full-trove mining only after Yuri approves H15 |

## Sprint R26: H-Series Neutral Scenario Bridge

| Item | Value |
|---|---|
| Status | Integrated locally; external reviews triaged |
| Product Goal | Convert H21 neutral diary movement profiles into source-safe deterministic Diary/Bernie scenario coverage without raw trove exposure |
| Worker Shape | Claude implementation lane, Antigravity/Gemini receptionist-domain review, DeepSeek Flash adversarial privacy/schema review |
| In Scope | Synthetic H-derived profile/scenario fixtures or tests, existing Bernie scenario harness boundaries, review artifacts |
| Out Of Scope | Raw `local_data`/ignored JSON, semantic appointment labelling, live AI/provider calls, frontend Diary UI, production routes, database migrations |
| Verification | Scenario integrity/replay pytest, py_compile for touched Python, review artifacts, `git diff --check` |

### Workstream R26-A - Claude H-Series Scenario Implementation

| Item | Value |
|---|---|
| Owner | Claude |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-r26-h-series-neutral-scenario-implementation.md` |
| Goal | Add the smallest source-safe bridge from H-series neutral movement profiles into deterministic scenario coverage |
| In Scope | `tests/fixtures/bernie_scenarios/`, `tests/bernie_scenarios/`, focused scenario integrity/replay tests, narrow docs if needed |
| Out of Scope | Raw trove files, ignored local JSON, semantic labels, production code, frontend |
| Verification | `py_compile` touched Python; `pytest tests/test_bernie_scenario_integrity.py tests/bernie_scenarios -q`; `git diff --check` |
| Status | Superseded by Ariadne-local implementation after Claude plan accepted |

### Workstream R26-B - Gemini Receptionist Scenario Review

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-r26-h-series-receptionist-scenario-review.md` |
| Goal | Map H21 neutral movement findings to receptionist-domain deterministic scenario priorities |
| In Scope | `docs/receptionist_review_r26.md` only after plan approval |
| Out of Scope | Code/tests, raw trove files, semantic labelling, live providers |
| Verification | Tangible review artifact with scenario recommendations and acceptance criteria |
| Status | Superseded; submitted artifact rejected for H15 semantic-boundary overreach |

### Workstream R26-C - DeepSeek Neutral Bridge Adversarial Review

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via `deepseek-worker` |
| Branch | subagent fork / `codex-r26-deepseek-neutral-scenario-adversarial-review` packet |
| Task Packet | `orchestration/agent_inbox/codex/codex-r26-deepseek-neutral-scenario-adversarial-review.md` |
| Goal | Challenge privacy leakage, semantic overclaiming, fixture drift, and deterministic acceptance criteria |
| In Scope | `docs/adversarial/h_series_scenario_bridge_review_r26.md` or narrow non-overlapping tests |
| Out of Scope | Raw trove files, semantic labels, production code, frontend, live providers |
| Verification | Review artifact inspection; tests if added |
| Status | Integrated |

## Sprint R14: Auth Bootstrap Harness Guard

| Item | Value |
|---|---|
| Status | Dispatched |
| Product Goal | Prevent future invalid review-auth token drift from surfacing as vague Diary selector timeouts |
| Worker Shape | Claude availability checked first and unavailable until 9:30pm Australia/Brisbane; DeepSeek Flash implementation lane plus Antigravity/Gemini domain/test-design review |
| In Scope | `review/test_diary_smoke.py` auth bootstrap helper/assertion, focused/full smoke verification, document-only domain review |
| Out Of Scope | Production Diary assets, backend routes/schemas, assertion weakening, live Office/GitHub Pages/Gemini calls |
| Verification | Focused R13 auth-sensitive cluster, full `review/test_diary_smoke.py`, R12 reason-code guard, `git diff --check` |

### Workstream R14-A - DeepSeek Auth Bootstrap Guard

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r14-auth-bootstrap-guard` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r14-deepseek-auth-bootstrap-guard.md` |
| Goal | Add reusable harness auth helper/assertion so invalid-token drift fails clearly |
| In Scope | `review/test_diary_smoke.py` only unless Ariadne expands scope |
| Out of Scope | Production code, backend, broad smoke rewrites |
| Verification | Focused auth-sensitive cluster, full smoke, R12 reason-code guard |
| Status | Queued |

### Workstream R14-B - Gemini Auth Harness Domain Review

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-r14-auth-harness-domain-review.md` |
| Goal | Ensure harness auth guard improves signal without hiding real expired-session UX concerns |
| In Scope | `docs/receptionist_review_r14.md` only after plan approval |
| Out of Scope | Production code, test implementation, live providers |
| Verification | Tangible document-only review artifact |
| Status | Queued |

## Sprint R13: Diary Smoke Harness Recovery

| Item | Value |
|---|---|
| Status | Dispatched |
| Product Goal | Restore a clean deterministic Diary review signal after R12 exposed 12 unrelated Bernie session/pilot full-smoke failures |
| Worker Shape | Claude availability checked first and unavailable until 9:30pm Australia/Brisbane; two DeepSeek Flash lanes replace Claude/Codex worker capacity, plus Antigravity/Gemini domain review |
| In Scope | Diagnose failing Bernie session/pilot smoke checks, repair stale harness assumptions or narrow real regressions, preserve R12 reason-code coverage, document domain/UX risk classification |
| Out Of Scope | Backend schema/routes, broad Diary redesign, weakening tests, live Gemini/Office/GitHub Pages calls, unrelated production changes |
| Verification | Focused failing smoke tests, full `review/test_diary_smoke.py` where feasible, `node --check docs\diary\diary.js` if JS changes, `git diff --check` |

### Workstream R13-A - DeepSeek Smoke Failure Diagnosis

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r13-diary-smoke-diagnosis` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r13-deepseek-diary-smoke-diagnosis.md` |
| Goal | Classify each full-smoke failure and identify the smallest safe repair path |
| In Scope | Diagnosis artifact and focused source/test inspection |
| Out of Scope | Production fixes unless separately approved after plan gate |
| Verification | Reproduce/cite failing tests and inspect implicated selectors/session mocks |
| Status | Queued |

### Workstream R13-B - DeepSeek Focused Smoke Recovery

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r13-diary-smoke-focused-fix` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r13-deepseek-diary-smoke-focused-fix.md` |
| Goal | Implement the smallest deterministic harness/source fix once safe |
| In Scope | `review/test_diary_smoke.py` and, only if proven necessary, narrow `docs/diary/diary.js` repair |
| Out of Scope | Removing assertions, broad UI redesign, backend changes, R12 reason-code regression |
| Verification | Focused smoke failures, R12 reason-code smoke target, full Diary smoke where feasible |
| Status | Queued |

### Workstream R13-C - Gemini Domain Review

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-r13-diary-smoke-domain-review.md` |
| Goal | Ensure harness recovery does not hide real receptionist workflow regressions |
| In Scope | `docs/receptionist_review_r13.md` only after plan approval |
| Out of Scope | Production code, test implementation, live provider/Office/GitHub Pages |
| Verification | Tangible review artifact with acceptance checks |
| Status | Queued |

## Bernie Reception Scenario Workstream

The native Bernie/Diary programme now has a formal receptionist-domain testing
track in `orchestration/bernie_reception_scenario_workstream.md`.

Purpose:

- Convert Yuri's exploratory receptionist testing into executable project
  memory.
- Start thin: 8-12 backend/session scenarios, not a grand receptionist
  simulation.
- Use the corpus to regression-lock clarification, slot-search, roster,
  patient-advisory, and confirmation invariants as deterministic diary
  mechanisms evolve.

Recommended next slice when Bernie clarification/state work resumes:

- Sprint R1: Reception Scenario Corpus Foundation.
- Sprint R2: Clarification Merge Semantics.
- Sprint R3: Stale Session / Revision Hardening.

## Sprint R6: Temporal Boundary Harness Follow-Up

| Item | Value |
|---|---|
| Status | Dispatched |
| Product Goal | Make same-day and related Bernie temporal-boundary policies deterministic in tests without broad production changes |
| Worker Shape | Claude main implementation lane after availability probe, DeepSeek Flash adversarial review, Antigravity/Gemini domain-priority review, Ariadne orchestration/integration |
| In Scope | Minimal harness or focused pytest clock injection, same-day `window_fully_past`/clamp/past-date coverage, selected executable fixtures or route tests, temporal policy review artifacts |
| Out Of Scope | Diary UI redesign, Word/taskpane changes, GitHub Pages assets, live Gemini/Vertex calls, raw appointment mutation date-policy implementation, broad session-store redesign, GraphRAG/MCP/indexer automation |
| Verification | py_compile touched tests/harness files; `pytest tests/test_bernie_scenario_integrity.py tests/bernie_scenarios -q`; focused same-day/no-slot/slot-search tests; git diff --check |

### Workstream R6-A - Claude Temporal Harness Foundation

| Item | Value |
|---|---|
| Owner | Claude |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-sprint-r6-temporal-harness-foundation.md` |
| Goal | Add deterministic same-day/past-date temporal-boundary coverage with minimal harness or focused pytest support |
| In Scope | Tests/fixtures/harness only unless a real bug is exposed |
| Out of Scope | Production behavior changes without failing-test justification; UI; live provider calls |
| Verification | py_compile plus focused scenario/no-slot/slot-search pytest |
| Status | Queued |

### Workstream R6-B - DeepSeek Temporal Adversarial Review

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r6-temporal-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r6-temporal-adversarial-review.md` |
| Goal | Challenge clock-injection/replay design and classify remaining temporal scenarios |
| In Scope | Review artifact or non-overlapping narrow tests |
| Out of Scope | Production code; broad harness rewrite; UI |
| Verification | Artifact inspection or focused tests if added |
| Status | Queued |

### Workstream R6-C - Gemini Temporal Domain Review

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-r6-temporal-domain-review.md` |
| Goal | Rank temporal policies by clinical safety and define hard-block vs clarification semantics |
| In Scope | `docs/receptionist_review_r6.md`, acceptance notes, executable-readiness classification |
| Out of Scope | Production code; broad harness rewrite; UI; live provider calls |
| Verification | Tangible review artifact |
| Status | Queued |


### Workstream R6-D - DeepSeek Temporal Edge-Case Scout

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r6-temporal-edge-scout` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r6-temporal-edge-scout.md` |
| Goal | Scout compact temporal edge cases without overlapping Claude implementation |
| In Scope | Edge-case review artifact or small non-overlapping proposed tests |
| Out of Scope | Production code; broad harness rewrite; Claude-owned implementation files unless later directed |
| Verification | Artifact inspection or focused tests if added |
| Status | Queued |

## Sprint R5: Executable Scenario Promotion

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrors realigned, audit clean |
| Product Goal | Promote the best R3/R4 receptionist-domain corpus memory into executable Bernie replay coverage where the current harness can express it cleanly |
| Worker Shape | Two DeepSeek Flash lanes under the Claude-recuperation fallback rule, Antigravity/Gemini domain-priority review, Ariadne orchestration/integration |
| In Scope | Selected R3/R4 scenario fixtures, minimal scenario loader/replay support if needed, scenario integrity/replay tests, fixture classification notes |
| Out Of Scope | Diary UI redesign, Word/taskpane changes, GitHub Pages assets, live Gemini/Vertex calls, raw appointment mutation date-policy implementation, broad session-store redesign, GraphRAG/MCP/indexer automation |
| Verification | py_compile touched harness files; `pytest tests/test_bernie_scenario_integrity.py tests/bernie_scenarios -q`; focused adjacent Bernie tests if R4 executable coverage changes; git diff --check |

### Workstream R5-A - DeepSeek Executable Promotion

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r5-scenario-promotion` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r5-deepseek-executable-scenario-promotion.md` |
| Goal | Promote at least one high-value R3/R4 corpus scenario into passing executable replay coverage |
| In Scope | Scenario fixtures, minimal harness support, focused replay/integrity tests |
| Out of Scope | Production app code, UI, live provider calls, direct raw mutation policy |
| Verification | py_compile and focused scenario pytest |
| Status | Integrated |

### Workstream R5-B - DeepSeek Adversarial Review

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r5-scenario-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r5-deepseek-scenario-adversarial-review.md` |
| Goal | Independently classify which R3/R4 fixtures can be executable now and which should remain corpus memory |
| In Scope | Review artifact or narrow tests around fixture/harness boundaries |
| Out of Scope | Production app code, broad harness rewrite, UI |
| Verification | Scenario integrity/replay checks if files change, or explicit review artifact |
| Status | Integrated |

### Workstream R5-C - Gemini Domain Priority Review

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-r5-scenario-promotion-domain-review.md` |
| Goal | Rank R3/R4 fixtures by receptionist-domain value and executable-readiness |
| In Scope | Review packet or `docs/receptionist_review_r5.md`, fixture classification, acceptance notes |
| Out of Scope | Production code edits, broad harness rewrite, UI, live provider calls |
| Verification | Tangible review artifact with recommended executable-vs-memory classification |
| Status | Integrated |

## Sprint R4: Backdated/Past-Date Safety

| Item | Value |
|---|---|
| Status | Integrated, verification passed, closeout in progress |
| Product Goal | Prevent Bernie backdated or past absolute appointment dates from reaching safe executable slot-search/proposal states while preserving same-day past-window handling |
| Worker Shape | Two DeepSeek Flash lanes replacing Claude while Claude quota recuperates, Antigravity/Gemini domain-policy review, Ariadne orchestration/integration |
| In Scope | Bernie slot normalizer past-date semantics, interpret/supervised booking route behavior, focused tests, domain-policy review artifact |
| Out Of Scope | Diary UI redesign, Word/taskpane changes, GitHub Pages assets, live Gemini/Vertex calls, D8 patient collision cap/self-source work, broad session-store redesign, GraphRAG/MCP/indexer automation |
| Verification | py_compile; focused Bernie normalizer/interpret/supervised pytest; adjacent D8 collision tests; git diff --check; no browser/Pages checks unless frontend files change |

### Workstream R4-A - DeepSeek Implementation Lane

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r4-past-date-hardening` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r4-deepseek-past-date-hardening.md` |
| Goal | Harden Bernie slot normalization and proposal paths so absolute past dates block deterministically |
| In Scope | `app/services/bernie_slot_normalizer.py`, narrowly related `app/routers/appointments.py`, focused route/normalizer tests |
| Out of Scope | Diary UI, taskpane/Word, live provider calls, broad collision work |
| Verification | py_compile and focused pytest for touched Bernie normalizer/route tests |
| Status | Integrated |

### Workstream R4-B - DeepSeek Adversarial Review Lane

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r4-past-date-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r4-deepseek-adversarial-past-date-review.md` |
| Goal | Independently probe bypasses and add/propose regression evidence for past-date safety |
| In Scope | Bernie normalizer/supervised/interpret tests and review notes |
| Out of Scope | Broad production refactors, diary UI, duplicated implementation-lane edits unless critical |
| Verification | py_compile, focused pytest, git diff --check, or explicit review artifact |
| Status | Superseded by integrated R4 route-level regressions; branch retained as pre-fix adversarial evidence |

### Workstream R4-C - Gemini Domain Policy Review

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-r4-past-date-domain-policy-review.md` |
| Goal | Define receptionist-safe policy for absolute past dates, same-day fully-past windows, and stale reference-date cases |
| In Scope | Review packet, optional `docs/receptionist_review_r4.md`, acceptance criteria/test-design notes |
| Out of Scope | Production code edits, diary UI, live provider calls |
| Verification | Review packet with actionable acceptance criteria and risks |
| Status | Integrated |

## Sprint R3: Stale Session / Revision Hardening

| Item | Value |
|---|---|
| Status | Integrated, verification passed, closeout in progress |
| Product Goal | Prevent stale Bernie client revision/context coordinates from merging, confirming, or resurrecting outdated appointment intent |
| Worker Shape | Claude backend/session implementation lane (temporarily backed up by a second DeepSeek Flash lane while Claude quota recovers), Antigravity/Gemini receptionist-domain acceptance lane, DeepSeek Flash regression lane, Ariadne orchestration/integration |
| In Scope | Server-side stale revision/session append guards, focused regression tests, stale browser/two-receptionist/correction-vs-clarification acceptance cases, bounded scenario artifacts |
| Out Of Scope | Diary UI redesign, Word/taskpane changes, GitHub Pages assets, live Gemini/Vertex calls, broad patient collision source hardening, GraphRAG/MCP/indexer automation, persisted session table redesign |
| Verification | py_compile; focused Bernie clarification/session/interpret/scenario pytest; fixture integrity tests if scenario files change; git diff --check; no browser/Pages checks unless frontend files change |

### Workstream R3-A - Backend Stale Revision Guard

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-sprint-r3-stale-session-revision-hardening.md` |
| Goal | Implement fail-closed stale-session/revision handling for Bernie clarification/context append flows |
| In Scope | `app/routers/appointments.py`, Bernie/session helpers if needed, focused stale revision tests |
| Out of Scope | Diary UI, live provider calls, persisted session redesign, unrelated collision-source hardening |
| Verification | py_compile and focused pytest for touched Bernie/session/interpret surfaces |
| Status | Superseded by DeepSeek backup/no-code-needed review because Claude quota was unavailable |

### Workstream R3-D - DeepSeek Backend Backup Lane

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r3-deepseek-backend-hardening` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r3-deepseek-backend-hardening.md` |
| Goal | Cover Claude's backend implementation lane while Claude quota recovers, with minimal stale-session hardening or no-code-needed regression proof |
| In Scope | `app/services/bernie/session_store.py`, `app/routers/appointments.py` stale coordinate seams, focused backend tests |
| Out of Scope | Diary UI, taskpane/Word changes, live provider calls, Antigravity docs/fixtures, global model/config switching |
| Verification | py_compile, focused Bernie session/clarification/context/scenario pytest, git diff --check |
| Status | Integrated |

### R3 Tooling Note - Shen Identity

- The configured `deepseek-worker` agent uses `model_provider = "deepseek_bridge"` and `model = "deepseek-flash"` in `C:\Users\sarashera\.codex\agents\deepseek-worker.toml`.
- The 2026-07-05 spawned Shen session metadata records `agent_role = "deepseek-worker"`, `model_provider = "deepseek_bridge"`, and turn context `model = "deepseek-flash"`.
- If Shen self-reports as OpenAI, treat that as generic Codex base-instruction leakage; the runtime provider evidence is the session metadata and provider config, not self-description.

### Workstream R3-B - Gemini Domain Acceptance

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-r3-stale-session-domain-review.md` |
| Goal | Define receptionist-domain acceptance cases and dissent for stale browser tabs, two receptionists, corrections, clarifications, and intent switches |
| In Scope | Scenario corpus notes, R2 clarification semantics, acceptance/review artifact, optional bounded scenario fixture additions |
| Out of Scope | Production backend ownership, UI redesign, live provider calls, master/handoff updates |
| Verification | Plan packet first; fixture integrity tests if scenario artifacts change |
| Status | Integrated |

### Workstream R3-C - DeepSeek Regression Lane

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r3-deepseek-stale-session-regression` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r3-deepseek-stale-session-regression.md` |
| Goal | Independently add or review focused regression coverage for stale Bernie session revision/context handling |
| In Scope | Tests/review around stale revision coordinates, clarification merge, intent switches, and no stale appointment/audit mutation |
| Out of Scope | Primary production implementation, UI edits, live provider calls, global config or model switching |
| Verification | py_compile, focused pytest, git diff --check, or clear review artifact if bridge sandbox blocks git/Python |
| Status | Integrated |

## Sprint R2: Clarification Merge Semantics

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrors realigned, audit clean |
| Product Goal | Make Bernie clarification replies merge only missing or ambiguous fields into the existing request frame, preserving already resolved patient, practitioner, date, time, and intent |
| Worker Shape | Claude backend/session implementation lane, Antigravity/Gemini receptionist-domain acceptance lane, DeepSeek Flash regression lane, Ariadne orchestration/integration |
| In Scope | Backend/session clarification merge semantics, focused regression tests, selected R1 clarification xfail promotion, scenario/fixture acceptance notes, bounded Graphify symbol-map use during review |
| Out Of Scope | Diary visual redesign, broad UI copy rewrites, persisted session tables, GraphRAG, live provider calls, auto-mode, unrelated patient collision hardening, raw appointment mutation grammar changes |
| Verification | py_compile; focused Bernie interpreter/supervised booking/session replay/slot normalizer pytest; fixture integrity tests if scenario files change; git diff --check |

### Workstream R2-A - Backend Clarification Merge

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-sprint-r2-clarification-merge-semantics.md` |
| Goal | Implement clarification merge semantics so missing-field replies preserve known request-frame fields |
| In Scope | `app/routers/appointments.py`, `app/services/bernie*`, appointment schemas if needed, focused tests, selected executable scenario promotion |
| Out of Scope | Diary UI redesign, live provider calls, persisted session store, GraphRAG, unrelated collision/source hardening |
| Verification | py_compile and focused pytest for touched Bernie/session/normalizer/replay surfaces |
| Status | Integrated |

### Workstream R2-B - Gemini Acceptance Review

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-r2-clarification-acceptance-review.md` |
| Goal | Provide independent receptionist-domain acceptance criteria, fixture critique, and dissent for clarification merge semantics |
| In Scope | R1 corpus clarification scenarios, reception workstream notes, scenario/docs/test-design artifacts, acceptance checklist |
| Out of Scope | Production implementation, broad UI/copy rewrite, live provider prompt work, master/handoff updates |
| Verification | Plan packet first; after approval, fixture integrity tests if scenario artifacts change plus review checklist |
| Status | Integrated |

### Workstream R2-C - DeepSeek Regression Lane

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r2-deepseek-clarification-regression` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r2-deepseek-clarification-regression.md` |
| Goal | Add or review independent regression coverage for clarification merge invariants using the headless `deepseek_bridge` route |
| In Scope | Focused tests/review around slot normalization, interpreter/session routes, scenario replay fixtures, and fixture integrity |
| Out of Scope | Primary production implementation ownership, UI edits, live provider calls, GraphRAG, Codex GUI model switching, global config edits |
| Verification | py_compile, focused pytest for added/changed tests, git diff --check |
| Status | Integrated |

### R2 Integration Notes

- During R2 closeout, codify the agreed Graphify usage rule into durable protocol: use it autonomously for known-symbol impact/orientation only, refresh before use when code changed, and treat results as a map to source/tests rather than truth.
- Do not enable Graphify MCP, hooks, or post-commit auto-indexing as part of R2 unless Yuri explicitly expands the sprint.

## Sprint R1: Reception Scenario Corpus Foundation

| Item | Value |
|---|---|
| Status | Integrated locally; push/mirror/audit pending |
| Product Goal | Establish a small version-controlled Bernie receptionist scenario corpus and replay harness so exploratory receptionist findings become executable project memory |
| Worker Shape | Claude backend harness lane, Antigravity/Gemini receptionist-domain scenario lane, DeepSeek Flash fixture integrity lane, Ariadne orchestration/integration |
| In Scope | Scenario schema/loader, backend/session replay harness, 8-12 seed scenarios, fixture integrity checks, authoring guidance |
| Out Of Scope | Broad UI redesign, GraphRAG, production PHI/log ingestion, auto-mode, unconfirmed diary writes, fixing every known Bernie behaviour |
| Verification | Scenario fixture validation, focused pytest for replay/integrity harness, py_compile, git diff --check |

### Workstream R1-A - Backend Replay Harness

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-sprint-r1-bernie-scenario-replay-harness.md` |
| Goal | Build the pytest loader/replay harness for backend Bernie session scenarios |
| In Scope | `tests/bernie_scenarios/`, loader/helpers, focused tests needed to prove scenario replay mechanics |
| Out of Scope | Scenario corpus authorship beyond minimal fixtures needed to prove the harness, Diary frontend, production app changes except tiny seams required by the harness |
| Verification | py_compile and focused pytest for the new harness plus relevant existing Bernie session tests |
| Status | Integrated |

### Workstream R1-B - Reception Scenario Corpus

| Item | Value |
|---|---|
| Owner | Antigravity / Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-r1-reception-scenario-corpus.md` |
| Goal | Design and author the first receptionist-domain scenario corpus from the R1 seed list |
| In Scope | `tests/fixtures/bernie_scenarios/`, scenario content, scenario acceptance notes, domain/test-design dissent |
| Out of Scope | Backend harness implementation, Diary UI changes, production code, prompt rewrites, GraphRAG |
| Verification | Corpus files parse under the agreed schema once Claude/DeepSeek validation is available; otherwise provide a manual schema checklist in completion notes |
| Status | Integrated |

### Workstream R1-C - DeepSeek Fixture Integrity Lane

| Item | Value |
|---|---|
| Owner | DeepSeek Flash via Codex worker |
| Branch | `codex/sprint-r1-deepseek-scenario-integrity` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint-r1-deepseek-scenario-integrity.md` |
| Goal | Add cheap independent fixture/schema integrity coverage and consistency review without spending native Codex worker usage |
| In Scope | Scenario fixture README/checklist, parse/uniqueness/category validation tests, review notes for malformed or ambiguous scenario expectations |
| Out of Scope | Backend replay harness, production app code, Diary UI, broad implementation of clarification semantics |
| Verification | py_compile, focused integrity pytest, git diff --check |
| Status | Integrated |

## Operating Rules

- Every agent starts with `python scripts\agent_worktrees.py handin`.
  This now performs the full intake ritual: sync, infer agent, list inbox, and
  print protocol alerts plus the next task packet.
- Protocol changes must be written to `orchestration/protocol_alerts.md`.
  Worker agents should trust those alerts over remembered prior-session details.
- Parallel workers finish with `python scripts\agent_worktrees.py submit ...`.
  Packet submit commands include `--task`, which creates a Codex review packet
  in the worker branch.
- If `submit` fails, the worker must stop and report the exact command, working
  directory, branch, and error output. Do not manually push to `master` or
  `handoff/current` as a workaround.
- `codex/current` is the durable Codex mirror branch. It is not the same thing as
  a Codex-app subagent worktree. Codex subagents should use unique task branches
  such as `codex/time-model`, `codex/gemini-sdk-migration`, or
  `codex/<short-task-name>`.
- Codex-app subagent worktrees may live under `.codex/worktrees/...`; treat them
  as disposable worker checkouts. They must submit or be reviewed/integrated by
  the orchestrator before their work is considered part of the project.
- Ariadne/orchestrator Codex is distinct from Codex worker/subagents. Codex
  workers must use explicit task branches, never `master`; future Codex plan
  packets should mark `Role` as either `orchestrator` or `codex-worker`.
- Codex dispatches concrete task packets to `orchestration/agent_inbox/<agent>/`.
- Agents read their next packet with `python scripts\agent_worktrees.py brief --agent <agent>`.
- Non-trivial sprint work is plan-gated. After `handin`, workers create a Codex
  plan packet with `python scripts\agent_worktrees.py plan --agent <agent>
  --task <task> ...`, show the same plan in their GUI, then stop. Coding starts
  only after the user/Codex says `complete sprint task`.
- During the plan gate, workers may create, commit, and push implementation-plan
  packets and minimum coordination status changes to Codex's inbox. This is not
  approval to change production code. For Antigravity, artifact approval means
  "submit the plan packet only" unless the user explicitly says
  `complete sprint task`.
- Agents capture off-scope follow-up ideas with
  `python scripts\agent_worktrees.py suggest-task --agent <agent> --title "..."`
  so Codex can triage them from `orchestration/agent_inbox/codex/`.
  Suggested packets are not permission to implement the work.
- Codex polls durable worker submissions with
  `python scripts\agent_worktrees.py poll --fetch`.
- Use `python scripts\agent_worktrees.py poll --fetch --include-codex-workers`
  only when a current Codex subagent worker is expected to have submitted on a
  `codex/<task>` branch. The default fast poll skips historic remote
  `codex/*` disposable worker refs.
  The default path includes Claude/Antigravity branches, submit-alert branches,
  and local Codex inbox packets, excluding remote disposable `codex/*` branches
  and the durable `codex/current` mirror.
- Codex records every reviewed submit/integration in `orchestration/integration_log.md`
  via `python scripts\agent_worktrees.py record-integration ...`.
- After each integration, Codex runs `python scripts\agent_worktrees.py audit --fetch`
  and, when appropriate, `python scripts\agent_worktrees.py retire-stale` to expose
  disposable worker worktrees that should be removed or manually reviewed.
- `retire-stale` is dry-run by default. It removes only clean disposable worker
  worktrees when called with `--apply`; dirty worktrees are reported, never removed.
- Only Codex, acting as orchestrator, advances `master` and `handoff/current` in
  parallel mode unless the user explicitly instructs otherwise.
- Codex must announce `HANDIN READY` before the user prompts external workers to
  run `handin`.
- After `HANDIN READY`, Ariadne should use the cheapest available text channel
  first for external-worker `handin`, corrective nudge, and `complete sprint
  task` prompts. Claude uses `scripts\drive_agent_headless.py`; Antigravity uses
  its project-scoped CLI. Computer Use is a fallback for GUI-only situations, not
  the routine path.
- After all plan packets are accepted, Ariadne should release independent
  implementation workstreams in parallel unless worker channels are unproven,
  broken, security-sensitive, or likely to mutate overlapping files.
- During a sprint, Codex must not push sprint work through to `master` until all
  active sprint agents, including any Codex subagent worker, have submitted or
  been explicitly stood down.
- Worker count is risk-based, not ritualized: use the right number of agents for
  the risk and separable surfaces, not "always three agents". Ariadne may keep a
  narrow sprint single-track, use one specialist reviewer, or spawn extra agents
  when independent ownership boundaries make the extra coverage worth it.
- Prefer batching non-urgent orchestration protocol edits until discussion
  settles. Codex should remind the user before launch when agreed protocol edits
  are pending.
- Every workstream must state files in scope, files out of scope, verification, and
  merge criteria.
- Agents should record concerns or disagreement in the "Dissent / Risks" field.
- Prefer grouping tactical sprints under a coherent phase programme. Sprints
  should be sized by product outcome rather than file count: backend, frontend,
  tests, and docs can share a sprint when they serve one clear user-visible or
  operational outcome.

## Transparency Routine

Use a single evidence chain for every parallel task:

1. Dispatch packet in `orchestration/agent_inbox/<agent>/`.
2. Worker submit creates a Codex review packet.
3. Codex review marks packets `integrated`, `superseded`, or `blocked`.
4. Codex records the outcome in `orchestration/integration_log.md`.
5. Codex runs `audit --fetch` and reports:
   - submitted work waiting for review
   - integration-log delta since the last poll
   - branch/baton/mirror alignment
   - stale disposable worktrees and whether they are clean or dirty
6. Clean stale disposable worktrees may be retired with `retire-stale --apply`.
   Dirty stale worktrees require explicit review or user-approved abandonment.

When reporting progress to the user, Codex should use this shape:

- **Polled:** what submissions/review packets were found.
- **Integrated:** what was accepted, repaired, rejected, or superseded.
- **Verified:** checks run and failures/warnings.
- **Deployed:** for `docs/` changes, whether GitHub Pages serves the expected
  cache-bust/version. If stale, run `gh api --method POST
  repos/yurifrusin/EMR4/pages/builds` and re-check the live URL.
- **Aligned:** which refs were pushed/realigned.
- **Retirement:** stale disposable worktrees removed or left for review.
- **User Review:** all feasible Codex-side/tool-enabled checks already run, any
  hotfixes made from those checks, and only the residual user review/testing
  Ariadne could not confirm with available tools; use "none required" with the
  reason when no manual testing remains. If residual user checks remain, provide
  concrete steps: setup, exact UI path, expected result, suspicious/failure
  signs, skippable items, and what evidence to report back.
- **Next Direction:** Codex's recommendation for the next project slice and any
  project-level concerns raised by the integrated agent work.

After every fully integrated batch, Codex updates
`orchestration/sprint_closeout.md` with:

- what changed
- Codex-run reviews/tests, residual user review, and anything not required
- detailed step-by-step instructions for residual Yuri-only checks
- what is not required before moving on
- known follow-up
- recommended next direction

## Sprint D6: Patient Advisory Collision Semantics

| Item | Value |
|---|---|
| Status | Integrated and verified locally; push/mirror/audit pending |
| Product Goal | Stop Bernie's future-booking advisory from warning/blocking unless the existing booking collides with the requested day |
| Worker Shape | Claude consolidated regression suite, Antigravity/Gemini backend/domain-policy review, DeepSeek Flash scout/test branch, Ariadne integration cleanup |
| In Scope | Patient booking context warning semantics, interpret/supervised route regression tests, warning-shape assertion, coordination packet review |
| Out Of Scope | Production code changes, frontend copy changes, migrations, persisted sessions, GraphRAG, auto-mode, broad API review |
| Verification | py_compile; focused/adjacent pytest; worker packet review |

Integration notes:

- Broad patient context stays broad: `existing_future_follow_up` remains useful advisory context that a patient has some future booking.
- Staff-facing collision warning stays narrow: warning emission is regression-locked to requested-day matches via `has_existing_booking_on_requested_day`.
- Antigravity/Gemini acted as a domain-policy/test-design reviewer, not just a UX lane, and identified follow-up risks around capped context, self-collision, and frontend hardcoded copy.
- DeepSeek Flash was useful as a cheap scout, but its scattered test additions were consolidated into one D6 regression module for maintainability.

## Sprint G2: Human Diary Update Confirm Migration

| Item | Value |
|---|---|
| Status | Integrated and verified locally; push/mirror/audit pending |
| Product Goal | Move human Diary drag/drop/resize appointment updates onto the same signed update-confirm route used by Bernie extension confirms |
| Worker Shape | Claude backend/domain plan, Codex invariant plan, Antigravity lane superseded after no submitted artifact, Ariadne implementation |
| In Scope | `AppointmentUpdateProposalOut` confirm evidence fields, update proposal evidence minting, `handleMoveResize` confirm POST path, backend and deterministic Diary smoke tests |
| Out Of Scope | Edit-form Save migration, broad status/cancel/delete grammar, raw PUT endpoint removal, persisted PHI/session table, GraphRAG, taskpane/Command Centre, visual redesign |
| Verification | py_compile; node check; frontend version check; focused update/tool-intent/confirm suites; human drag/resize confirm smoke; full deterministic Diary smoke harness; diff check |

Integration notes:

- Safe ordinary update proposals now return `confirm_endpoint`,
  `confirm_payload`, update freshness id, and update-purpose signed evidence.
- Human drag/drop/resize keeps the existing proposal dialog, but after staff
  confirmation posts the signed confirm payload to
  `/appointments/proposals/update/confirm`.
- The old raw PUT update path remains as a bounded authenticated staff/API
  compatibility endpoint and as an old-backend fallback, but confirm-grade
  human drag/resize UI now uses backend-owned evidence when available.
- New backend and Diary smoke tests prove signed evidence is present, confirming
  writes once with bounded audit evidence, and the human drag/resize path does
  not emit raw PUT.
- Edit-form Save remains deliberately out of scope because it combines detail
  update and separate status PATCH semantics.

## Sprint G1: Unified Diary Update Confirm Grammar

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Product Goal | Move Bernie-authored appointment extensions from raw update PUT to a backend-owned signed update confirmation grammar |
| Worker Shape | Claude backend/domain plan, Antigravity Diary UX plan with scoped UI amendment, Codex invariant plan, Ariadne implementation |
| In Scope | `POST /appointments/proposals/update/confirm`, update-scoped signed evidence, Bernie tool-intent confirm payloads, Diary Confirm change network path, adversarial backend/UI tests |
| Out Of Scope | Broad diary action grammar for status/cancel/delete, persisted PHI/session table, GraphRAG, broad API rewrite, taskpane/Command Centre, human drag/drop migration off raw PUT |
| Verification | py_compile; node check; frontend version check; focused tool-intent/update/confirm suites; full deterministic Diary smoke harness; diff check |

Integration notes:

- Bernie tool-intent extension proposals now return a backend-owned
  `confirm_endpoint`, `confirm_payload`, update freshness id, and
  update-purpose signed confirmation evidence.
- `Confirm change` posts that payload to
  `/appointments/proposals/update/confirm` with explicit staff confirmation.
  It no longer calls raw `PUT /appointments/{id}`.
- The confirm endpoint binds evidence to the current appointment state plus the
  proposed command, revalidates the update against live state, writes once
  through the shared update helper, and records bounded audit evidence.
- Missing confirmation, wrong-purpose/tampered signed evidence, and stale
  current appointment state fail closed without mutating or writing audit rows.
- The raw staff PUT remains for backward compatibility this sprint; the next
  native action grammar sprint can migrate human drag/drop/resize onto the same
  confirm route.

## Sprint V2: Bernie Visible Tool-Intent UX

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Product Goal | Let the visible Diary Ask Bernie composer consume the V1 tool-intent route for appointment extension, showing friendly proposal states while preserving backend proposal evidence as the only source of confirmability |
| Worker Shape | Claude route/UI contract plan, Antigravity visible UX plan accepted with Ariadne authority-boundary amendment, Codex invariant plan captured after protocol stop, Ariadne implementation |
| In Scope | `docs/diary/diary.js` tool-intent routing/rendering/confirm guard, `docs/diary/diary.css` proposal card styling, `review/test_diary_smoke.py` route/confirm/stale-state coverage, asset cache-bust |
| Out Of Scope | Broad edit grammar, auto-mode/direct writes, persisted PHI/session tables, GraphRAG retrieval changes, taskpane/Command Centre, broad API rewrite |
| Verification | node check; py_compile; frontend version check; tool-intent/update/confirm backend suite; full deterministic Diary smoke harness; diff check |

Integration notes:

- Explicit `extend`/`lengthen` instructions now route to
  `/appointments/proposals/bernie/tool-intent`.
- Proposal rendering uses backend `BernieToolIntentOut.proposal.command` plus
  visible diary context; friendly text and staff text cannot create authority.
- `Confirm change` is rendered only for `proposal_ready` plus `proposal.safe`
  and sends the proposal command to the existing appointment update path.
- Clarification/blocked/unsupported tool-intent states show no confirm control
  and clear stale booking/no-slot UI.

## Sprint V1: Bernie Reception Voice And Tool-Intent Routing

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Product Goal | Give Bernie the first typed, non-booking diary tool-intent proposal route so requests such as extending an appointment become native diary proposals rather than ad hoc prompt text |
| Worker Shape | Claude backend lane superseded by session cap, Antigravity visible UX plan accepted for V2, Codex invariant plan accepted, Ariadne backend/frame implementation |
| In Scope | `BernieToolIntentIn/Out`, non-mutating `/appointments/proposals/bernie/tool-intent` route for appointment extension, visible diary appointment ids in Bernie context frames, focused backend and Diary review tests |
| Out Of Scope | Visible appointment-extension UI cards, auto-mode/direct writes, persisted PHI/session tables, GraphRAG retrieval changes, taskpane/Command Centre, broad API rewrite |
| Verification | py_compile; node check; frontend version check; new tool-intent tests; adjacent appointment update/confirm/context tests; full deterministic Diary smoke harness; diff check |

Integration notes:

- V1 supports explicit extension language only (`extend`/`lengthen`) and requires
  a target duration plus exactly one matching visible appointment context.
- Successful requests delegate to the existing deterministic
  `AppointmentUpdateProposalOut` contract. The Bernie route itself never writes
  appointment state and never returns confirmation-grade evidence.
- Unsupported, ambiguous, or incomplete requests fail closed as unsupported or
  clarification-required states with no proposal.
- The route carries source attribution for intent parsing, visible diary context,
  proposal authority, and staff-confirmed write authority.
- Diary `diary_day_booking` frames now include `appointment_id`, creating the
  native handle V2 can use for visible extend/edit proposal UX.

## Sprint K1b: Advisory Retrieval Wiring

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Product Goal | Wire typed practice-knowledge retrieval into Bernie as advisory-only reception context so Bernie can show useful practice references without gaining slot/search/confirm/write authority |
| Worker Shape | Claude backend lane superseded by session cap, Antigravity visible Diary UX plan accepted, Codex/Aristotle advisory-boundary plan accepted, Ariadne implementation/integration |
| In Scope | `app/routers/appointments.py` advisory retrieval hook, `app/services/practice_knowledge/retriever.py` weekday guard, `app/services/diary/policy.py` advisory-only predicate, Diary practice-reference rendering, focused route/policy/UI tests |
| Out Of Scope | Graph/vector store deployment, persisted PHI/session tables, auto-mode, taskpane/Command Centre, broad API rewrite, retrieval as slot/roster/policy/confirm/write truth |
| Verification | Practice-knowledge and advisory-boundary tests; focused Bernie route/policy/confirm wrapper suite; full deterministic Diary smoke harness; py_compile; node check; frontend version check; diff check |

Integration notes:

- Retrieved facts now enter Bernie only as `advisory_warning` frames with
  `basis="practice_knowledge_retrieval"` and advisory-only payload invariants.
- The Diary panel renders those facts as "Practice reference" cards with source
  provenance. They do not create candidate rows, no-slot rows, or confirm
  controls.
- Weekday-specific facts are guarded so a request for Saturday does not inherit
  a Friday-only roster fact because the practitioner name matches.
- Advisory warnings are no longer considered `advisory_warnings_only` when a
  stronger slot-search state with candidates exists.

## Sprint K1: Typed Practice Knowledge Substrate

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrored, and audited |
| Product Goal | Create a typed, provenance-bearing practice-knowledge substrate that can later support GraphRAG-style retrieval while keeping Bernie and the diary state machine advisory-only at the retrieval boundary |
| Worker Shape | Claude implementation, Antigravity advisory-UX plan accepted for a later wiring sprint, Codex/Laplace advisory-boundary review, Ariadne integration |
| In Scope | `app/services/practice_knowledge/`, deterministic in-memory retriever protocol seam, advisory-only result envelopes, one-way Bernie advisory-frame adapter, adversarial tests |
| Out Of Scope | Route/UI retrieval wiring, vector/graph store deployment, persisted sessions, PHI-bearing knowledge/session tables, slot availability authority from retrieval, confirm affordance decisions from retrieval, write payloads from retrieval |
| Verification | K1 practice-knowledge tests, adjacent diary/Bernie authority tests, compileall, static import scan, `git diff --check` |

Integration notes:

- Claude submitted a pure `practice_knowledge` package and tests; Ariadne
  reviewed and integrated it.
- Antigravity's UI boundary plan remains useful for a later K1b wiring sprint,
  but no frontend route/UI retrieval work was included in K1.
- The GraphRAG-facing seam is now the retriever protocol and typed envelope,
  not a deployed graph/vector store.
- Retrieval remains advisory-only: it may help Bernie explain or suggest, but
  must not set slot truth, roster truth, policy hard blocks, confirm authority,
  freshness/audit evidence, or write payloads.

## Sprint S1: Signed Confirmation Evidence

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, and audited |
| Product Goal | Harden Bernie/proposal confirmation evidence so confirmation-grade writes are backed by server-signed evidence and fail closed when evidence is missing, malformed, tampered, stale, or mismatched |
| Worker Shape | Ariadne backend implementation replacing the capped Claude lane, Antigravity Diary UI evidence-echo review plan, Codex worker adversarial invariant plan, Ariadne orchestration/review |
| Claude Task Packet | `orchestration/agent_inbox/claude/claude-sprint-s1-signed-confirm-evidence-contract.md` |
| Antigravity Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-s1-confirm-evidence-ui-review.md` |
| Codex Task Packet | `orchestration/agent_inbox/codex/codex-sprint-s1-signed-evidence-invariants.md` |
| In Scope | HMAC/signed candidate/proposal evidence design, confirm evidence echo, stale/tamper/replay/mismatch tests, legacy compatibility strategy, confirm-affordance authority boundaries |
| Out Of Scope | Persisted session table, GraphRAG/practice-knowledge route/UI wiring, auto-mode, broad raw write-path/API-spine redesign, UI redesign, live PHI |
| Verification | Plan packets first; later implementation must run focused evidence/confirm/proposal tests, relevant Diary smoke fixtures if UI changes, compileall/node checks as applicable, and `git diff --check` |

Integration notes:

- Claude hit its five-hour session cap before producing an implementation plan,
  so Ariadne replaced the backend/domain lane and marked the Claude packet
  superseded.
- Antigravity's plan confirmed the Diary UI should only echo backend-supplied
  evidence; Ariadne verified `enrichBernieConfirmPayload()` already preserves
  signed confirm-payload fields, so no frontend code or asset bump was needed.
- The backend now mints and verifies versioned HMAC confirmation evidence for
  Bernie supervised booking confirms, while legacy unsigned compatibility is
  explicit and auditable.
- Focused signed-evidence tests, adjacent Bernie/diary confirm tests,
  py-compile, and `git diff --check` passed.

## Sprint N4: Bernie Server-Side Session/Event Foundation

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, and audited |
| Product Goal | Define the minimum server-owned Bernie session/event persistence foundation so conversation memory, stale-state rejection, signed confirmation evidence, and render-from-state UI can converge without premature PHI-heavy storage |
| Worker Shape | Claude backend/session contract plan, Antigravity Diary session UX/render-from-state plan, Codex worker adversarial invariant plan, Ariadne orchestration/review |
| Claude Task Packet | `orchestration/agent_inbox/claude/claude-sprint-n4-bernie-server-session-contract.md` |
| Antigravity Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-n4-diary-session-ux-review.md` |
| Codex Task Packet | `orchestration/agent_inbox/codex/codex-sprint-n4-session-invariants.md` |
| In Scope | Plan first; build on `app/services/bernie/session.py`; retention/privacy posture, optimistic concurrency/stale event controls, one session per staff per diary surface, signed evidence/session binding, render-from-state tail, focused tests |
| Out Of Scope | Production code before plan approval, broad API-spine rewrite, GraphRAG route/UI wiring, auto-mode, live PHI, full transcript persistence unless justified, UI redesign |
| Verification | Plan packets first; later implementation must run focused Bernie session/evidence tests, migration checks if tables are added, relevant Diary harness checks if UI changes, py-compile/node checks as applicable, and `git diff --check` |

Integration notes:

- Claude remained capped by the five-hour session limit, so Ariadne superseded
  the backend lane and implemented the accepted backend/session plan.
- Antigravity submitted a render-from-state Diary tail plan. Ariadne accepted it
  as future UI guidance but deferred implementation until a backend session
  endpoint exists.
- Codex/McClintock submitted the adversarial session invariant plan; Ariadne
  implemented the backend foundation and tests from that plan.
- N4 adds executable server-owned append/concurrency/idempotency semantics via
  an in-memory store, without adding a PHI-bearing table, route endpoint, UI
  migration, or frontend asset change.
- Focused Bernie session/evidence tests, adjacent evidence/confirm boundary
  tests, py-compile, and `git diff --check` passed.

## Sprint N5: Bernie Session Endpoint And Diary Render Tail

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, and audited |
| Product Goal | Expose the N4 server-owned Bernie session semantics through a minimal authenticated endpoint and let the Diary panel begin rendering/refetching server session state without making browser state authoritative |
| Worker Shape | Claude backend session endpoint plan, Antigravity Diary render/refetch plan, Codex worker endpoint/UI invariant plan, Ariadne orchestration/review |
| Claude Task Packet | `orchestration/agent_inbox/claude/claude-sprint-n5-bernie-session-endpoint-contract.md` |
| Antigravity Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-n5-diary-session-render-tail.md` |
| Codex Task Packet | `orchestration/agent_inbox/codex/codex-sprint-n5-session-endpoint-invariants.md` |
| In Scope | Plan first; active-session/new-session/event append/refetch contract, revision conflict responses, stale/refetch UI, latest-message/history rendering from server state, no browser PHI storage, focused route/UI tests |
| Out Of Scope | Production code before plan approval, PHI-bearing DB table/migration unless explicitly reapproved, GraphRAG route/UI wiring, auto-mode, broad API-spine rewrite, taskpane/Command Centre changes |
| Verification | Plan packets first; later implementation must run backend session route tests, focused Diary smoke checks if UI changes, node/py-compile checks, frontend asset version checks if deployable assets change, and `git diff --check` |

Integration notes:

- Claude remained capped by the five-hour session limit, so Ariadne superseded
  the backend lane and implemented the minimal backend endpoint contract.
- Antigravity submitted a Diary render/refetch plan; Ariadne accepted it as the
  frontend follow-up but deferred runtime asset changes until after the route
  contract landed.
- Codex/Peirce submitted the endpoint/UI invariant plan; Ariadne implemented
  backend route tests covering its route-layer invariants.
- N5 adds process-local, authenticated Bernie session routes for active session,
  new session, and append typed event with revision/idempotency conflict
  handling. It does not add a persisted PHI-bearing table.
- Focused backend route/session tests, adjacent signed-confirm/proposal tests,
  py-compile, and `git diff --check` passed.

## Sprint N6: Diary Render From Bernie Session Endpoint

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, deployed, mirrored, and audited |
| Product Goal | Make the Diary Bernie panel consume the N5 server-owned session endpoint for active-session load, new-session/refetch, stale conflict handling, and PHI-minimised event appends while keeping the browser presentational |
| Worker Shape | Claude backend/API contract review if quota allows, Antigravity Diary UI render/refetch plan, Codex worker UI invariant/review-harness plan, Ariadne orchestration/integration |
| Claude Task Packet | `orchestration/agent_inbox/claude/claude-sprint-n6-bernie-session-ui-contract-review.md` |
| Antigravity Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-n6-diary-render-server-session.md` |
| Codex Task Packet | `orchestration/agent_inbox/codex/codex-sprint-n6-diary-session-ui-invariants.md` |
| In Scope | Plan first; `docs/diary/diary.js`, `diary.html/css` only if needed, focused review smoke checks, active-session load, new-session/refetch, append requests with expected revision/idempotency, stale conflict UX, no browser PHI/session authority |
| Out Of Scope | Production code before plan approval, backend route/schema changes unless the plan proves a tiny additive adjustment is required, database migration, GraphRAG/practice-knowledge wiring, auto-mode, taskpane/Command Centre changes, broad UI redesign |
| Verification | Plan packets first; later implementation must run `node --check`, focused route-intercepted Diary review checks, backend session route regressions if touched, no local/session storage PHI assertions, frontend version checks if deployable assets change, and `git diff --check` |

Integration notes:

- Claude remained capped by the five-hour window, so Ariadne superseded that
  lane after recording the reason.
- Antigravity submitted a server-session render/refetch UI plan. Ariadne
  accepted the session/refetch/stale-conflict direction but amended the
  transcript-rendering approach: N6 keeps the existing client-presentational
  Bernie flow while appending PHI-minimised server-session events, because the
  current endpoint intentionally rejects raw transcript/PHI payloads.
- Codex/Lorentz submitted a UI invariant plan. Ariadne integrated the route-
  intercepted smoke checks for active session load, PHI-minimised event append,
  stale conflict confirmation blocking, and no browser PHI/session persistence.
- N6 connects the deployed Diary Bernie panel to the N5 server session substrate,
  adds stale-session guardrails, and bumps Diary assets to `diary.js?v=154` and
  `diary.css?v=129`.
- No backend route/schema change, database migration, GraphRAG wiring, auto-mode,
  taskpane, Command Centre, or broad UI redesign was included.

## Sprint N7: Bernie Server Outcome Events And Confirmation Binding

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, and audited |
| Product Goal | Make Bernie interpreter/proposal/candidate/confirmation outcomes first-class server-session events so N6's session bridge starts converging toward server-owned conversation state without raw transcript persistence |
| Worker Shape | Claude backend/session contract plan if quota allows, Antigravity Diary outcome-render/state UX plan, Codex worker adversarial invariant plan, Ariadne orchestration/integration |
| Claude Task Packet | `orchestration/agent_inbox/claude/claude-sprint-n7-bernie-session-outcome-contract.md` |
| Antigravity Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-n7-diary-session-outcome-ui-review.md` |
| Codex Task Packet | `orchestration/agent_inbox/codex/codex-sprint-n7-session-outcome-invariants.md` |
| In Scope | Plan first; server-owned outcome event model for interpreter/proposal/candidate/confirm milestones, PHI-minimised references, expected revision/idempotency, stale-session rejection, signed confirmation evidence/session binding, focused route/store/Diary review checks |
| Out Of Scope | Production code before plan approval, persisted DB table/migration, raw transcript/PHI event storage, GraphRAG/practice-knowledge wiring, auto-mode, broad API-spine rewrite, taskpane/Command Centre changes |
| Verification | Plan packets first; later implementation must run focused backend session/evidence/confirm tests, Diary route-intercepted smoke checks if UI changes, node/py checks, frontend version checks if deployable assets change, and `git diff --check` |

Integration notes:

- Claude remained capped by the five-hour session window, so Ariadne superseded
  that lane after recording the 429 reset.
- Antigravity was prompted twice through the project-scoped CLI but produced no
  stdout, source-packet notes, plan packet, or worktree changes. Ariadne stood
  the lane down because N7 did not require Diary asset changes.
- Codex worker Boole produced a useful invariant plan but hit the Windows Store
  `python` alias before it could submit. Ariadne recovered the plan into an
  official Codex plan packet and implemented the accepted backend/session slice.
- N7 adds server-owned outcome event types and process-local outcome append
  semantics for interpreter/context/slot/proposal/confirmation milestones,
  with revision/idempotency/PHI-key guardrails.
- N7 also adds optional signed confirmation `session_binding`: existing signed
  confirmation payloads remain compatible, but when a binding is supplied it is
  included in the HMAC payload and validated fail-closed against the current
  server-owned session coordinates before any write.
- No persisted session table, migration, GraphRAG wiring, auto-mode, Diary asset
  change, taskpane, Command Centre, or broad API rewrite was included.

## Sprint N8: Route-Level Outcome Event Wiring

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, and audited |
| Product Goal | Wire real Bernie interpretation, supervised-booking, proposal, and confirmation route outcomes into the server-owned session outcome event substrate without changing visible Diary behaviour |
| Worker Shape | Claude lane superseded by quota cap, Antigravity lane superseded after no-artifact CLI result, Codex/Sartre invariant plan accepted, Ariadne implementation and verification |
| Claude Task Packet | `orchestration/agent_inbox/claude/claude-sprint-n8-bernie-route-outcome-contract.md` |
| Antigravity Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint-n8-diary-session-outcome-ui-review.md` |
| Codex Task Packet | `orchestration/agent_inbox/codex/codex-sprint-n8-route-outcome-invariants.md` |
| In Scope | Optional server-session route coordinates, compact interpretation/context/slot/proposal/confirmation outcome appends, server-stamped session binding in signed confirm evidence, focused backend route/session tests |
| Out Of Scope | Persisted session table/migration, Diary UI wiring for `server_session_*`, GraphRAG/practice-knowledge routing, auto-mode, taskpane/Command Centre changes, broad API-spine rewrite |
| Verification | Focused N8 route outcome tests; adjacent Bernie session/store/evidence/confirm/wrapper tests; py_compile; node --check for unchanged Diary JS; frontend asset version check; git diff --check |

Integration notes:

- Claude headless plan attempt returned 429 session-limit reset, so Ariadne
  superseded that lane.
- Antigravity CLI returned blank stdout and the clean antigravity/current
  worktree contained no plan packet or artifact, so Ariadne superseded that
  lane.
- Codex worker Sartre supplied the accepted invariant plan. Ariadne implemented
  the bounded backend route wiring directly.
- N8 keeps all route-session fields optional and backward-compatible. The live
  Diary does not yet send `server_session_*` route coordinates; a later Diary
  sprint should do that wiring.
- No Diary asset, UI redesign, persisted PHI-bearing session table, GraphRAG
  route/UI integration, auto-confirm, or broad appointment API refactor landed.

## Sprint 106: Bernie Reception-Domain Copilot Architecture Consult

| Item | Value |
|---|---|
| Status | Consulting plan integrated; first execution slice queued as Sprint 106A |
| Product Goal | Bring Claude Fable 5 in as a consulting reviewer for Bernie's reception-domain copilot architecture before further implementation |
| Worker Shape | Claude/Fable 5 plan-only review, overseen by Ariadne; no Antigravity or Codex worker branch for this sprint |
| Task Packet | `orchestration/agent_inbox/claude/claude-bernie-reception-domain-copilot-architecture-consult.md` |
| Model Policy | Planning should use Claude CLI `--model claude-fable-5` with high effort if available; fall back only with explicit Ariadne/Yuri awareness |
| Pause Gate | Completed: Yuri approved executing the first bounded extraction slice after Ariadne review |
| In Scope | Current Bernie interpreter, patient booking context, slot search, roster/schedule diagnostics, diary UI state machine, chat turns, transition/render guards, tests, and the proposed domain-specific receptionist-agent architecture |
| Out Of Scope | Production code edits during planning, autonomous booking, live PHI, broad API-spine rewrite, provider migration, and any direct booking mutation without staff confirmation |

## Sprint 106A: Bernie Bounded Domain Extraction Foundation

| Item | Value |
|---|---|
| Status | Queued for Claude/Fable implementation |
| Product Goal | Start standing Bernie on the long-run reception-domain foundation without prematurely adding the persisted session table |
| Worker Shape | Claude/Fable 5 implementation slice, Ariadne review/integration |
| Task Packet | `orchestration/agent_inbox/claude/claude-bernie-bounded-domain-extraction-foundation.md` |
| In Scope | `app/services/bernie/` bounded package, low-risk wrappers/extraction, persistence-shaped session/event contracts, capability registry skeleton, focused backend tests |
| Out Of Scope | Persisted session DB table, migrations, frontend render-from-server-state migration, typed context-frame enforcement, API-breaking response changes, autonomous booking, broad router rewrite |
| Verification | Focused Bernie backend suites and `git diff --check`; stop if extraction pressure expands beyond the packet |

## Sprint 105: Bernie Typed Turn Contract And Confirmation Evidence

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, deployed, mirrored, audited, and closed |
| Product Goal | Promote Bernie chat/session metadata into typed backend-visible turns and confirmation evidence so no-slot suggestions, candidate selection, proposal preview, and confirmation are explicit events with stale-proposal protection |
| Worker Shape | Claude backend/API turn contract plan, Antigravity/Gemini Diary typed-turn UI plan, and Codex worker invariant/review-harness plan |
| Out Of Scope | Broad root-to-branch API redesign, statechart runtime dependency, limited Bernie auto-mode, voice/headset/wake-word work, Caller ID, Medicare/HI/PVM/OPV verification, and any agent-only write path |

Integrated workstreams:

- Claude: `orchestration/agent_inbox/claude/claude-sprint105-bernie-turn-contract.md`
  for backend/API typed turn schemas, event vocabulary, candidate/proposal
  freshness ids or hashes, and confirmation staleness checks.
- Antigravity/Gemini: `orchestration/agent_inbox/antigravity/antigravity-sprint105-bernie-typed-turn-ui.md`
  for Diary typed staff/Bernie turn events, typed no-slot suggestion clicks,
  candidate/proposal evidence wiring, and stale composer/proposal cleanup.
- Codex worker: `orchestration/agent_inbox/codex/codex-sprint105-bernie-turn-invariants.md`
  plan accepted as review guidance; implementation was stood down because
  Claude/Antigravity plus Ariadne integration repairs covered the invariant
  harness surfaces without needing a third overlapping production patch.

Integration notes:

- Claude backend/API work was accepted with additive optional typed turn refs,
  deterministic candidate/proposal freshness ids, and a fail-closed confirmation
  staleness gate when clients echo evidence.
- Antigravity Diary UI work was accepted after Ariadne repaired interrupted CLI
  output and added the end-to-end bridge so the UI echoes backend `turn_ref`,
  `candidate_freshness_id`, and `proposal_freshness_id` at confirmation.
- Focused backend tests and the full deterministic diary smoke harness passed.
- Sprint 105 continues the concrete agentic Diary/API-pattern programme before
  the broad root-to-branch API-spine review.

## Sprint 104: Bernie Conversational State Memory

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, deployed, mirrored, audited, and closed |
| Product Goal | Turn *bernie* from a single-prompt panel into an explicit conversational workflow with state machine memory, fresh clarification turns, no-slot suggestions, stale-state rules, and patient-specific booking context |
| Worker Shape | Plan-gated Claude backend/API workstream, Antigravity/Gemini Diary UI workstream, and Codex worker invariant/review-harness workstream |
| Out Of Scope | Broad root-to-branch API rewrite, XState dependency, voice/headset integration, Medicare/HI/PVM/OPV implementation, Caller ID integration, and limited auto-mode implementation |

Integrated workstreams:

- Claude: `orchestration/agent_inbox/claude/claude-sprint104-bernie-patient-context-contract.md`
  for backend/API `patient_booking_context`, no-slot suggestion contract,
  state-memory fields, and focused tests.
- Antigravity/Gemini: `orchestration/agent_inbox/antigravity/antigravity-sprint104-bernie-chat-state-ui.md`
  for Diary chat/clarification UI, stale-state transitions for
  Today/Prev/Next/date picker/Refresh, compact/no-slot copy, and auto-preview
  toggle boundary.
- Codex worker: `orchestration/agent_inbox/codex/codex-sprint104-bernie-state-invariants.md`
  for transition-table/statechart invariants, fixture design from Yuri's live
  tests, and acceptance harness planning.

Integration notes:

- Claude backend/API work was accepted with Ariadne test repairs for current
  clarification copy and deterministic no-slot fixture time.
- Antigravity Diary UI work was accepted after Ariadne repaired interrupted CLI
  output, restored compatibility with legacy auto-preview state, and verified
  the full diary smoke harness.
- Codex worker invariant-harness work was integrated as executable Sprint 104
  acceptance evidence.
- Remaining design follow-up: make UI `session_id`/turn metadata an explicit
  backend-owned input contract and use typed no-slot suggestion payloads end to
  end in the next sprint.

## Sprint 100: Bernie Booking Session State Machine

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, deployed, mirrored, and audited |
| Launch Gate | Complete: design guide, dispatch packets, worker plan review, and implementation release completed |
| Integration Gate | Complete locally: worker commits cherry-picked, Ariadne repaired harness expectations, and focused verification passed |
| Product Goal | Replace the current loosely coupled *bernie* booking flow with an explicit session state machine so relative dates, diary navigation, candidate selection, clarification, preview, and confirmation remain logically separated |
| Design Guide | `orchestration/event_driven_statechart_architecture.md` |

### Workstream GA - Bernie Backend Session And Temporal Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-sprint100-bernie-backend-state-contract.md` |
| Goal | Plan backend/API changes for immutable request reference dates, clinic-day exhaustion handling, session/candidate evidence, and no-reinterpretation confirmation contracts |
| In Scope | Plan packet first only; `app/schemas/appointments.py`, `app/routers/appointments.py`, `app/services/bernie_booking_interpreter.py`, `app/services/bernie_slot_normalizer.py`, and focused backend tests; same-day after-hours behaviour; immutable `request_reference_date`; candidate snapshot/evidence fields; no-write invariants |
| Out of Scope | Production code before plan approval, diary UI implementation, broad GraphQL/API-spine redesign, phone/Caller ID/OPV/PVM/Medicare integrations, live voice, and weakening staff confirmation |
| Verification | Plan must specify tests for after-hours same-day requests, partly-past in-hours clamping, relative tomorrow immutability, selected-candidate confirmation using absolute slot fields, no mutation before confirm, and no live-provider dependency |
| Status | Integrated |

### Workstream GB - Bernie Diary State Machine UI

| Item | Value |
|---|---|
| Owner | Antigravity/Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint100-bernie-ui-state-machine.md` |
| Goal | Plan a diary-side *bernie* session state machine that keeps instruction, interpretation, candidate snapshot, selected slot, diary preview, choose-another-time, and confirmed states separate |
| In Scope | Plan packet first only; `docs/diary/diary.js`, `docs/diary/diary.css`, `docs/diary/diary.html`, and `review/test_diary_smoke.py`; explicit UI state object; immutable session reference date; candidate snapshot reuse; post-confirm panel cleanup; compact Details behaviour; auto-preview toggle boundary |
| Out of Scope | Production code before plan approval, backend schema implementation except requested contract fields, broad diary redesign, phone/voice integrations, and bypassing staff confirmation |
| Verification | Plan must specify deterministic UI tests for `today after 3` after clinic hours, `tomorrow` candidate selection without jumping two days, `Choose another time` returning to the same candidate snapshot, confirm success cleanup, stale confirm recovery, and asset version checks |
| Status | Integrated |

### Workstream GC - Bernie State Invariant Review Harness

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/sprint100-bernie-state-invariants` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint100-bernie-state-invariants.md` |
| Goal | Independently plan the acceptance/invariant harness for the *bernie* state machine, using Yuri's live screenshots as failure fixtures |
| In Scope | Read-only plan/review packet first only; inspect current *bernie* backend/UI/tests and propose model-based or transition-table tests; define invariants for reference-date immutability, candidate snapshot reuse, UI state cleanup, confirmation gating, and after-hours temporal logic |
| Out of Scope | Production code edits before plan approval, integration, live provider/browser manual testing, and broad API-spine implementation beyond noting reusable modelling lessons |
| Verification | Plan must include concrete acceptance gates, transition table, failure fixtures, required backend/UI test names, and resubmission criteria for the worker plans |
| Status | Integrated |

## Sprint 99: Bernie Confidence And Response Policy

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, deployed, mirrored, and audited |
| Launch Gate | Complete: dispatch committed, pushed, audited, and HANDIN READY announced |
| Integration Gate | Complete: worker plans reviewed, implementation submitted, Ariadne repaired cross-branch issues, and focused verification passed |
| Product Goal | Give *bernie* a typed confidence and response policy so it assumes only when confidence is adequate, asks human-like clarification when uncertainty is meaningful, blocks only when confidence/safety gates require it, and exposes technical details on demand rather than in ordinary receptionist copy |

### Workstream FA - Bernie Confidence Policy Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-sprint99-bernie-confidence-policy-contract.md` |
| Goal | Plan backend/API confidence axes, decision bands, assumptions, staff checks, and non-mutating release gates for *bernie* booking interpretation |
| In Scope | Plan packet first only; `app/schemas/appointments.py`, `app/routers/appointments.py`, `app/services/bernie_booking_interpreter.py`, focused *bernie* tests, and release-gate docs; separate intent, temporal, practitioner, patient-identity, slot-validity, and future speech/transcription confidence axes; omitted-date inference; practitioner typo matching; large-database patient ambiguity handling |
| Out of Scope | Production code before plan approval, diary UI implementation, live phone/voice/Caller ID/Medicare/OPV/PVM integrations, broad GraphQL/API-spine redesign, weakening staff confirmation, and unrelated refactors |
| Verification | Plan must specify exact backend files/tests, confidence thresholds/gates, no-write assertions, ordinary prompt release gates, omitted-date test, practitioner typo test, patient ambiguity/duplicate test, and migration/no-migration rationale |
| Status | Integrated |

### Workstream FB - Bernie First-Person Confidence UI

| Item | Value |
|---|---|
| Owner | Antigravity/Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-sprint99-bernie-first-person-confidence-ui.md` |
| Goal | Plan the receptionist-facing response layer for first-person *bernie* copy, compact evidence, Details disclosure, inferred-date messages, and candidate/preview states |
| In Scope | Plan packet first only; `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`, and `review/test_diary_smoke.py`; copy such as `I've assumed...` and `Do you mean...`; high-confidence compact state; low-confidence expanded evidence; most-likely diary preview when allowed; future voice/chat parity |
| Out of Scope | Production code before plan approval, backend schema implementation except requested contract fields, live voice/headset work, phone-system/Caller ID/Medicare integrations, broad diary redesign, removing staff confirmation, and raw debug details in ordinary mode |
| Verification | Plan must specify exact diary files/tests, route-intercepted smoke cases for inferred today, typo-resolved practitioner, ambiguous patient candidates, Details toggle, no raw snake_case in ordinary mode, no write before confirm, asset version checks, and deployed/local review strategy |
| Status | Integrated |

### Workstream FC - Confidence Acceptance Review

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/sprint99-confidence-acceptance-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-sprint99-confidence-acceptance-review.md` |
| Goal | Independently review the current *bernie* confidence problem and submit acceptance criteria, edge cases, and API/UI risk notes for Ariadne before implementation release |
| In Scope | Read-only plan/review packet first only; current *bernie* backend, diary UI, smoke harness, release gates, and latest closeout; focus on confidence axes, fuzzy matching, omitted-date inference, first-person copy, Details disclosure, and release-gate coverage |
| Out of Scope | Production code edits, integration, live provider/browser testing, and broad API-spine design beyond capturing follow-up boundaries |
| Verification | Review packet must include concrete acceptance gates, hidden risks, recommended tests, Sprint 99 versus deferred boundaries, and resubmission criteria for worker plans |
| Status | Integrated |

## Sprint 96: Bernie Reception Assistant UX And API Evidence Contract

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, deployed, mirrored, and audited |
| Launch Gate | Complete: dispatch committed, pushed, audited, and HANDIN READY announced |
| Integration Gate | Complete |
| Product Goal | Turn Bernie from a scary supervised-review prototype into a calm reception assistant backed by rigorous non-mutating proposal APIs, explicit staff confirmation, and auditability |

### Workstream EA - Bernie API Evidence Contract Plan

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-bernie-api-evidence-contract-plan.md` |
| Goal | Plan the backend/API adjustments needed for receptionist-grade Bernie booking proposals, auditability, and future context-frame placeholders |
| In Scope | Plan packet first only; review `app/schemas/appointments.py`, `app/routers/appointments.py`, `app/models/appointments.py`, `app/models/ai_audit.py`, existing Bernie/appointment/audit tests; propose any minimal schema/router/test changes needed so Bernie returns structured slot, patient, identity, practitioner, confirmation, keyboard/action, and audit evidence while confirmed writes remain the only appointment mutations; identify whether existing `AppointmentAuditLog` and Access AI audit are sufficient or what focused audit event is missing; keep Caller ID, OPV/PVM, and phone-system integrations as optional empty context-frame/provider placeholders only |
| Out of Scope | Production code edits before plan approval, diary frontend implementation, live Caller ID/phone-system integration, live Medicare/OPV/PVM/IHI calls, GCP/provider/auth changes, clinical/taskpane/Command Centre work, broad implementation-plan rewrite, and broad security/dependency work |
| Verification | Plan packet must name exact backend files/tests to touch, no-write/no-mutation assertions, audit assertions, focused pytest targets, and migration/no-migration rationale |
| Status | Integrated |

### Workstream EB - Bernie Reception UX Plan

| Item | Value |
|---|---|
| Owner | Antigravity/Gemini |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-bernie-reception-ux-plan.md` |
| Goal | Plan a calmer, practice-usable diary experience for Bernie-assisted booking without weakening confirmation gates |
| In Scope | Plan packet first only; review `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`, and `review/test_diary_smoke.py`; propose staff-facing copy/visual hierarchy replacing "Supervised Booking Review", robot/masked iconography, red/blocked theatre, and `BERNIE PROVISIONAL BOOKING`; include candidate-slot click-through, visible provisional slot focus, patient details and identity evidence where available, clear Confirm button and keyboard shortcut, calm warning language, and deterministic smoke checks |
| Out of Scope | Production code edits before plan approval, backend/schema changes except documented requested contracts, live phone/Medicare/provider integrations, broad diary redesign, taskpane/Command Centre/billing/SMS/resource-admin work, and any bypass of staff confirmation |
| Verification | Plan packet must name exact diary files/tests to touch, copy/UX acceptance criteria, keyboard path checks, confirmation-gate checks, asset cache-bust/version checks, and deployed/local smoke strategy |
| Status | Superseded |

### Workstream ED - Replacement Bernie Reception UX Plan

| Item | Value |
|---|---|
| Owner | Codex UX worker with Ariadne review |
| Branch | Direct subagent plan; implementation branch TBD |
| Task Packet | Replacement for rejected `antigravity-bernie-reception-ux-plan` |
| Goal | Produce an implementation-ready UX plan that makes Bernie feel like a calm reception assistant while preserving staff-confirmed API guardrails |
| In Scope | Plan only; `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`, and `review/test_diary_smoke.py`; replacement copy, panel/card hierarchy, candidate selection, provisional diary card information density, visible Confirm action, keyboard shortcut, route-intercepted no-write checks, and a restrained provisional-card pulse approved by Yuri |
| Out of Scope | Backend schema, live Caller ID/phone integration, live OPV/PVM/Medicare/IHI checks, taskpane, Command Centre, broad diary redesign, and weakening staff confirmation |
| Verification | Plan must specify exact copy changes, card hierarchy, pulse/accessibility guardrails, deterministic smoke checks, asset version checks, and failure signs before implementation release |
| Status | Integrated |

### Workstream EC - Bernie Product/API Acceptance Review

| Item | Value |
|---|---|
| Owner | Codex subagent |
| Branch | `codex/bernie-reception-acceptance-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-bernie-reception-acceptance-review.md` |
| Goal | Independently analyse the screenshots, current Bernie code, and implementation-plan fit, then submit acceptance criteria and risks for Ariadne to use when judging worker plans |
| In Scope | Plan packet / review notes first only; read-only inspection of Bernie backend contracts, diary UI, review harness, Access AI/audit seams, `orchestration/resource_admin_bernie_tool_design.md`, and `orchestration/phase_programmes.md`; recommend what should be fixed in Sprint 96 versus deferred; explicitly challenge overreach into Caller ID/OPV/phone integration |
| Out of Scope | Production code edits before plan approval, integrating other workers, live service setup, broad implementation-plan rewrite, and implementation release |
| Verification | Subagent plan/review must include what is working, what is not working, proposed acceptance gates, likely hidden risks, and suggested resubmission criteria for Claude/Antigravity plans |
| Status | Integrated |

## Sprint 74: Bernie Instruction Readiness Reset Polish

| Item | Value |
|---|---|
| Status | Integrated by Ariadne with bounded post-worker repair; verification passed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Complete |
| Product Goal | Make selected-context Bernie instruction readiness clearer and reset pending instruction state cleanly before live staff-pilot smoke |

### Workstream DR - Bernie Instruction Readiness Reset Polish

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-bernie-instruction-readiness-reset-polish.md` |
| Goal | Plan, then after approval refine chip/typed instruction readiness copy and reset behaviour without weakening explicit submit or confirmation gates |
| In Scope | Plan packet first; after approval `docs/diary/diary.{html,css,js}` and `review/test_diary_smoke.py` as needed; selected linked appointment context only; clear staff-supervised ready-to-submit copy after chip selection or typed instruction; reset instruction/interpreter state when Change is clicked, the current appointment is re-imported, or imported context becomes stale; no automatic provider call before explicit staff submit; preserve stale-selection guard, allowlist gate, no manual IDs in ordinary mode, no URL/browser-storage instruction persistence, explicit approval checkbox, and asset version bump if runtime assets change |
| Out of Scope | Backend routes/schemas/models, migrations, provider/Gemini changes, autonomous booking, default production exposure changes, query-string free-text intake, browser storage for instructions/context, patient/practitioner search redesign, taskpane, Command Centre, billing, SMS, resource admin, broad diary redesign, dependency/security work, and unrelated CSS cleanup |
| Verification | Plan packet first; after approval bundled Node syntax check, focused route-intercepted Bernie UI checks for chip/typed readiness copy, Change reset, re-import reset, stale-context reset/no chips/no call, confirmation gating, full diary review harness if diary runtime assets change, frontend version integrity, and `git diff --check` |
| Status | Integrated |

## Sprint 73: Bernie Selected Appointment Instruction Affordance

| Item | Value |
|---|---|
| Status | Integrated by Ariadne with bounded post-worker repair; pushed, mirrored, audited, deployed, and closed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Complete |
| Product Goal | Make the staff-visible Bernie pilot instruction surface easier and safer to use from imported selected-appointment context |

### Workstream DO - Bernie Selected Appointment Instruction Affordance

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-bernie-selected-instruction-affordance.md` |
| Goal | Plan, then after approval add safe selected-context instruction affordances without bypassing explicit staff submit or confirmation gates |
| In Scope | Plan packet first; after approval `docs/diary/diary.{html,css,js}` and `review/test_diary_smoke.py` as needed; selected linked appointment context only; bounded suggested instruction buttons/chips or concise context-aware placeholder/copy; no automatic provider call before explicit staff submit; no PHI-heavy persistence/logging; preserve stale-selection guard, allowlist gate, no manual IDs in ordinary mode, explicit approval checkbox, and asset version bump if runtime assets change |
| Out of Scope | Backend routes/schemas/models, migrations, provider/Gemini changes, autonomous booking, default production exposure beyond existing allowlisted launcher, query-string free-text intake, browser storage for instructions/context, patient/practitioner search redesign, taskpane, Command Centre, billing, SMS, resource admin, broad diary redesign, dependency/security work, and unrelated CSS cleanup |
| Verification | Plan packet first; after approval JS syntax, focused route-intercepted Bernie UI checks for suggested instruction affordance/no-auto-call/stale-context preservation/confirm gating, full diary review harness if runtime assets change, frontend version integrity, and `git diff --check` |
| Status | Integrated |

### Workstream DP - Bernie Selected Instruction Safety Review

| Item | Value |
|---|---|
| Owner | Claude |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-bernie-selected-instruction-safety-review.md` |
| Goal | Provide independent read-only safety/contract review for selected-appointment instruction affordances |
| In Scope | Read-only review of `docs/diary/diary.js`, `review/test_diary_smoke.py`, and relevant orchestration context; submit concrete acceptance criteria, edge cases, and safety concerns to Codex |
| Out of Scope | Production code edits, backend/provider/schema/migration changes, frontend implementation, dependency work, taskpane, Command Centre, billing, SMS, resource admin, and broad diary redesign |
| Verification | `git status --short --branch` before submit; `git diff --check` only if the worker unexpectedly edits a file |
| Status | Integrated |

### Workstream DQ - Codex Acceptance Criteria Review

| Item | Value |
|---|---|
| Owner | Codex subagent Mencius |
| Branch | N/A read-only subagent |
| Task Packet | Direct subagent prompt |
| Goal | Independently identify existing functions/tests and acceptance risks for Sprint 73 |
| In Scope | Read-only inspection of Bernie pilot code and diary smoke harness; return concise acceptance and edge-case review to Ariadne |
| Out of Scope | File edits, implementation, integration decisions |
| Verification | Ariadne reviews the returned subagent notes before approving implementation |
| Status | Complete; acceptance notes reviewed by Ariadne |

## Sprint 70: Bernie Staff-Visible Pilot Entry Path

| Item | Value |
|---|---|
| Status | Integrated by Ariadne; pushed, mirrored, audited, and deployed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Antigravity worker packet superseded; Ariadne implemented bounded diary/review-harness change |
| Product Goal | Expose the supervised Bernie booking-assistant panel through a staff-visible, non-default, allowlisted diary entry path without manual ID exposure |

### Workstream DN - Bernie Staff-Visible Pilot Entry Path

| Item | Value |
|---|---|
| Owner | Ariadne/orchestrator after Antigravity CLI no-op |
| Branch | `master` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-bernie-staff-visible-pilot-entry-path.md` |
| Goal | Plan, then after approval expose the existing supervised Bernie booking-assistant panel through a staff-visible non-default diary entry path for allowlisted pilot use |
| In Scope | Plan packet first; after approval diary UI assets and review harness updates as needed; visible entry only when existing pilot/eligibility gate allows it; launcher uses real selected linked appointment context or another explicit non-manual context source; no manual patient/practitioner ID fields in staff-visible mode; dev/manual fallback hidden behind explicit dev flags; instruction readiness, compact context summary, supervised confirmation, no default production exposure, no autonomous writes, and asset version bumps preserved |
| Out of Scope | Backend/provider/schema/migration changes unless the accepted plan proves a tiny contract-only adjustment is unavoidable; autonomous booking, default production exposure, query-string free-text intake, URL/browser-storage context persistence, PHI-heavy logging, patient/practitioner search redesign, taskpane, Command Centre, billing, SMS, resource admin, broad diary redesign, and unrelated CSS cleanup |
| Verification | Plan packet first; after approval bundled Node syntax check, route-intercepted default-hidden/allowlisted-visible/context/no-manual-ID/readiness/confirmation checks, full diary review harness if diary runtime assets change, frontend version integrity, and `git diff --check` |
| Status | Superseded as worker packet; integrated by orchestrator |

## Sprint 69: Bernie Context Readiness Summary

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, audited, and deployed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Antigravity plan accepted; implementation integrated with Codex bugfix and rendered product review |
| Product Goal | Ensure the Bernie pilot panel only presents instruction entry as actionable once context is ready, and keeps a compact context summary visible |

### Workstream DM - Bernie Context Readiness Summary

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-bernie-context-readiness-summary.md` |
| Goal | Plan, then after approval improve panel readiness and selected-context continuity before staff-visible exposure |
| In Scope | Plan packet first; after approval diary UI/readiness code and review harness updates as needed; no-context state should not show an actionable instruction submit; valid imported/manual context should show a compact non-PHI context summary through instruction and confirmation states; existing explicit gates preserved |
| Out of Scope | Backend/provider/schema/migration changes, appointment mutation semantics, patient/practitioner search, production/default exposure changes, autonomous booking, taskpane, Command Centre, billing, SMS, resource admin, broad redesign, PHI-heavy logging, URL/browser-storage persistence, and unrelated CSS cleanup |
| Verification | Plan packet first; after approval bundled Node syntax check, route-intercepted checks for no-context and selected-context summary states, full diary review harness if diary runtime assets change, frontend version integrity, and `git diff --check` |
| Status | Integrated |

## Sprint 68: Bernie Pilot Review Ergonomics

| Item | Value |
|---|---|
| Status | Integrated locally; closeout verification passed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Antigravity plan accepted; implementation integrated with Codex wording/style cleanup |
| Product Goal | Make the existing Bernie pilot context/instruction/review panel read more clearly as a supervised, explicit staff workflow |

### Workstream DL - Bernie Pilot Review Ergonomics

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-bernie-pilot-review-ergonomics.md` |
| Goal | Plan, then after approval refine staff-facing wording and compact status hierarchy inside the existing Bernie pilot panel |
| In Scope | Plan packet first; after approval diary UI copy/style and review harness updates as needed; selected appointment context wording; manual fallback wording; staff instruction input wording; blocked/provisional/no-selection messages; supervised confirmation reminders; existing safety gates preserved |
| Out of Scope | Backend/provider/schema/migration changes, appointment mutation semantics, patient/practitioner search, production/default exposure changes, autonomous booking, taskpane, Command Centre, billing, SMS, resource admin, broad redesign, PHI-heavy logging, and URL/browser-storage persistence |
| Verification | Plan packet first; after approval bundled Node syntax check, focused route-intercepted review checks as needed, full diary review harness if diary runtime assets change, frontend version integrity, and `git diff --check` |
| Status | Integrated |

## Sprint 67: Bernie Selected Appointment Context

| Item | Value |
|---|---|
| Status | Integrated locally; closeout verification passed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Antigravity plan accepted; implementation integrated with Codex safety cleanup |
| Product Goal | Replace the temporary typed-only Bernie pilot context path with a real diary-selected appointment context source |

### Workstream DK - Bernie Selected Appointment Context

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-bernie-selected-appointment-context.md` |
| Goal | Plan, then after approval let staff explicitly use the currently selected linked diary appointment as Bernie pilot context |
| In Scope | Plan packet first; after approval `docs/diary` UI assets and `review/` harness checks as needed; active appointment detection; explicit use-selected-appointment affordance; practitioner/patient context from linked appointments; blocked state for no selection, missing practitioner, provisional, or unlinked patient; manual ID fallback retained; no URL/localStorage/sessionStorage context persistence; diary asset version bump if runtime assets change |
| Out of Scope | Backend routes/schemas/models, migrations, autonomous booking, broad patient/practitioner search, patient lookup UI, taskpane, Command Centre, billing, SMS, resource admin, appointment mutation behavior, PHI-heavy logging, broad diary redesign, and unrelated refactors |
| Verification | Plan packet first; after approval bundled Node syntax check, focused route-intercepted Playwright checks for linked/blocked contexts and no persistence, full review harness if diary runtime assets change, frontend version integrity, and `git diff --check` |
| Status | Integrated |

## Sprint 66: Bernie Staff Instruction Input Surface

| Item | Value |
|---|---|
| Status | Integrated locally; closeout verification passed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Antigravity plan accepted after scope narrowing; implementation integrated with Codex cleanup |
| Product Goal | Replace temporary structured-context instruction construction with a proper staff-entered, pilot-gated instruction surface that avoids query-string free text |

### Workstream DJ - Bernie Staff Instruction Input Surface

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-bernie-staff-instruction-input-surface.md` |
| Goal | Plan, then after approval add a compact staff instruction input inside the existing Bernie pilot/review launch path |
| In Scope | Plan packet first; after approval `docs/diary` UI assets and `review/` harness checks as needed; body-only staff instruction submission; no query-string or localStorage free-text intake; no automatic provider call before explicit staff action; empty/clarification/blocked states; existing pilot/context/approval gates; frontend asset version bump if runtime assets change |
| Out of Scope | Backend routes/schemas/provider changes, autonomous booking, production default exposure, PHI-heavy logging or persistence, patient/practitioner selector redesign, taskpane, Command Centre, migrations, billing, SMS, resource admin, broad diary redesign, and unrelated refactors |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, focused route-intercepted review harness checks, full diary review harness if diary runtime assets change, frontend version integrity checks, and `git diff --check` |
| Status | Integrated |

## Sprint 55: Bernie Dev Review Fixture Route

| Item | Value |
|---|---|
| Status | Queued; waiting for Claude plan |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Pending Claude plan review |
| Product Goal | Provide deterministic non-PHI backend fixture payloads for the dev-gated Bernie review panel without hand-authored Playwright payloads |

### Workstream DI - Bernie Dev Review Fixture Route

| Item | Value |
|---|---|
| Owner | Claude |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-bernie-dev-review-fixture-route.md` |
| Goal | Plan, then after approval add a narrow backend-only dev/test fixture source for Bernie review payloads |
| In Scope | Plan packet first; after approval backend dev/test-only route or fixture helper, deterministic non-PHI blocked/candidate/confirmation-ready payloads, auth/practice/default gating if route-exposed, no appointment/audit writes, no LLM/provider calls, and focused pytest coverage |
| Out of Scope | Diary UI, taskpane, Command Centre, live autonomous booking, production default exposure, real patient data, Gemini/LLM parsing, migrations unless strictly unavoidable, appointment write semantics, SMS, billing, resource admin, broad router redesign, and unrelated test hygiene |
| Verification | Plan packet first; after approval py_compile touched Python, focused fixture tests, adjacent Bernie supervised-booking/review payload tests where relevant, no-write/no-audit/no-LLM proof, auth/practice/default-gating checks if route-exposed, and `git diff --check` |
| Status | Queued |

## Sprint 54: Bernie Dev Review Launch Affordance

| Item | Value |
|---|---|
| Status | Queued; waiting for Antigravity plan |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Pending Antigravity plan review |
| Product Goal | Make the dev-gated Bernie review path easier to launch without hand-crafted full query URLs, while preserving hidden/no-call defaults |

### Workstream DH - Bernie Dev Review Launch Affordance

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-bernie-dev-review-launch-affordance.md` |
| Goal | Plan, then after approval add a tiny dev-only affordance for entering the existing Bernie live review path |
| In Scope | Plan packet first; after approval `docs/diary` UI assets and `review/` harness checks as needed; affordance visible only with an explicit dev flag, route-intercepted launcher/review/confirm checks, default hidden/no-call proof, explicit approval gating, and asset version bump if runtime assets change |
| Out of Scope | Backend routes/schemas, live autonomous booking, production default exposure, natural-language LLM parsing, real API writes in tests, taskpane, Command Centre, migrations, patient/resource admin, billing, SMS, broad diary redesign, and unrelated refactors |
| Verification | Plan packet first; after approval JS syntax checks, deterministic Playwright route-intercepted checks, default-mode no-call/no-exposure checks, frontend version integrity if assets change, existing diary review harness where relevant, and `git diff --check` |
| Status | Queued |

## Sprint 53: Bernie Dev-Mode Review Feature Flag

| Item | Value |
|---|---|
| Status | Queued; waiting for Antigravity plan |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Pending Antigravity plan review |
| Product Goal | Expose the supervised Bernie review/confirm path in ordinary diary dev mode behind an explicit opt-in flag without changing production default behaviour |

### Workstream DG - Bernie Dev-Mode Review Feature Flag

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-bernie-dev-review-feature-flag.md` |
| Goal | Plan, then after approval add a narrow dev-only opt-in path for the existing supervised Bernie review/confirm flow outside smoke mode |
| In Scope | Plan packet first; after approval `docs/diary` UI assets and `review/` harness checks as needed; explicit query/feature flag gate, default non-smoke no-exposure/no-call proof, route-intercepted supervised-booking and confirm-Bernie proof, explicit staff approval gating, and asset version bump if runtime assets change |
| Out of Scope | Backend routes/schemas, live autonomous booking, production default exposure, natural-language LLM parsing, real API writes in tests, taskpane, Command Centre, migrations, patient/resource admin, billing, SMS, broad diary redesign, and unrelated refactors |
| Verification | Plan packet first; after approval JS syntax checks, deterministic Playwright route-intercepted checks, default-mode no-call/no-exposure checks, frontend version integrity if assets change, existing diary review harness where relevant, and `git diff --check` |
| Status | Queued |

## Sprint 47: Bernie Wrapper Confirmation Review Harness

| Item | Value |
|---|---|
| Status | Queued; waiting for Codex worker plan |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Pending Codex worker plan review |
| Product Goal | Prove the supervised Bernie wrapper can hand confirmation-ready evidence to explicit confirm-Bernie without autonomous writes |

### Workstream CC - Bernie Wrapper Confirmation Review Harness

| Item | Value |
|---|---|
| Owner | Codex worker/subagent |
| Branch | `codex/bernie-wrapper-confirmation-review-harness` |
| Task Packet | `orchestration/agent_inbox/codex/codex-bernie-wrapper-confirmation-review-harness.md` |
| Goal | Plan, then after approval add a deterministic backend review harness proving wrapper output can be explicitly confirmed and blocked/candidate-only paths remain non-mutating |
| In Scope | Plan packet first; after approval focused backend tests/review harness only unless a tiny production fix is required by a real contract gap; wrapper -> confirm-Bernie success, confirmed=false block, stale-conflict block, candidate-only no-write, blocked normalization no-write, exactly-one appointment/audit write on success, and no LLM/provider calls |
| Out of Scope | Diary UI, taskpane, Command Centre, natural-language parsing, autonomous runtime execution, new write routes, schema redesign, migrations, SMS, billing, resource admin, broad appointment/audit redesign, and changing Sprint 40-46 semantics unless a verified bug is exposed |
| Verification | Plan packet first; after approval py_compile touched tests/Python, focused harness pytest, wrapper and confirm tests, Sprint 45 full-flow harness, adjacent slot-search/selection/create-proposal tests if production code changes, no-write/no-LLM/exactly-one-write proof, and `git diff --check` |
| Status | Queued |


## Sprint 44: Bernie Confirm Create-Proposal Contract

| Item | Value |
|---|---|
| Status | Queued; waiting for Codex worker plan |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Pending Codex worker plan review |
| Product Goal | Add the explicit supervised backend bridge that turns approved Bernie create-proposal evidence into exactly one appointment write with bounded audit evidence |

### Workstream CA - Bernie Confirm Create-Proposal Contract

| Item | Value |
|---|---|
| Owner | Codex worker/subagent |
| Branch | `codex/bernie-confirm-create-proposal` |
| Task Packet | `orchestration/agent_inbox/codex/codex-bernie-confirm-create-proposal-contract.md` |
| Goal | Plan, then after approval add a narrow backend confirmation/write contract for supervised Bernie slot-selection/create-proposal evidence |
| In Scope | Plan packet first; after approval appointment router/schema/tests as needed; explicit confirmation, practice/auth/conflict checks, exactly-one appointment write on success, bounded audit evidence, no LLM/provider calls, and reuse of Sprint 43 harness as regression protection |
| Out of Scope | Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous Bernie runtime, direct natural-language execution, SMS, billing, resource admin, migrations unless strictly unavoidable, broad appointment redesign, broad audit redesign, and unrelated test hygiene |
| Verification | Plan packet first; after approval py_compile touched Python, focused confirmation/write pytest, Sprint 43 flow harness, adjacent slot-selection/create-proposal tests, no-write proof for failed confirmations, exactly-one-write/audit proof for success, no-LLM proof, and `git diff --check` |
| Status | Queued |

## Sprint 43: Bernie Slot Flow Review Harness

| Item | Value |
|---|---|
| Status | Integrated locally; closeout verification passed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Codex worker plan accepted and implementation integrated |
| Product Goal | Prove the deterministic Bernie normalize-search-select flow through compact backend tests before adding final appointment write semantics |

### Workstream BZ - Bernie Slot Flow Review Harness

| Item | Value |
|---|---|
| Owner | Codex worker/subagent |
| Branch | `codex/bernie-slot-flow-review-harness` |
| Task Packet | `orchestration/agent_inbox/codex/codex-bernie-slot-flow-review-harness.md` |
| Goal | Plan, then after approval add deterministic backend review harness coverage for command normalization, normalized slot search, supervised slot selection, mismatch/conflict blocks, and no appointment/audit/LLM side effects |
| In Scope | Plan packet first; after approval focused backend tests/review helpers only, likely `tests/test_bernie_slot_flow_review_harness.py` or adjacent helpers; small testability extraction only if justified |
| Out of Scope | Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous Bernie runtime, final appointment write/confirmation bridge, audit mutation, migrations, billing, SMS, resource admin, broad refactors, and unrelated test hygiene |
| Verification | Plan packet first; after approval py_compile touched Python, focused pytest for the harness, adjacent Bernie slot endpoint tests if production code changes, no-mutation/no-LLM proof, and `git diff --check` |
| Status | Integrated |

## Sprint 42: Bernie Slot Selection Proposal Contract

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, audited, and closed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Codex worker plan accepted and implementation integrated |
| Product Goal | Let future Bernie/reception workflows choose one candidate from normalized slot-search results and receive a supervised create-proposal-compatible payload without creating an appointment |

### Workstream BY - Bernie Slot Selection Proposal Contract

| Item | Value |
|---|---|
| Owner | Codex worker/subagent |
| Branch | `codex/bernie-slot-selection-proposal` |
| Task Packet | `orchestration/agent_inbox/codex/codex-bernie-slot-selection-proposal-contract.md` |
| Goal | Plan, then after approval add a backend-only supervised selection/review contract that converts a selected safe slot candidate into existing appointment-create proposal evidence without confirming or mutating an appointment |
| In Scope | Plan packet first; after approval a narrow appointment-router/helper/schema/test slice, candidate/date/time/duration/practitioner/location/patient validation, create-proposal-compatible output or blocks/warnings, no-LLM/no-write proof, and compatibility with existing normalized slot-search and create-proposal contracts |
| Out of Scope | Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous tool execution, actual appointment creation/edit/status/cancel, audit mutation, SMS, billing, patient demographics, resource admin, migrations unless strictly unavoidable, DB-backed natural-language name resolution, and broad scheduling redesign |
| Verification | Plan packet first; after approval py_compile touched backend modules/tests, focused pytest for the new selection contract, adjacent normalized slot-search/proposal/create-proposal tests if shared code changes, explicit no-mutation/no LLM proof, and `git diff --check` |
| Status | Integrated |

## Sprint 41: Bernie Normalized Slot Search Execution Contract

| Item | Value |
|---|---|
| Status | Integrated, verified, pushed, mirrored, audited, and closed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Codex worker plan accepted and implementation integrated |
| Product Goal | Let future Bernie/reception workflows submit one structured slot-search command and receive both normalization evidence and non-mutating candidate slots, without creating appointments or adding autonomous booking |

### Workstream BX - Bernie Normalize-And-Search Contract

| Item | Value |
|---|---|
| Owner | Codex worker/subagent |
| Branch | `codex/bernie-normalized-slot-search` |
| Task Packet | `orchestration/agent_inbox/codex/codex-bernie-normalized-slot-search-contract.md` |
| Goal | Plan, then after approval add a backend-only non-mutating endpoint/helper that accepts `SlotSearchCommandIn`, requires explicit `reference_date`, normalizes it, and if safe runs the existing slot-search proposal logic to return candidate slots plus normalization context |
| In Scope | Plan packet first; after approval narrow appointment-router/helper refactor if needed, response schema/tests as needed, authentication/role behaviour consistent with adjacent slot-search endpoints, deterministic reference-date handling, invalid-command blocked response without slot-search execution, safe-command candidate search through existing non-mutating proposal path, and no-LLM/no-write proof |
| Out of Scope | Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous tool execution, appointment creation/edit/status/cancel, audit mutation, SMS, billing, patient demographics, resource admin, migrations unless strictly unavoidable, DB-backed name-to-UUID resolution, and broad scheduling redesign |
| Verification | Plan packet first; after approval py_compile touched backend modules/tests, focused pytest for the new endpoint/helper, existing normalizer tests, adjacent slot-search proposal tests, explicit no-mutation/no LLM proof, and `git diff --check` |
| Status | Integrated |

## Sprint 40: Bernie Slot Normalize Endpoint Contract

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrored, audited, and closed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Codex worker plan accepted and implementation integrated |
| Product Goal | Expose the deterministic Sprint 39 Bernie slot-command normalizer through a narrow backend route/tool contract without executing searches or creating appointments |

### Workstream BW - Bernie Slot Normalize Endpoint Contract

| Item | Value |
|---|---|
| Owner | Codex worker/subagent |
| Branch | `codex/bernie-slot-normalize-endpoint` |
| Task Packet | `orchestration/agent_inbox/codex/codex-bernie-slot-normalize-endpoint-contract.md` |
| Goal | Plan, then after approval add a non-mutating backend endpoint or route helper for `SlotSearchCommandIn` -> `SlotSearchCommandResult` |
| In Scope | Plan packet first; after approval role-gated/practice-scoped backend route/tool contract, explicit deterministic reference-date handling, focused tests for auth/shape/invalid input/non-mutation/no LLM/search execution, and compatibility with `SlotSearchProposalIn` |
| Out of Scope | Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous tool execution, appointment creation, slot-search execution beyond normalizer invocation, audit mutation, SMS, billing, patient demographics, resource admin, migrations unless strictly unavoidable, and DB-backed name-to-UUID resolution |
| Verification | Plan packet first; after approval py_compile touched backend modules/tests, focused endpoint/route pytest, existing normalizer tests, adjacent slot-search proposal tests if schemas/routes are touched, non-mutation/no LLM proof, and `git diff --check` |
| Status | Integrated |

## Sprint 39: Bernie Slot Command Normalizer Contract

| Item | Value |
|---|---|
| Status | Integrated |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Product Goal | Normalize future Bernie/reception slot-search command input into the typed slot-search constraint object without executing searches or creating appointments |

### Workstream S39-A - Backend Slot Command Normalizer Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-claude-bernie-slot-command-normalizer-contract.md` |
| Goal | Plan, then after approval add a deterministic backend command-normalization contract for future Bernie/reception slot-search commands |
| In Scope | Plan packet first; after approval backend command-normalization schemas/service/tests only as needed, likely `app/schemas/appointments.py` or a small appointments/Bernie helper plus focused tests; accept structured or LLM-like JSON/dict input, validate/normalize dates, times, practitioner/patient/location/type identifiers where possible, and output a `SlotSearchProposalIn`-compatible constraint object plus warnings/blocks/summary |
| Out of Scope | Diary UI, live Bernie runtime, Gemini/LLM calls, autonomous tool execution, appointment creation/search execution, taskpane, Command Centre, SMS, billing, patient demographics, resource admin, database migrations unless strictly unavoidable, and broad scheduling redesign |
| Verification | Plan packet first; after approval py_compile touched backend modules/tests, focused pytest covering accepted input shapes, invalid/missing constraints, date/time normalization, non-mutation proof, no LLM/search execution, and `git diff --check` |
| Status | Integrated |

## Sprint 38: Bernie-Safe Slot Search Proposal Foundation

| Item | Value |
|---|---|
| Status | Integrated; closeout pending push/mirror/audit |
| Launch Gate | Complete |
| Integration Gate | Passed; implementation review packets polled and verified |
| Product Goal | Give future Bernie/reception workflows a non-mutating, typed slot-search proposal contract and deterministic read-only preview harness |

### Workstream S38-A - Backend Slot Search Proposal Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-claude-bernie-slot-search-proposal-contract.md` |
| Goal | Plan, then after approval add a non-mutating backend slot-search proposal contract for future Bernie/reception use |
| In Scope | Plan packet first; after approval backend appointment/slots/proposal surfaces only as needed, likely `app/schemas/appointments.py`, `app/routers/appointments.py`, and focused tests; endpoint must be practice-scoped, auth/role-gated, location-aware where current slot logic supports it, return typed candidate slots plus warnings/blocks/summary, and never write appointments or audit rows |
| Out of Scope | Diary UI implementation, autonomous Bernie runtime, LLM calls, taskpane, Command Centre, SMS, billing, patient demographics, resource admin, mutation of appointments, and broad scheduling redesign |
| Verification | Plan packet first; after approval py_compile touched backend modules/tests, focused pytest proving role/practice scoping, no appointment/audit writes, expected candidate slot output, conflict/break/location handling where applicable, and `git diff --check` |
| Status | Integrated after Claude review packet and Ariadne verification |

### Workstream S38-B - Diary Slot Search Preview Harness

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-antigravity-diary-slot-search-preview-harness.md` |
| Goal | Plan, then after approval add a tiny deterministic diary/review harness surface for future read-only slot-search proposal previews |
| In Scope | Plan packet first; after approval docs/diary smoke fixtures and review harness files only unless a minimal diary helper is unavoidable; add deterministic checks for a read-only slot-search proposal preview shape from mock data using stable selectors/compact assertions |
| Out of Scope | Backend implementation, live API integration unless Claude's contract is already integrated and trivially callable, autonomous Bernie runtime, appointment create/edit/status/cancel mutations, taskpane, Command Centre, resource admin, SMS, billing, and broad diary layout changes |
| Verification | Plan packet first; after approval `node --check` if diary JS changes, deterministic review pytest for slot-search preview, frontend version check if assets change, and `git diff --check` |
| Status | Integrated after Antigravity review packet and Ariadne verification |


## Sprint 37: Appointment Audit Warning Summary

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrored, audited, and closed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Passed; implementation review packets polled and verified |
| Product Goal | Persist and display bounded warning metadata for confirmed appointment proposal mutations so audit history can prove when staff confirmed warnings |

### Workstream S37-A - Backend Audit Warning Summary Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-claude-appointment-audit-warning-summary-contract.md` |
| Goal | Plan, then after approval persist safe warning metadata for confirmed appointment proposal mutations |
| In Scope | Plan packet first; after approval appointment proposal/confirmation and audit-log backend surfaces only as needed, likely `app/models/appointments.py`, `app/schemas/appointments.py`, `app/routers/appointments.py`, Alembic migration if persistence requires one, and focused appointment audit/proposal tests |
| Out of Scope | Diary UI implementation, broad supervisor dashboard, Bernie runtime/tool execution, taskpane, Command Centre, SMS, billing, patient demographics, unrelated appointment flows, broad audit framework beyond appointment mutation warning metadata |
| Verification | Plan packet first; after approval py_compile touched backend modules, focused pytest for appointment proposal/audit warning-summary persistence, adjacent audit/proposal tests if touched, Alembic upgrade head if migration added, and `git diff --check` |
| Status | Integrated after Claude review packet and Ariadne bounded sanitizer/migration repair |

### Workstream S37-B - Diary Audit Warning Summary UI

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-antigravity-diary-audit-warning-summary-ui.md` |
| Goal | Plan, then after approval display persisted appointment audit warning metadata in the read-only diary Audit History section |
| In Scope | Plan packet first; after approval `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`, smoke fixtures, and `review/test_diary_smoke.py` or `review/checks_diary.json` as needed for deterministic warning-summary assertions |
| Out of Scope | Backend implementation, appointment mutation/proposal logic, broad booking modal redesign, supervisor dashboard, Bernie runtime/tool execution, taskpane, Command Centre, SMS, billing, resource administration, cancelled appointment restore/reactivation |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, deterministic diary review smoke with compact assertions for warning summary rendering, frontend version check if assets change, `git diff --check`, targeted browser checks only if structural assertions cannot prove behaviour |
| Status | Integrated after Antigravity review packet and Ariadne verification |


## Sprint 36: Diary Audit History Keyboard Accessibility

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrored, audited, and closed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Passed; pushed/mirrored/audited |
| Product Goal | Make the read-only audit-history toggle keyboard-accessible and semantically clearer without changing visible layout or mutation behaviour |

### Workstream S36-A - Audit History Toggle Semantics

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-audit-history-keyboard-accessibility.md` |
| Goal | Plan, then after approval add focused keyboard/ARIA semantics for the audit-history toggle and deterministic assertions |
| In Scope | Plan packet first; after approval `docs/diary/diary.html`, `docs/diary/diary.js`, and `review/test_diary_smoke.py` only unless a directly required adjacent frontend file is unavoidable |
| Out of Scope | Backend code, appointment mutation/proposal flows, broad booking modal redesign, taskpane, Command Centre, billing, SMS, AI provider code, resource administration, cancelled appointment review, non-audit-history controls |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, deterministic diary smoke, frontend version check if assets change, and `git diff --check` |
| Status | Integrated after Antigravity review packet and Ariadne verification |

## Sprint 35: Diary Audit History Test-Hook Hardening

| Item | Value |
|---|---|
| Status | Integrated locally; closeout verification passed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Passed; pending final push/mirror/audit |
| Product Goal | Keep audit-history UI review cheap and robust by adding stable test hooks and deterministic assertions for the read-only audit-history section |

### Workstream S35-A - Diary Audit History Stable Selectors

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-audit-history-testid-hardening.md` |
| Goal | Plan, then after approval add stable data-testid hooks and smoke assertions for the audit-history section without changing mutation behaviour |
| In Scope | Plan packet first; after approval `docs/diary/diary.html`, `docs/diary/diary.js`, and `review/test_diary_smoke.py` only unless a directly required adjacent frontend file is unavoidable |
| Out of Scope | Backend code, appointment mutation/proposal flows, taskpane, Command Centre, billing, SMS, AI provider code, resource administration, cancelled appointment review, broad booking modal redesign |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, deterministic diary smoke, frontend version check if assets change, and `git diff --check` |
| Status | Integrated after Antigravity review packet and Ariadne verification |

## Sprint 34: Appointment Audit History Readability

| Item | Value |
|---|---|
| Status | Integrated locally; closeout verification passed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Passed; pending final push/mirror/audit |
| Product Goal | Make confirmed appointment audit history understandable to staff by replacing raw actor/action/status details with safe, readable metadata while preserving proposal-first and read-only boundaries |

### Workstream S34-A - Backend Audit Actor Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-audit-actor-contract.md` |
| Goal | Plan, then after approval add or prove a backend contract for safe confirmed-by actor display metadata on appointment audit rows |
| In Scope | Plan packet first; after approval appointment audit endpoint/schema/router tests for a non-PHI staff actor display field, preserving existing audit writes and practice scoping |
| Out of Scope | Diary UI, broad user-directory API, PHI in audit rows, warning-code persistence, supervisor dashboard, Bernie execution, taskpane, Command Centre, billing, SMS |
| Verification | Plan packet first; after approval py_compile touched backend modules, focused audit actor tests plus existing audit tests, adjacent mutation tests if touched, and `git diff --check` |
| Status | Integrated by Ariadne from accepted Claude plan after Claude 429/session limit |

### Workstream S34-B - Diary Audit Readability UI

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-audit-history-readability.md` |
| Goal | Plan, then after approval polish the read-only diary audit history copy so staff see friendly actor/action/status text without new mutation affordances |
| In Scope | Plan packet first; after approval `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`, smoke fixtures, and deterministic review checks for audit readability if useful |
| Out of Scope | Backend implementation, write actions from audit history, unrelated booking modal redesign, taskpane, Command Centre, AI provider code, restore/reactivation, billing, SMS, Bernie execution |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, deterministic diary review smoke, frontend version check if assets change, `git diff --check`, targeted browser checks only if structural checks cannot verify behaviour |
| Status | Integrated after Antigravity review packet and Ariadne verification |

## Sprint 33: Appointment Proposal Audit/History Foundation

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrored, audited, and closed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Claude and Antigravity submissions reviewed, integrated, and hotfixed by Ariadne |
| Product Goal | Give high-risk appointment proposal decisions a deterministic audit/history foundation so future supervisors and Bernie tooling can review what was confirmed without adding direct model-to-database autonomy |

### Workstream S33-A - Backend Proposal Audit Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-proposal-audit-contract.md` |
| Goal | Plan, then after approval add or prove a backend contract for recording confirmed high-risk appointment proposal decisions |
| In Scope | Plan packet first; after approval backend appointment audit/proposal-history model/API and focused pytest coverage for confirmed create/update/status/waiting-area/delete writes, scoped history reads, cross-practice denial, and no audit rows for blocked/aborted proposals |
| Out of Scope | Diary UI, taskpane, Command Centre, Gemini/AI provider code, receptionist messaging, restore/reactivation, billing, SMS, broad audit framework, and direct Bernie execution |
| Verification | Plan packet first; after approval py_compile touched backend modules, focused pytest for audit/proposal-history contracts plus existing appointment mutation suites affected by touched code, and `git diff --check` |
| Status | Integrated |

### Workstream S33-B - Diary Proposal History Review UI

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-proposal-history-review-ui.md` |
| Goal | Plan, then after approval add or scaffold a lightweight read-only diary review surface for proposal/audit history when the backend contract exists |
| In Scope | Plan packet first; after approval `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`, smoke-mode fixture/hooks if needed, and cheap review assertions for the read-only history affordance |
| Out of Scope | Backend implementation, taskpane, Command Centre, Gemini/AI provider code, write actions from the history surface, restore/reactivation, broad supervisor dashboard, billing/SMS, and visual redesign of unrelated diary panels |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, deterministic diary review smoke, any new cheap Playwright/review assertion, frontend version check if assets change, and targeted browser checks only if structural checks cannot verify the behaviour |
| Status | Integrated |

## Sprint 32: No-show/DNA Attendance Outcome Semantics

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrored, audited, and closed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Claude implemented a focused backend proof suite; Antigravity frontend workstream superseded after existing diary semantics and cheap checks were verified |
| Product Goal | Make No Show and DNA appointment outcomes explicit, proposal-first, terminal, non-blocking, and cheap to review without confusing them with cancellation or active waiting-room state |

### Workstream S32-A - Backend No-show/DNA Status Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-noshow-dna-status-contract.md` |
| Goal | Plan, then after approval harden or prove the backend appointment status proposal contract for NoShow and DNA attendance outcomes |
| In Scope | Plan packet first; after approval `app/routers/appointments.py`, `app/schemas/appointments.py` only if needed, focused appointment status/proposal/waiting-area tests for NoShow/DNA terminal transitions, non-blocking slot behaviour, and no direct mutation before proposal confirmation |
| Out of Scope | Diary frontend, taskpane, Command Centre, cancellation reason/note capture, cancelled appointment review UI, recurrence, SMS/reminders, billing, broad audit logging, migrations unless a verified backend contract gap requires one |
| Verification | Plan packet first; after approval py_compile touched appointment modules, focused pytest for appointment status/proposal/waiting-area/no-show-DNA coverage, adjacent conflict tests if touched, and `git diff --check` |
| Status | Integrated locally |

### Workstream S32-B - Diary No-show/DNA Flow

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-noshow-dna-flow.md` |
| Goal | Plan, then after approval make the diary no-show/DNA user flow clear and reviewable |
| In Scope | Plan packet first; after approval `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js` only if needed, deterministic review checks in `review/`, smoke-mode fixtures/test hooks, and asset cache-bust if diary assets change |
| Out of Scope | Backend routes/models/tests/migrations, taskpane, Command Centre, resource administration, cancellation reason/note capture, cancelled appointment review redesign, recurrence, broad visual restyle, direct mutation before proposal confirmation |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js` if touched, `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q`, `python scripts/check_frontend_versions.py` if assets change, targeted Playwright/DOM assertions where useful, and `git diff --check` |
| Status | Superseded; no frontend code delta integrated |

## Sprint 31: AI Boundary And Cheap Review Harness

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrored, audited, deployed, and closed |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Claude and Antigravity submissions reviewed and accepted |
| Product Goal | Formalize the first practical AI provider boundary and expand deterministic diary review so the sprint loop uses CLI/text and Playwright/pytest before GUI automation |

### Workstream S31-A - AI Provider Boundary Facade

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-ai-provider-boundary-facade.md` |
| Goal | Plan, then after approval add the first thin EMR4-owned AI service boundary for clinical/Bernie-facing AI contracts |
| In Scope | Plan packet first; after approval a small backend-only scaffold around existing Gemini consultation/letter usage, likely `app/services/ai/contracts.py`, `app/services/ai/service.py`, `app/services/ai/providers/gemini.py`, and focused tests/fixtures if justified |
| Out of Scope | Provider switch, LiteLLM integration, prompt rewrite, live Gemini credential work, diary frontend, taskpane UI, Command Centre UI, Bernie runtime, migrations, broad consultation/letter behaviour changes |
| Verification | Plan packet first; after approval py_compile touched Python modules, focused pytest for new AI contracts/tests, existing consultation/letter tests if touched and available, no live provider calls required, `git diff --check` |
| Status | Integrated locally |

### Workstream S31-B - Diary Review Harness Hardening

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-review-harness-hardening.md` |
| Goal | Plan, then after approval extend deterministic diary review checks so more user-review work runs through cheap Playwright/pytest assertions |
| In Scope | Plan packet first; after approval `review/checks_diary.json`, `review/harness.py`, `review/test_diary_smoke.py`, `review/README.md`, and minimal `docs/diary` test hooks/data-testid attributes if justified |
| Out of Scope | Backend API changes, migrations, production diary behaviour redesign, appointment mutation semantics, taskpane/Command Centre, Bernie runtime, broad visual restyle, Computer Use dependency |
| Verification | Plan packet first; after approval `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q`, `node --check docs/diary/diary.js` if touched, `npm run validate-all` if relevant, `git diff --check`; capture screenshots/traces only on failure |
| Status | Integrated locally |

## Sprint 29: Cancellation Reason Capture

| Item | Value |
|---|---|
| Status | Dispatched; plan gate pending |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Integration Gate | Pending worker plans and Codex approval |
| Product Goal | Let reception capture a short cancellation reason or note without weakening proposal-first cancellation safety |

### Workstream S29-A - Backend Cancellation Reason Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-cancellation-reason-contract.md` |
| Goal | Plan, then after approval add a minimal backend contract for cancellation reason/note capture |
| In Scope | `app/routers/appointments.py`, `app/schemas/appointments.py`, `app/models/appointments.py` only if a separate persisted cancellation field is justified, Alembic migration only if a new field is chosen, focused cancellation/proposal tests |
| Out of Scope | Diary frontend, taskpane, Command Centre, patient demographics, billing, SMS/reminders, broad audit logging, proposal review history |
| Verification | Plan packet first; after approval py_compile touched appointment modules, focused cancellation/delete proposal pytest, migration checks if added, adjacent proposal tests if touched, `git diff --check` |
| Status | Dispatched |

### Workstream S29-B - Diary Cancellation Reason Flow

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-cancellation-reason-flow.md` |
| Goal | Plan, then after approval add a small diary UI flow for optional cancellation reason/note capture |
| In Scope | `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`, smoke-mode cancellation reason simulation, asset cache-bust, minimal copy |
| Out of Scope | Backend routes/models/tests/migrations, taskpane, Command Centre, patient search/linking, Waiting Room layout redesign, Resource Administration, recurrence, broad modal redesign, direct delete before proposal confirmation |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, `npm run validate-all`, smoke/browser checks for empty reason, entered reason, abort, confirm, blocked proposal, waiting-area warning, `git diff --check` |
| Status | Dispatched |

## Sprint 28: Cancellation Proposal Safety

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrored, audited, and deployed v95 observed |
| Launch Gate | Closed; Claude and Antigravity plans were reviewed and implementation was released |
| Integration Gate | Complete; worker submissions reviewed and merged |
| Product Goal | Ensure destructive appointment cancellation/delete actions follow proposal-first safety semantics before any write |

### Workstream S28-A - Backend Cancel Proposal Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-cancel-proposal-contract.md` |
| Goal | Harden or prove the backend contract for cancellation/delete preflight before destructive appointment writes |
| In Scope | `app/routers/appointments.py`, `app/schemas/appointments.py`, focused appointment proposal/cancel/delete tests, minimal production fixes only if a real gap is found |
| Out of Scope | Diary frontend, taskpane, Command Centre, patient workflows, Resource Administration, migrations unless a schema issue is proven, direct writes that bypass proposal semantics |
| Verification | Plan packet first; after approval py_compile touched appointment router/schema, focused cancellation/delete proposal pytest, adjacent update/status proposal tests, `git diff --check` |
| Status | Integrated |

### Workstream S28-B - Diary Cancel Proposal Flow

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-cancel-proposal-flow.md` |
| Goal | Route the diary `Cancel Appointment` action through proposal-first safety semantics before destructive writes |
| In Scope | `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`, smoke-mode cancellation proposal simulation, asset cache-bust, minimal cancellation confirmation copy |
| Out of Scope | Backend routes/models/tests/migrations, taskpane, Command Centre, patient search/linking, Waiting Room layout, Resource Administration, recurrence, broad visual redesign, direct delete before proposal confirmation |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, `npm run validate-all`, smoke/browser checks for cancel proposal safe/warning/blocked/cancel-confirm/revert paths, `git diff --check` |
| Status | Integrated |

## Sprint 27: Diary Mouse Move/Resize Affordances

| Item | Value |
|---|---|
| Status | Integrated, pushed, mirrored, audited, and closed |
| Launch Gate | Closed; Claude and Antigravity plans were reviewed and implementation was released |
| Integration Gate | Closed; implementation submissions reviewed, integrated, and hotfixed by Ariadne |
| Product Goal | Give staff discoverable mouse affordances for moving and resizing appointments while preserving proposal-gated safety semantics |

### Workstream S27-A - Appointment Mouse Proposal Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-mouse-drag-proposal-contract.md` |
| Goal | Harden backend proposal/update coverage for mouse-equivalent move, resize, and resource-column changes |
| In Scope | `app/routers/appointments.py`, `app/schemas/appointments.py`, `tests/test_appointment_update_proposal.py` or adjacent proposal tests; minimal fixes only if a real contract gap is found |
| Out of Scope | Diary frontend, pointer UI, migrations/schema redesign, recurrence, patient identity, taskpane/Command Centre, direct writes that bypass proposals |
| Verification | `py_compile` for appointment router/schema, focused proposal pytest, `git diff --check` |
| Status | Integrated |

### Workstream S27-B - Diary Mouse Drag/Resize UX

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-mouse-drag-resize-affordances.md` |
| Goal | Add visible appointment drag/move and resize affordances that reuse the existing proposal-gated move/resize pathway |
| In Scope | `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`, and frontend smoke tooling if needed |
| Out of Scope | Backend route redesign, schema/migration, recurrence, patient search/linking, Waiting Room, Resource Administration, taskpane/Command Centre, direct mutation before confirmation |
| Verification | JS syntax, asset check, browser/Chrome smoke for preview/cancel/confirm/blocked conflict, `git diff --check` |
| Status | Integrated with Ariadne hotfix |

## Reasoning Budget Guidance

Use maximum reasoning for:

- architecture decisions
- security/privacy/clinical-safety decisions
- schema and migration design
- integration reviews
- debugging unclear failures

Use medium/high reasoning for:

- implementing an already-approved plan
- focused backend route work
- frontend UI implementation from a clear spec
- test writing

Use lower reasoning only for:

- mechanical version bumps
- formatting
- simple copy/docs updates
- running known commands

The default pattern should be: think hard at planning and review boundaries, execute
at medium/high once the plan is stable, then think hard again before integration.

## Sprint 26: Move/Resize Proposal Flow

| Item | Value |
|---|---|
| Programme | Phase 2 Programme 2B - Safe Appointment Mutation Workbench |
| Status | Integrated locally; closeout verification complete; pending push/audit |
| Launch Gate | Closed; Claude and Antigravity plans were reviewed and implementation was released |
| Integration Gate | Closed; implementation submissions reviewed, integrated, and hotfixed by Ariadne |
| Theme | Bring appointment move/resize interactions under the same proposal-first safety rail as create/edit/status/waiting-area changes |

### Workstream S26-A - Backend Move/Resize Proposal Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-move-resize-proposal-contract.md` |
| Goal | Plan and then harden the backend update-proposal contract for drag/drop-like date/time/resource moves and duration resize changes before any write |
| In Scope | Backend appointment update proposal route/schema/tests as needed; conflict blocks, break warnings, terminal-status blocks, practice isolation, and non-mutating proof |
| Out of Scope | Diary frontend implementation, drag/drop/resize UI, taskpane, Command Centre, Gemini, migrations unless the plan proves a schema issue, broad appointment redesign |
| Verification | Plan packet first; after approval focused appointment update proposal pytest checks, py_compile/check_backend as needed, and row-unchanged assertions |
| Status | Integrated |

### Workstream S26-B - Diary Move/Resize Proposal Flow

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-move-resize-proposal-flow.md` |
| Goal | Plan and then add or prepare the smallest diary UI path for appointment move/resize interactions to use proposal preflight before mutation |
| In Scope | `docs/diary/diary.html`, `docs/diary/diary.js`, smoke helpers, and minimal CSS only if required and documented; assess current absence/presence of drag/drop/resize affordances |
| Out of Scope | Backend route/schema changes, taskpane, Command Centre, Gemini, Resource Administration, Waiting Room layout, recurrence, broad visual redesign |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, `npm run validate-all`, smoke-mode proposal checks, and Ariadne Chrome/CDP checks where feasible |
| Status | Integrated with Ariadne hotfix |

### Workstream S26-C - Ariadne Integration and Review

| Item | Value |
|---|---|
| Owner | Codex/Ariadne |
| Branch | `master` integration worktree |
| Role | orchestrator |
| Goal | Review Sprint 26 plans together, release implementation only after plan approval, inspect diffs, run feasible verification, integrate, close out, push, realign, audit, and notify Yuri |
| In Scope | `poll --fetch`, plan/review inspection, focused backend/frontend checks, Chrome/CDP/live diary smoke where relevant, bounded safe repairs |
| Out of Scope | Acting as proof of a separate Codex worker submission or bypassing worker plan gates |
| Verification | `poll --fetch`, exact diff review, focused tests, browser/Chrome checks if runtime UI changes land, `git diff --check` |
| Status | Closeout in progress |

## Sprint 25: Status/Waiting-Area Proposal Retrofit

| Item | Value |
|---|---|
| Programme | Phase 2 Programme 2B - Safe Appointment Mutation Workbench |
| Status | Integrated, pushed, mirrored, audited, and deployed v86 observed |
| Launch Gate | Complete; Claude and Antigravity plans accepted and implementation released with `complete sprint task` |
| Integration Gate | Complete |
| Theme | Bring receptionist-facing status, check-in, and waiting-area changes under the same proposal-first safety rail as create/edit |

### Workstream S25-A - Backend Status/Waiting-Area Proposal Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-status-waiting-area-proposal-contract.md` |
| Goal | Plan and then extend appointment proposal contracts so status and waiting-area mutations can be preflighted before any write |
| In Scope | Backend appointment proposal schemas/routes/tests; deterministic block/warning/allow responses; practice/location/resource safety; no-write proposal behavior |
| Out of Scope | Diary frontend implementation, drag/drop/resize, recurrence, taskpane/Command Centre/Gemini, Resource Administration UI, patient duplicate workflow |
| Verification | Plan packet first; after approval focused appointment status/waiting-area/proposal pytest checks, import/check_backend as needed, and proof that proposal calls do not mutate appointments |
| Status | Integrated |

### Workstream S25-B - Diary Status/Waiting-Area Proposal Flow

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-status-waiting-area-proposal-flow.md` |
| Goal | Plan and then route diary status/check-in/waiting-area changes through proposal preflight before mutation, matching the create/edit Confirm & Save pattern |
| In Scope | `docs/diary/diary.{html,css,js}`, status controls, waiting-room/check-in affordances, proposal handling, smoke/live-test helpers, cache-busting |
| Out of Scope | Backend routes/models/tests/migrations, taskpane/Command Centre/Gemini, drag/drop/resize, recurrence, Resource Administration, patient duplicate review, broad visual redesign |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, smoke-mode allowed/blocked/warning/reset/API-failure checks, and Ariadne live Chrome/CDP checks after integration |
| Status | Integrated |

### Workstream S25-C - Ariadne Integration and Review

| Item | Value |
|---|---|
| Owner | Codex/Ariadne |
| Role | orchestrator |
| Branch | `master` only for orchestration docs and final integration |
| Goal | Review plans together, ensure backend/UI proposal semantics match, run all feasible tool-enabled tests including live browser checks, and leave only genuine Yuri-only checks if any |
| In Scope | Plan review, polling, integration sequencing, bounded repairs, closeout/user-test summary, next-sprint recommendation |
| Out of Scope | Acting as proof of a separate Codex worker submission or bypassing worker plan gates |
| Verification | `poll --fetch`, plan/review inspection, focused backend/frontend checks, Chrome/CDP/live diary smoke where relevant, `git diff --check` |
| Status | Integrated |

## Sprint 24: Appointment Edit Proposal Flow

| Item | Value |
|---|---|
| Programme | Phase 2 Programme 2B - Safe Appointment Mutation Workbench |
| Status | Integrated, pushed, mirrored, audited, and Ariadne live Chrome/CDP smoke passed |
| Launch Gate | Complete; plans accepted and implementation released with `complete sprint task` |
| Integration Gate | Complete |
| Theme | Route receptionist-facing appointment edit/reschedule through the formal non-mutating proposal layer before writing changes |

### Workstream S24-A - Backend Edit Proposal Contract Hardening

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-edit-proposal-contract-hardening.md` |
| Goal | Plan and then harden the backend `POST /appointments/proposals/update/{appointment_id}` contract only where needed for safe diary edit/reschedule preflight |
| In Scope | `app/routers/appointments.py`, `app/schemas/appointments.py`, focused update-proposal and adjacent appointment update tests, contract notes if needed |
| Out of Scope | Diary frontend implementation, taskpane/Command Centre, patient demographics, resource admin, migrations unless the plan proves a schema issue, Bernie runtime |
| Verification | Plan packet first; after approval `scripts/check_backend.ps1`, `tests/test_appointment_update_proposal.py`, adjacent booking/break tests if touched, `git diff --check` |
| Status | Integrated locally |

### Workstream S24-B - Diary Edit Proposal UI Flow

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-edit-proposal-flow.md` |
| Goal | Plan and then make appointment edit/reschedule saves call the update proposal endpoint before the actual `PUT`, mirroring the existing create-proposal Confirm & Save flow |
| In Scope | `docs/diary/diary.{html,css,js}`, edit modal proposal call, safe/warning/blocked copy, Confirm & Save state reset, smoke-mode simulation, cache-bust |
| Out of Scope | Backend route/schema changes, create-proposal behaviour except shared helper reuse, taskpane/Command Centre, Waiting Room panel layout, Resource Administration, drag/drop/resize, Bernie runtime |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, `npm run validate-all`, smoke/browser notes for edit safe/warning/blocked flows where feasible, `git diff --check` |
| Status | Integrated locally |

### Workstream S24-C - Ariadne Integration and Review

| Item | Value |
|---|---|
| Owner | Codex/Ariadne |
| Role | orchestrator |
| Branch | `master` only for orchestration docs after worker plans are accepted or during closeout |
| Goal | Review proposal-contract and UI plans together, verify create/edit proposal compatibility, run feasible backend/frontend/browser checks, and produce detailed Yuri-only residual review steps if any |
| In Scope | Plan review, integration sequencing, bounded repairs, closeout/user-test summary, next-sprint recommendation |
| Out of Scope | Acting as proof of a separate Codex worker submission or bypassing worker plan gates |
| Verification | `poll --fetch`, plan/review inspection, backend/frontend checks, browser/Chrome checks if available, `git diff --check` |
| Status | Ariadne-owned |

## Sprint 23: Room Default Waiting-Area Invariant

| Item | Value |
|---|---|
| Status | Integrated locally with focused verification passing |
| Launch Gate | Complete; packets submitted by Claude and Antigravity; no Codex worker expected |
| Integration Gate | Complete; push, mirror realignment, audit, and live Pages v84 review pending |
| Theme | Ensure every active room has a valid default waiting area so reception/admin state stays coherent after room or waiting-area changes |

### Workstream S23-A - Backend Default Waiting-Area Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-room-default-waiting-area-contract.md` |
| Goal | Plan and then enforce a safe backend invariant that every active room has a valid active default waiting area where possible |
| In Scope | Room/WaitingArea backend models, schemas, resource-admin routes/services, seed/dev-data repair, migrations only if required, focused pytest coverage |
| Out of Scope | Diary frontend UI, taskpane/Command Centre, appointment booking/status semantics beyond preserving existing consumers, broad roster redesign |
| Verification | Plan packet first; after approval focused resource-admin/default-waiting-area pytest coverage, backend Tier-1 check, full pytest if shared fixtures are touched, `git diff --check` |
| Status | Integrated |

### Workstream S23-B - Resource Admin Default Waiting-Area UI

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-room-default-waiting-area-ui.md` |
| Goal | Plan and then make room default waiting areas visible/editable in Resource Administration without regressing existing room/waiting-area flows |
| In Scope | `docs/diary/diary.{html,css,js}`, source/deployed asset sync and cache-bust if needed, default/fallback UI messaging, smoke/browser checks |
| Out of Scope | Backend contract changes, migrations, taskpane/Command Centre, appointment booking/status UI, roster admin redesign, drag/drop/resize |
| Verification | Plan packet first; after approval JS syntax, `npm run validate-all`, local/deployed asset version checks, smoke/live browser checks, `git diff --check` |
| Status | Integrated |

### Workstream S23-C - Ariadne Integration and Review Harness

| Item | Value |
|---|---|
| Owner | Codex/Ariadne |
| Role | orchestrator |
| Branch | `master` only for orchestration docs after worker plans are accepted or during closeout |
| Goal | Review both plans for invariant/UI compatibility, then run all feasible backend/frontend/browser checks before asking Yuri for any residual user review |
| In Scope | Plan review, integration sequencing, bounded repairs, closeout/user-test summary, and next-sprint recommendation |
| Out of Scope | Acting as proof of a separate Codex worker submission or bypassing worker plan gates |
| Verification | `poll --fetch`, plan/review inspection, backend/frontend checks, browser/Chrome checks if runtime UI changes land, `git diff --check` |
| Status | Integrated, pushed, mirrored, audited, and closed |

## Sprint 22: Development Tooling Optimisation

| Item | Value |
|---|---|
| Status | Integrated locally with verification passing |
| Launch Gate | Complete |
| Integration Gate | Complete; push, mirror realignment, and audit pending |
| Theme | Improve EMR4's AI-assisted development feedback loops before the next product-growth sprint |

### Workstream S22-A - Backend Dev Loop Tooling

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-backend-dev-loop-tooling.md` |
| Goal | Plan and then improve backend development feedback loops so Ariadne and workers can run fast, reliable checks before residual user review |
| In Scope | Backend/dev-environment tooling, pytest/static-check ergonomics, startup verification, backend check-tier documentation, small scripts/config that reduce false starts |
| Out of Scope | Product behaviour, diary/taskpane UI, migrations, schema changes, WhatsApp production send behaviour, security alert dismissal, broad dependency upgrades |
| Verification | Plan packet first; after approval app import/startup check, proposed focused checks, `run_dev` or equivalent non-destructive probe where feasible, `git diff --check` |
| Status | Integrated |

### Workstream S22-B - Frontend Browser Dev Tooling

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-frontend-browser-dev-tooling.md` |
| Goal | Plan and then improve diary/taskpane frontend and browser-feedback loops so UI affordance regressions are caught by tools before Yuri is asked to test |
| In Scope | Diary/taskpane smoke commands, browser/check scripts, local/deployed asset version checks, npm script ergonomics, Antigravity/Gemini-assisted UI QA notes |
| Out of Scope | Product UI behaviour changes, visual redesign, backend API contracts, migrations, patient/clinical flows, production WhatsApp sending, forced broad dependency upgrades |
| Verification | Plan packet first; after approval JS/build/validate or smoke commands, local/deployed asset URL checks where feasible, `git diff --check`, browser/visual observations |
| Status | Integrated |

### Workstream S22-C - Ariadne Architecture and Tooling Harness

| Item | Value |
|---|---|
| Owner | Ariadne/orchestrator Codex |
| Role | orchestrator |
| Branch | `master` only for orchestration docs after worker plans are accepted or during closeout |
| Goal | Review Sprint 22 plans against the software-fundamentals architecture frame: shared design language, fast feedback loops, TDD-sized increments, deep-module boundaries, and residual user-test discipline |
| In Scope | Plan review, integration checklist, closeout wording, and next-sprint architecture/tooling recommendations |
| Out of Scope | Acting as proof of a separate Codex worker submission, production feature implementation, or bypassing worker plan gates |
| Verification | `poll --fetch`, plan/review inspection, feasible local/browser checks before closeout, `git diff --check` for orchestration updates |
| Status | Integrated |

## Sprint 20: Security Baseline

| Item | Value |
|---|---|
| Status | Integrated locally after plan-gated review |
| Launch Gate | Complete |
| Integration Gate | Complete; observe GitHub Actions after push |
| Theme | Add a small repeatable security baseline before deeper product work |

### Workstream S20-A - Python Security Baseline

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-python-security-baseline.md` |
| Goal | Add fast backend/Python dependency and static-analysis security checks |
| In Scope | Python security workflow/tooling notes, likely `pip-audit` and Bandit, deterministic commands Ariadne can rerun, plus Claude Code tool/plugin recommendations |
| Out of Scope | Runtime app behavior, migrations, diary/taskpane UI, Node/Office audit |
| Verification | New local security commands where feasible; YAML validation/diff checks; exact command output in completion notes |
| Status | Integrated |

### Workstream S20-B - Node Office Security Baseline

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-node-security-baseline.md` |
| Goal | Add repeatable Office add-in dependency audit and validation checks |
| In Scope | Node/Office audit workflow or metadata, `EMR4 Sidebar` package audit reproducibility, concise local command notes, plus Antigravity/Gemini tool/plugin recommendations |
| Out of Scope | Runtime frontend behavior, diary/taskpane asset changes, backend/Python security checks |
| Verification | `npm audit`/Office validation where feasible; `git diff --check`; exact command output in completion notes |
| Status | Integrated |

### Workstream S20-C - Security Review Harness

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/security-review-harness` |
| Task Packet | `orchestration/agent_inbox/codex/codex-security-review-harness.md` |
| Goal | Configure CodeQL/Dependabot coordination and create Ariadne's Sprint 20 security review checklist |
| In Scope | CodeQL/Dependabot config, `orchestration/security_baseline_review.md`, Codex Security review path, installed Codex tool/skill inventory |
| Out of Scope | Production code, migrations, runtime frontend/backend behavior, duplicating Claude/Antigravity workflows |
| Verification | `git diff --check`, YAML validation where feasible, documented Codex Security scan/review path |
| Status | Integrated |

## Sprint 21: Security Alert Triage and Focused Remediation

| Item | Value |
|---|---|
| Status | Integrated locally with verification passing |
| Launch Gate | Complete |
| Integration Gate | Complete; Codex worker stood down after repeated local tooling blockers and Ariadne completed the triage harness |
| Theme | Turn Sprint 20 security signals into bounded fixes and an Ariadne-facing alert triage harness |

### Workstream S21-A - Consultation CodeQL Fixes

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-consultation-codeql-fixes.md` |
| Goal | Address high/medium CodeQL findings in `app/routers/consultation.py` without changing successful API behaviour |
| In Scope | Path cleanup validation, sensitive-content logging reduction, bounded error responses, focused tests if adjacent |
| Out of Scope | UI, diary/taskpane assets, migrations, RBAC redesign, Gemini prompt redesign |
| Verification | Focused py_compile/pytest/Bandit commands recorded in Completion Notes |
| Status | Integrated |

### Workstream S21-B - Node Security Workflow Triage

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-node-security-workflow-triage.md` |
| Goal | Improve Node/Office security workflow signal quality while preserving a clean production audit gate |
| In Scope | `.github/workflows/node-security.yml`, `EMR4 Sidebar/package*.json` only if the plan proves a safe metadata/update change |
| Out of Scope | Runtime diary/taskpane UI, backend, forced major build-tool upgrades |
| Verification | `npm run validate`, `npm audit --omit=dev`, and non-blocking full `npm audit` where feasible |
| Status | Integrated |

### Workstream S21-C - Security Alert Triage Harness

| Item | Value |
|---|---|
| Owner | Codex worker/security-manager |
| Branch | `codex/security-alert-triage` |
| Task Packet | `orchestration/agent_inbox/codex/codex-security-alert-triage-harness.md` |
| Goal | Inventory GitHub security alerts with `gh`, classify fix-now/defer/noise, and preserve a redacted Ariadne review harness |
| In Scope | `orchestration/security_alert_triage.md`, read-only `gh` security queries, links to existing security baseline notes |
| Out of Scope | Production code changes, alert dismissal, cloud/key rotation, master/handoff integration |
| Verification | `gh auth status`, CodeQL/secret/Dependabot/workflow queries, secret-safe report review |
| Status | Superseded by Ariadne-owned `orchestration/security_alert_triage.md` |

### Deferred Product Follow-Up

- Future resource-admin work should ensure every active room always has a
  default waiting area. A sensible default is the active waiting area with
  display order `0` when no room-specific default has been selected.

## Sprint 19: Resource Admin Foundations

| Item | Value |
|---|---|
| Sprint Goal | Add the first safe admin path for physical rooms and waiting areas so reception/admin can maintain Phase 2 diary resources without confusing locations, rooms, diary views, waiting areas, appointment status, or patient identity |
| Dispatch Mode | Plan-gated parallel sprint |
| Start State | `master`, `handoff/current`, and durable worker mirrors aligned at `d78659a` after Sprint 18 closeout |
| User Review Dependency | None before planning; implementation plans must be reviewed before coding |
| Integration Rule | Do not push Sprint 19 work to `master` until Claude, Antigravity, and any Codex worker have submitted or been explicitly stood down |
| Status | Integrated; pending push/deploy and user review |

### Workstream A - Backend Room and Waiting-Area Admin Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-diary-resource-admin-contract.md` |
| Goal | Plan, then after approval implement the smallest role-gated backend admin contract for rooms and waiting areas |
| In Scope | `app/schemas/diary.py`, `app/routers/diary.py`, focused `tests/test_diary_resource_admin.py`; `GET /diary/rooms`; create/update/archive for `Room` and `WaitingArea`; Admin/PracticeOwner RBAC; practice and location scoping; archive semantics; room `default_waiting_area_id` validation |
| Out of Scope | Diary frontend, roster writes, diary template editing, appointment mutation semantics, migrations unless the approved plan proves one is needed, full practice admin UI, patient merge, Bernie runtime, audit-log platform |
| Verification | Plan packet first; after approval backend py_compile plus focused resource-admin tests and adjacent `test_location_scoped_diary.py`, `test_diary_roster.py`, and `test_waiting_area_contract.py` coverage |
| Plan Gate | Required before coding |
| Merge Criteria | Admin writes cannot leak cross-practice data; inactive/archive preserves historical references; room defaults cannot point at cross-location/cross-practice waiting areas; existing diary read endpoints keep working |
| Dissent / Risks | Display-order uniqueness and archive behaviour may expose existing dev-data assumptions; do not introduce non-person bookable resources in this slice |
| Status | Integrated |

### Workstream B - Diary Resource Admin First Slice

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-resource-admin-ui.md` |
| Goal | Plan, then after approval add a restrained diary-admin surface for rooms and waiting areas using the Workstream A API contract |
| In Scope | `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`; active-location context; list/create/edit/archive controls for rooms and waiting areas; default waiting-area selection for rooms; clear success/failure feedback; cache bust if assets change |
| Out of Scope | Backend changes, roster editor, diary template editor, appointment create/edit/status logic, main diary appointment geometry, Waiting Room card layout, taskpane, Command Centre, duplicate merge, Bernie runtime |
| Verification | Plan packet first; after approval `node --check docs\diary\diary.js`, `git diff --check`, and manual visual notes for one-location and multi-location resource admin flows |
| Plan Gate | Required before coding |
| Merge Criteria | One-location diary remains uncluttered; multi-location context remains explicit; admin controls do not mutate appointments or waiting-room attendance state; API errors are visible and recoverable |
| Dissent / Risks | This depends on Workstream A's final route/payload shape; if backend scope changes, UI should stop at a plan or adapter shell rather than guessing |
| Status | Integrated |

### Workstream C - Resource Admin Review Harness

| Item | Value |
|---|---|
| Owner | Codex worker or orchestrator |
| Branch | Unique `codex/<short-task-name>` worker branch, or direct orchestrator docs if no worker is launched |
| Task Packet | `orchestration/agent_inbox/codex/codex-resource-admin-review-harness.md` |
| Goal | Prepare the integration and user-review harness for resource admin without duplicating backend or frontend implementation scopes |
| In Scope | Orchestration review docs, API spot-check snippets, user review checklist, closeout scaffolding, and vocabulary guardrails tying back to `orchestration/resource_admin_bernie_tool_design.md` |
| Out of Scope | Production backend/frontend code, migrations, taskpane, Command Centre, appointment mutations, patient merge, autonomous Bernie runtime |
| Verification | Plan packet first if launched as a worker; after approval `git diff --check` and snippet sanity review against the final submitted backend API |
| Plan Gate | Required before coding if launched as worker |
| Merge Criteria | Review harness names the exact surfaces to test and not test; keeps room/resource/waiting-area/location language separate; preserves agent dissent/risks from submitted plans |
| Dissent / Risks | If Codex keeps this direct, no external worker handin is needed for Workstream C; if launched as a subagent, use normal submit and include it in the integration gate |
| Status | Integrated |

## Sprint 18: Patient-Admin Safety and Duplicate Visibility

| Item | Value |
|---|---|
| Sprint Goal | Make duplicate patient records visible and safer to reason about, while tightening the taskpane patient search/save feedback that led to confusion during review |
| Dispatch Mode | Plan-gated parallel sprint |
| Start State | `master`, `handoff/current`, and durable worker mirrors aligned at Sprint 17 closeout |
| User Review Dependency | None before planning; implementation plans must be reviewed before coding |
| Integration Rule | Do not push sprint work to `master` until Claude, Antigravity, and the Codex worker have submitted or been explicitly stood down |
| Status | Integrated, deployed, and user-reviewed; see `orchestration/sprint_closeout.md` |

### Workstream A — Backend Duplicate Review Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-patient-duplicate-review-api.md` |
| Goal | Plan, then after approval implement a read-only backend duplicate-patient review contract |
| In Scope | Patient duplicate review schemas/router/tests; same-name+DOB groups; Medicare+IRN and IHI strong-identifier groups; reference counts where practical; practice isolation |
| Out of Scope | Frontend UI, patient merge/delete mutation, manual DB deletion, production data migrations |
| Verification | Plan packet first; after approval focused pytest for duplicate review API and relevant patient tests |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream B — Taskpane Patient Search and Alert Clarity

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-taskpane-patient-search-and-alerts.md` |
| Goal | Plan, then after approval improve full-name patient search and make patient-details save failures obvious without scrolling |
| In Scope | Taskpane HTML/JS/CSS only; cache bust; patient search and patient-details save feedback |
| Out of Scope | Backend changes, diary changes, Command Centre redesign, patient merge/delete implementation |
| Verification | Plan packet first; after approval JS syntax check plus manual taskpane verification notes |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream C — Dev Duplicate Audit Helper

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | unique `codex/<short-task-name>` worker branch |
| Task Packet | `orchestration/agent_inbox/codex/codex-dev-data-duplicate-audit-tool.md` |
| Goal | Plan, then after approval add a read-only developer helper for inspecting duplicate patients and references |
| In Scope | `scripts/` helper or equivalent command path; dummy-guide update; read-only output by default |
| Out of Scope | Automatic deletion, patient merge mutation, production admin UI, app runtime behaviour changes |
| Verification | Plan packet first; after approval run helper against dev DB if available and confirm safe failure without DB settings |
| Plan Gate | Required before coding |
| Status | Integrated |

## Sprint 17: Command/Proposal Workflow Retrofit

| Item | Value |
|---|---|
| Status | Dispatched; plan gate pending |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Implementation Gate | Pending worker plans and Codex approval |
| Theme | Retrofit high-risk receptionist workflows onto the formal command/proposal layer before adding Bernie runtime |

### Workstream AX - Appointment Update Proposal Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-update-proposal-contract.md` |
| Goal | Plan, then after approval implement backend proposal contract(s) for editing, rescheduling, cancelling, and/or status-changing an existing appointment without mutating until staff confirmation |
| In Scope | Appointment schemas/router/tests; non-mutating proposal endpoint(s); typed command payloads; conflict, break, provisional-identity, terminal/cancellation, and waiting-area/status warnings if touched |
| Out of Scope | Diary frontend, taskpane, Command Centre, Bernie runtime, migrations unless necessary, patient demographics, room/location admin, drag/drop/resize, SMS/reminder confirmation, billing/finalisation |
| Verification | Plan packet first; after approval backend py_compile, focused pytest, adjacent booking/status/break tests, `git diff --check` |
| Plan Gate | Required before coding |
| Status | Dispatched |

### Workstream AY - Diary Create Proposal Flow

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-create-proposal-flow.md` |
| Goal | Plan, then after approval make the diary booking modal call `POST /api/v1/appointments/proposals/create` before writing a new booking |
| In Scope | `docs/diary/diary.{html,css,js}`; cache-bust if diary assets change; booking-create modal proposal, block, warning, and confirmation flow only |
| Out of Scope | Backend route/schema changes, taskpane, Command Centre, Waiting Room panel layout, main diary appointment geometry, location selector redesign, patient demographics, Bernie runtime, drag/drop/resize |
| Verification | Plan packet first; after approval `node --check docs\diary\diary.js`, `git diff --check`, visual/manual notes for safe create, conflict block, break warning, and provisional warning if supported |
| Plan Gate | Required before coding |
| Status | Dispatched |

### Workstream AZ - Command Proposal Review Harness

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/command-proposal-review-harness` |
| Task Packet | `orchestration/agent_inbox/codex/codex-command-proposal-review-harness.md` |
| Goal | Plan, then after approval create the review harness and developer-facing API snippets for the formal command/proposal layer |
| In Scope | Orchestration docs, sprint closeout/review harness updates, developer guide snippets where useful, PowerShell/API examples for proposal safe/warning/blocked paths |
| Out of Scope | Production backend/frontend changes, migrations, diary UI, taskpane, Command Centre, Bernie runtime, modifying Claude/Antigravity packets after dispatch |
| Verification | Plan packet first; after approval `git diff --check` plus executable snippet/schema verification if practical |
| Plan Gate | Required before coding |
| Status | Dispatched |

## Sprint 16: Location-Aware Diary Foundations

| Item | Value |
|---|---|
| Status | Integrated |
| Launch Gate | Complete |
| Implementation Gate | Complete |
| Theme | Make the diary/resource model explicitly location-aware while separating physical sites from diary screen/page views |

### Workstream AU - Location-Scoped Diary Backend Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-location-scoped-diary-contract.md` |
| Goal | Plan, then after approval implement, the smallest backend changes needed so diary templates, rooms, waiting areas, rosters, and appointments do not assume one physical location per practice |
| In Scope | Backend models/schemas/routers/tests around `PracticeLocation`, `Room`, `WaitingArea`, `DiaryTemplate`, `DiaryRoster`, `Appointment.location_id`, seed/test data, migrations only if needed |
| Out of Scope | Diary frontend, taskpane, Command Centre, full practice/location admin UI, drag/drop/resize, online booking portal, Bernie runtime |
| Verification | Plan packet first; after approval, focused location/diary/appointment pytest, backend py_compile, migration check if changed, `git diff --check` |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AV - Diary Location Selector and View Boundary

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-location-selector-view-boundary.md` |
| Goal | Plan, then after approval implement, a restrained diary UI path for choosing/indicating the active physical location and preserving the distinction from diary page/column-group views |
| In Scope | `docs/diary/diary.{html,css,js}` and cache-bust; frontend consumption of existing/new location-aware diary APIs if available; no broad redesign |
| Out of Scope | Backend schema/routes/tests, taskpane, Command Centre, drag/drop/resize, full admin UI, Bernie runtime, appointment-card geometry changes |
| Verification | Plan packet first; after approval, `node --check docs\diary\diary.js`, `git diff --check`, live/smoke visual notes for one-location fallback and multi-location affordance |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AW - Location and Diary View Design Harness

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/location-diary-view-design-harness` |
| Task Packet | `orchestration/agent_inbox/codex/codex-location-diary-view-design-harness.md` |
| Goal | Plan, then after approval prepare the design guardrails, user-review checklist, and future Bernie tool vocabulary for practice vs location vs room/resource vs waiting area vs diary page/view group |
| In Scope | Orchestration docs, implementation-plan notes, review harness, API/user-test snippets if useful |
| Out of Scope | Production backend/frontend implementation, migrations, taskpane/Command Centre, autonomous Bernie runtime, drag/drop/resize |
| Verification | Plan packet first; after approval, `git diff --check` |
| Plan Gate | Required before coding |
| Status | Integrated |

## Sprint 15: Plan-Gated Waiting Room Check-In Operations

| Item | Value |
|---|---|
| Status | Integrated |
| Launch Gate | Complete |
| Implementation Gate | Complete |
| Theme | Make Waiting Room check-in operational while preserving room/resource/waiting-area terminology and avoiding diary-grid churn |

### Workstream AR - Waiting Area Check-In Defaults

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-waiting-area-checkin-defaults.md` |
| Goal | Plan, then after approval implement, backend defaults/clearing semantics for waiting-area assignment during check-in/status transitions |
| In Scope | Appointment status/update semantics, waiting-area assignment/defaulting/clearing tests, practice scoping, inactive/cross-practice guards, terminal status policy |
| Out of Scope | Diary frontend, taskpane, room/admin UI, Bernie runtime, SMS/email/voice reminder confirmation, billing/finalisation locking, drag/drop/resize |
| Verification | Plan packet first; after approval, focused pytest, backend py_compile, `git diff --check` |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AS - Diary Check-In Waiting-Area UI

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-checkin-waiting-area-ui.md` |
| Goal | Plan, then after approval implement, Waiting Room side-panel check-in with visible/default waiting-area assignment and denser Expected Today display |
| In Scope | `docs/diary/diary.{html,css,js}` and diary cache-bust; Waiting Room side-panel only |
| Out of Scope | Backend routes/models/tests/migrations, taskpane, Command Centre, booking modal semantics beyond existing status/check-in API, main diary grid appointment positioning, drag/drop/resize, Bernie runtime |
| Verification | Plan packet first; after approval, `node --check docs\diary\diary.js`, `git diff --check`, visual acceptance notes |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AT - Waiting Room Review Harness

| Item | Value |
|---|---|
| Owner | Codex |
| Branch | `codex/current` or disposable Codex worker branch |
| Task Packet | `orchestration/agent_inbox/codex/codex-waiting-room-review-harness.md` |
| Goal | Plan, then after approval prepare review scripts/checklists and guardrails for room-to-waiting-area defaults and Waiting Room user review |
| In Scope | Orchestration docs, sprint closeout draft/checklist, PowerShell API snippets, design guardrails |
| Out of Scope | Production backend/frontend code, migrations, taskpane/Command Centre, Bernie runtime, drag/drop/resize, duplicating Claude/Antigravity scopes |
| Verification | Plan packet first; after approval, `git diff --check` |
| Plan Gate | Required before coding |
| Status | Integrated |

## Sprint 14: Plan-Gated Receptionist Workflow Foundations

| Item | Value |
|---|---|
| Status | Integrated |
| Launch Gate | Complete |
| Implementation Gate | Complete |
| Theme | Clarify receptionist workflow semantics before further diary/Waiting Room coding or Bernie tools |

### Workstream AO - Waiting Area Check-In Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-waiting-area-checkin-contract.md` |
| Goal | Plan, then after approval implement, the backend contract for assigning waiting areas during check-in and status transitions |
| In Scope | Appointment status/update semantics, waiting-area assignment, practice scoping, patient identity/status separation, focused backend tests |
| Out of Scope | Diary frontend, taskpane, room admin UI, Bernie implementation, SMS/reminder confirmation, billing/finalisation locking |
| Verification | Plan packet first; after approval, focused pytest and backend py_compile |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AP - Diary Waiting Room UX Clarity

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-waiting-room-ux-clarity.md` |
| Goal | Plan, then after approval implement, Waiting Room side-panel clarity improvements for receptionist workflow |
| In Scope | `docs/diary/` Waiting Room panel only: area tabs, panel counts, card density/stacking inside the side panel, action wording |
| Out of Scope | Diary grid appointment positioning, booking slot geometry, booking modal semantics, backend, taskpane, drag/drop/resize, Bernie |
| Verification | Plan packet first; after approval, `node --check docs\diary\diary.js`, `git diff --check`, visual acceptance notes |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AQ - Resource Admin and Bernie Tool Design

| Item | Value |
|---|---|
| Owner | Codex |
| Branch | `codex/resource-admin-bernie-tool-design` |
| Task Packet | `orchestration/agent_inbox/codex/codex-resource-admin-bernie-tool-design.md` |
| Goal | Plan the resource/admin foundation and safe Bernie tool boundaries needed before supervised receptionist assistance |
| In Scope | Design docs, implementation-plan notes, future endpoint/tool boundaries, room/resource/waiting-area terminology |
| Out of Scope | Production UI, autonomous Bernie actions, LLM agent runtime, schema migration unless plan-approved, drag/drop/resize |
| Verification | Plan packet first; after approval, docs diff check or explicit code checks if implementation is approved |
| Plan Gate | Required before coding |
| Status | Integrated |

## Sprint 13: Waiting Areas, Patient Editing, and Bernie Prerequisites

| Item | Value |
|---|---|
| Status | Integrated |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Build the room/waiting-area and patient-edit foundations Bernie will need later, without starting autonomous copilot work yet |

### Workstream AL - Waiting Area Resource Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-waiting-area-resource-contract.md` |
| Goal | Add the minimal backend contract for named physical waiting areas linked to rooms/resources and waiting-room filtering/grouping |
| In Scope | `app/models/tenancy.py`, `app/models/diary.py`, `app/schemas/diary.py`, `app/schemas/appointments.py`, `app/routers/diary.py`, `app/routers/appointments.py`, Alembic migration if needed, `seed.py`, focused tests, plus `tests/conftest.py` only for pgvector test fixture hardening |
| Out of Scope | Diary frontend, taskpane/Command Centre, Bernie implementation, patient-edit UI, drag/drop/resize, SMS, billing/completion, ADHA/IHI live integration |
| Verification | Focused waiting-room/diary/appointment pytest, fresh-DB pgvector fixture check if `tests/conftest.py` changes, migration checks if needed, backend compile check, `git diff --check` |
| Status | Queued |

### Workstream AM - Diary Waiting Area Tabs

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-waiting-area-tabs.md` |
| Goal | Make the diary patient-flow panel support physical waiting-area tabs/groups while preserving simple fallback behaviour |
| In Scope | `docs/diary/diary.{html,css,js}` and diary cache-bust only |
| Out of Scope | Backend routes/models/tests/migrations, taskpane/Command Centre, Bernie implementation, patient edit details UI, drag/drop/resize, SMS, billing/completion |
| Verification | `node --check docs\diary\diary.js`, `git diff --check`, live/smoke checks for no-area fallback, multiple areas, linked/provisional action, narrow layout, and status changes |
| Status | Queued |

### Workstream AN - Patient Edit Details Foundation

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/patient-edit-details-foundation` |
| Task Packet | `orchestration/agent_inbox/codex/codex-patient-edit-details-foundation.md` |
| Goal | Add safe patient-detail editing for the loaded patient while preserving hard duplicate protections |
| In Scope | `app/routers/patients.py`, `app/schemas/patients.py`, `tests/test_patients.py`, `EMR4 Sidebar/src/taskpane/taskpane.{html,css,js}`, synced `docs/taskpane/*`, taskpane cache-bust if assets change |
| Out of Scope | Diary frontend, waiting-area backend contract, appointment routes/models, Command Centre clinical coding, generated Word document rewrite, OneDrive import tooling, ADHA/IHI live verification, OCR, Bernie implementation |
| Verification | Focused patient pytest, taskpane JS syntax checks on source/docs, `sync_taskpane.py` if source changes, `git diff --check`, edit/cancel/save/duplicate-block smoke notes |
| Status | Queued |

## Sprint 12: Provisional Booking Link and State Model

| Item | Value |
|---|---|
| Status | Integrated locally |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Finish the practical provisional-to-linked-patient booking workflow while clarifying appointment state and waiting-area semantics before drag/drop/resize |

### Workstream AI - Provisional Booking Link Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-provisional-link-contract.md` |
| Goal | Finish the backend contract for linking provisional appointments to existing patient records while preserving patient identity/linkage versus attendance status separation |
| In Scope | Appointment/diary backend models, schemas, routers, focused tests, migration only if needed, seed/test helpers only if needed |
| Out of Scope | Diary frontend, taskpane/Command Centre, drag/drop/resize, SMS confirmation, billing/completion workflow, full waiting-area model, real ADHA/IHI integration |
| Verification | Focused appointment patient-link/create-edit/status/conflict tests, touched diary break/roster tests, migration check if needed, `git diff --check` |
| Status | Integrated |

### Workstream AJ - Diary Provisional Patient Linking

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-link-provisional-patient.md` |
| Goal | Add diary UI to link a provisional/free-text booking to an existing patient record and warn before saving bookings that cross break blocks |
| In Scope | `docs/diary/diary.{html,css,js}` and diary cache-bust if assets change |
| Out of Scope | Backend routes/models/tests/migrations, taskpane/Command Centre, drag/drop/resize, SMS workflow, billing/completion workflow, full waiting-area model |
| Verification | `node --check docs\diary\diary.js`, `git diff --check`, smoke/live checks for provisional create, link, status warning, break-crossing warning, narrow layout, and failures |
| Status | Integrated |

### Workstream AK - Appointment State and Waiting-Area Model

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/appointment-state-waiting-area-model` |
| Task Packet | `orchestration/agent_inbox/codex/codex-appointment-state-and-waiting-area-model.md` |
| Goal | Produce the design note and review harness for appointment identity/status/waiting-area semantics before drag/drop/resize |
| In Scope | Orchestration/design docs, implementation-plan notes if appropriate, Sprint 12 review checklist, exact PowerShell API snippets for user review |
| Out of Scope | Production backend/frontend implementation, migrations, diary/taskpane feature work, Gemini/AI, billing implementation, real ADHA/IHI integration |
| Verification | `git diff --check`; focused syntax/check only if any helper script is added |
| Status | Integrated |

## Sprint 11: Patient-Link Semantics and New Patient Safety

| Item | Value |
|---|---|
| Status | Integrated locally |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Split patient identity/linkage from appointment attendance while hardening New Patient duplicate handling |

### Workstream AF - Appointment Patient-Link Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-patient-link-contract.md` |
| Goal | Make the backend distinguish linked patient records from provisional free-text diary names, without treating Confirmed as an attendance state |
| In Scope | Appointment model/schema/router/tests, migration if needed, focused appointment create/edit/status/waiting-room/conflict tests |
| Out of Scope | Diary frontend, taskpane/Command Centre UI, drag/drop/resize, SMS reminder confirmation, billing/completion guard design beyond noting risks |
| Verification | Focused appointment pytest, migration check if a migration is added, `git diff --check` |
| Status | Integrated |

### Workstream AG - Diary Patient-Link UI Semantics

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-patient-link-ui.md` |
| Goal | Make linked versus provisional patient identity legible in the diary and remove Confirmed from routine attendance-status treatment |
| In Scope | `docs/diary/diary.{html,css,js}` and cache-bust if assets change |
| Out of Scope | Backend routes/models/tests/migrations, taskpane/Command Centre, drag/drop/resize, SMS reminder workflow, billing/completion workflow |
| Verification | `node --check docs\diary\diary.js`, live/smoke visual checks where possible, `git diff --check` |
| Status | Integrated |

### Workstream AH - New Patient Duplicate Workflow

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/new-patient-duplicate-workflow` |
| Task Packet | `orchestration/agent_inbox/codex/codex-new-patient-duplicate-workflow.md` |
| Goal | Harden New Patient creation with cancel/escape/success paths and duplicate-candidate warning before record/file creation |
| In Scope | `EMR4 Sidebar/src/taskpane/taskpane.{html,css,js}`, mirrored `docs/taskpane/*` via `sync_taskpane.py`, focused checks/tests if available |
| Out of Scope | Diary frontend, appointment patient-link backend, Command Centre clinical coding, OneDrive import tooling, ADHA/IHI live integration, OCR |
| Verification | `node --check` on taskpane JS source and docs copy, `git diff --check`, `sync_taskpane.py` if source changes, focused patient tests if backend is touched |
| Status | Integrated |

## Sprint 10: Nurse Bookability and Patient Identity Foundation

| Item | Value |
|---|---|
| Status | Integrated locally |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Make Nurse/Room 2 deliberately bookable via a practitioner-backed resource while starting the safer patient-identity foundation in a separate lane |

### Workstream AC - Nurse Practitioner Dev-Data Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-nurse-practitioner-dev-data-contract.md` |
| Goal | Make Room 2/Nurse deliberately bookable by representing Nurse as a real practitioner/staff resource in dev data and tests |
| In Scope | `seed.py`, focused diary roster/template tests, focused appointment create/edit/slots tests, minimal backend fixes only if the current contract blocks safe nurse representation |
| Out of Scope | Diary frontend, taskpane/Command Centre, patient identity/duplicate work, waiting-area UI, room/resource-only bookings without `practitioner_id`, drag/drop/resize |
| Verification | Focused diary roster/template and appointment/slots pytest suites plus `git diff --check` |
| Status | Integrated |

### Workstream AD - Diary Nurse Bookability Affordance

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-nurse-bookability-affordance.md` |
| Goal | Make practitioner-backed Nurse/Room 2 columns clearly bookable while label-only/non-practitioner columns remain visibly non-bookable |
| In Scope | `docs/diary/diary.{html,css,js}` and cache-bust bump |
| Out of Scope | Backend routes/models/tests/migrations, taskpane/Command Centre, patient identity/duplicate work, waiting-area data model, drag/drop/resize |
| Verification | `node --check docs\diary\diary.js`, live/smoke/narrow visual checks, `git diff --check` |
| Status | Integrated |

### Workstream AE - Patient Identity Duplicate Foundation

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/patient-identity-duplicates` |
| Task Packet | `orchestration/agent_inbox/codex/codex-patient-identity-duplicates.md` |
| Goal | Start the backend foundation for safer patient creation with focused tests and minimal API/model support for identity fields and duplicate-candidate handling |
| In Scope | `app/models/patients.py`, `app/schemas/patients.py`, `app/routers/patients.py`, patient tests, Alembic migration if needed, `create_patient_file.py` only for minimal generated-file mapping |
| Out of Scope | Diary frontend, appointment/roster/nurse booking work, taskpane UI implementation, OneDrive import tooling, ADHA/IHI service integration, Medicare claiming integration |
| Verification | Focused patient pytest, migration check if needed, `git diff --check`, generator smoke if touched |
| Status | Integrated |

## Sprint 9: Patient Flow and Patient Entry Hardening

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Harden the practical patient-flow layer before drag/drop/resize and roster-admin work |

### Workstream Z - Booking Patient-Flow Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-booking-patient-flow-contract.md` |
| Goal | Strengthen appointment update/status/waiting-room contract for the next diary operations layer |
| In Scope | Appointment schemas/router/models as needed, focused appointment create/edit/status/waiting-room/slots tests |
| Out of Scope | Diary frontend, drag/drop/resize UI, roster admin UI, taskpane/Command Centre/Gemini, patient search/New Patient work |
| Verification | Focused appointment pytest suites plus any new patient-flow contract tests |
| Status | Integrated |

### Workstream AA - Diary Patient-Flow Workbench

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-patient-flow-workbench.md` |
| Goal | Improve the receptionist-facing diary patient-flow surface while preserving booking create/edit behaviour |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend routes/models/tests/migrations, drag/drop, resize handles, roster admin UI, online booking portal, patient import tooling |
| Verification | JS syntax plus live/smoke/narrow create/edit/status/patient-flow visual checks |
| Status | Integrated |

### Workstream AB - Patient Search and New Patient Hardening

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/patient-search-new-patient-hardening` |
| Task Packet | `orchestration/agent_inbox/codex/codex-patient-search-new-patient-hardening.md` |
| Goal | Add meaningful tests and minimal fixes for DB-backed patient search and New Patient creation |
| In Scope | Focused patient tests, `app/routers/patients.py`, `app/schemas/patients.py`, `create_patient_file.py`, seed/test helpers only as needed |
| Out of Scope | OneDrive import tools, diary frontend, appointment/status routes, taskpane UI, Command Centre, Gemini/AI behaviour |
| Verification | Focused patient pytest suite, `git diff --check`, generator smoke test if touched |
| Status | Integrated |

## Sprint 8: Booking Create/Edit First Slice

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Add a practical create/edit booking path without starting drag/drop/resize |

### Workstream W - Booking Create/Edit Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-booking-create-edit-contract.md` |
| Goal | Harden the backend appointment create/edit contract for diary use |
| In Scope | Appointment models/schemas/router, focused create/edit/conflict/auth/scope tests, minimal seed/test helper changes if needed |
| Out of Scope | Diary frontend, drag/drop/resize UI, roster admin UI, waiting-room display app, taskpane/Command Centre/Gemini, online booking portal |
| Verification | Focused appointment conflict/status/waiting-room/slots pytest suites plus any new booking create/edit tests |
| Status | Integrated |

### Workstream X - Diary Create/Edit Modal

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-create-edit-modal.md` |
| Goal | Add restrained diary create/edit controls using the existing appointments API |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend routes/models/tests, drag/drop/resize, recurring appointments, roster admin UI, waiting-room display app, taskpane/Command Centre/Gemini, online booking portal |
| Verification | JS syntax plus live/smoke/narrow create/edit/failure visual checks |
| Status | Integrated |

### Workstream Y - Booking Create/Edit Review Plan

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/booking-create-edit-review-plan` |
| Task Packet | `orchestration/agent_inbox/codex/codex-booking-create-edit-review-plan.md` |
| Goal | Prepare integration and user-review checklist for the create/edit booking slice |
| In Scope | Orchestration/review documentation, including exact PowerShell API snippets for user review |
| Out of Scope | Production backend/frontend code, migrations, drag/drop/resize, roster admin UI, taskpane/Command Centre/Gemini |
| Verification | `git diff --check` |
| Status | Integrated |

## Sprint 7: Controlled Status Mutation

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Add safe receptionist-facing appointment status changes before booking create/edit/drag/drop work |

### Workstream T - Appointment Status Mutation Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-status-mutation-contract.md` |
| Goal | Harden backend status mutation behavior and regression coverage |
| In Scope | Appointment status router/schema/tests; minimal production fixes only if tests expose unsafe behavior |
| Out of Scope | Diary frontend, taskpane/Command Centre/Gemini, booking create/edit/drag/drop, roster admin UI |
| Verification | Focused appointment status/waiting-room/slots pytest suites |
| Status | Integrated |

### Workstream U - Diary Status Controls

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-status-controls.md` |
| Goal | Add restrained diary controls for status-only mutation |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend, taskpane/Command Centre/Gemini, booking create/edit/drag/drop, roster admin UI |
| Verification | JS syntax plus live/smoke/narrow/failure/session visual checks |
| Status | Integrated |

### Workstream V - Status Mutation Review Plan

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/status-mutation-review-plan` |
| Task Packet | `orchestration/agent_inbox/codex/codex-status-mutation-review-plan.md` |
| Goal | Define the post-integration review path for controlled status mutation |
| In Scope | Small orchestration/checklist documentation only |
| Out of Scope | Production backend/frontend implementation, tests, migrations, booking create/edit/drag/drop |
| Verification | `git diff --check` |
| Status | Integrated |

## Sprint 6: Read-Only Patient Flow Visibility

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Make appointment status and waiting-room/patient-flow state reviewable before booking or status mutation UI |

### Workstream Q - Waiting Room Status Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-waiting-room-status-contract.md` |
| Goal | Harden read-only waiting-room/status API behavior and tests |
| In Scope | Appointment models/schemas/router and appointment/waiting-room tests |
| Out of Scope | Diary frontend, taskpane/Command Centre/Gemini, booking/status mutation UI |
| Verification | Focused appointment/waiting-room pytest suites |
| Status | Integrated |

### Workstream R - Diary Status Affordances

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-status-affordances.md` |
| Goal | Make appointment lifecycle/status easier to scan in the read-only diary |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend, taskpane/Command Centre/Gemini, booking/status mutation controls |
| Verification | JS syntax plus live/smoke/narrow visual checks |
| Status | Integrated |

### Workstream S - Patient Flow Review Notes

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/patient-flow-review-notes` |
| Task Packet | `orchestration/agent_inbox/codex/codex-patient-flow-review-notes.md` |
| Goal | Define review expectations for read-only patient-flow/status visibility |
| In Scope | Small orchestration/checklist documentation only |
| Out of Scope | Production backend/frontend implementation, tests, migrations, booking/status mutations |
| Verification | `git diff --check` |
| Status | Integrated |

## Sprint 5: Diary Polish and Test Infrastructure

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Smooth the diary user-review rough edges and harden the test infrastructure before booking mutations |

### Workstream N - Test DB Teardown Hardening

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-test-db-teardown-hardening.md` |
| Goal | Fix the recurring partial PostgreSQL test DB teardown/reset failure seen during rapid pytest reruns |
| In Scope | `tests/conftest.py` and narrow test DB setup/teardown helpers/tests as needed |
| Out of Scope | Production app behavior, migrations, diary frontend, taskpane/Command Centre/Gemini, booking mutations |
| Verification | Repeat focused diary roster/template pytest runs; broader tests only if fixture changes risk shared behavior |
| Status | Integrated |

### Workstream O - Diary Date and Now Marker Refinement

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-ui-date-now-refinement.md` |
| Goal | Add a practical date control and soften the current-time marker without regressing narrow diary layout |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend, tests beyond narrow frontend smoke helpers, taskpane/Command Centre/Gemini, booking mutations |
| Verification | JS syntax plus live/smoke/narrow/date-picker/Now-marker browser checks |
| Status | Integrated |

### Workstream P - Diary Smoke/Live Review Checklist

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/diary-smoke-live-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-diary-smoke-live-review.md` |
| Goal | Clarify smoke-mode versus live-diary expectations and prepare the post-integration review checklist |
| In Scope | Small orchestration/checklist documentation only |
| Out of Scope | Production backend/frontend implementation, migrations, seed data, taskpane/Command Centre/Gemini |
| Verification | `git diff --check`; JS syntax only if JS is touched |
| Status | Integrated |

## Sprint 4: Diary Roster Consumption

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Make date-specific roster data visible in the diary without starting booking mutation work |

### Workstream K - Diary Roster Dev-Data Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-diary-roster-dev-data-contract.md` |
| Goal | Make roster backend data seedable, scoped, ordered, and predictable enough for frontend consumption |
| In Scope | `app/models/diary.py`, `app/schemas/diary.py`, `app/routers/diary.py`, `seed.py`, migrations/tests as needed |
| Out of Scope | `docs/diary/*`, booking mutations, Gemini/taskpane/Command Centre |
| Verification | Focused diary roster/template tests plus migration checks if changed |
| Status | Integrated |

### Workstream L - Diary Roster Consumption

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-roster-consumption.md` |
| Goal | Fetch and merge date-specific roster entries into the read-only diary frontend with safe fallback |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend routes/models/tests, booking mutations, taskpane/Command Centre/Gemini |
| Verification | JS syntax plus normal/smoke/narrow/date-navigation browser checks |
| Status | Integrated |

### Workstream M - Diary Roster Smoke Review

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/diary-roster-smoke-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-diary-roster-smoke-review.md` |
| Goal | Prepare the review/smoke-test surface for roster consumption without duplicating implementation scopes |
| In Scope | Small orchestration/checklist or smoke-review artifacts; tiny non-overlapping smoke fixture only if safe |
| Out of Scope | Backend roster implementation, production frontend roster merge, booking mutations |
| Verification | `git diff --check`; `node --check docs\diary\diary.js` if JS touched |
| Status | Integrated |

## Sprint 3: Diary Operations Foundation

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |

### Workstream H - Diary Time-Ruler UX

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/diary-time-ruler-ux` |
| Task Packet | `orchestration/agent_inbox/codex/codex-diary-time-ruler-ux.md` |
| Goal | Make flexible diary times visible and navigable without starting booking mutation work |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend roster models, appointment mutation routes, drag/drop booking edits |
| Verification | JS syntax plus desktop/narrow smoke checks |
| Status | Queued |

### Workstream I - Room and Diary Roster Foundation

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-diary-roster-foundation.md` |
| Goal | Persist room/roster configuration so diary columns can become date-specific |
| In Scope | Backend models, migration, schemas/router/service/tests |
| Out of Scope | Diary frontend, booking drag/drop, Gemini migration |
| Verification | Relevant pytest plus migration checks |
| Status | Queued |

### Workstream J - Gemini SDK Migration Spike

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-gemini-sdk-migration-spike.md` |
| Goal | De-risk migration away from deprecated `vertexai.generative_models` before removal |
| In Scope | Gemini/Vertex imports and calls, dependency notes, a small compatibility layer only if safe |
| Out of Scope | Prompt redesign, diary backend/frontend, clinical feature redesign |
| Verification | App import / targeted tests, plus exact risks if credentials block live smoke |
| Status | Queued |

## Sprint 1: Diary Interactivity Foundation

## Agent Inbox

Task packets are stored here:

- `orchestration/agent_inbox/claude/`
- `orchestration/agent_inbox/antigravity/`
- `orchestration/agent_inbox/codex/`

Packet status values are lightweight text: `queued`, `in_progress`, `submitted`,
`integrated`, `superseded`, or `blocked`. The submit command pushes the worker
branch only; Codex reviews and integrates afterward.

### Workstream A — Backend Time Model

| Item | Value |
|---|---|
| Owner | Codex |
| Branch | `codex/current` or `codex/time-model` if split further |
| Goal | Define and implement canonical appointment time representation |
| In Scope | `app/models/appointments.py`, `app/schemas/appointments.py`, `app/routers/appointments.py`, Alembic migration, seed updates |
| Out of Scope | Frontend drag/drop UI, room roster UI |
| Plan | Move appointments toward clinic-local `appointment_date` + `start_time_local` + `duration_minutes` + timezone-derived UTC helpers; preserve API compatibility during transition where practical |
| Verification | Migration applies; appointment CRUD tests; `/slots` tests; app import |
| Dissent / Risks | Requires careful transition from existing `start_time` data |
| Status | Integrated |

### Workstream B — Diary Grid Interval Rendering

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` or `antigravity/diary-grid-intervals` |
| Goal | Rebuild the diary grid so appointments occupy intervals, not only start cells |
| In Scope | `docs/diary/diary.js`, `docs/diary/diary.css`, `docs/diary/diary.html` |
| Out of Scope | Backend schema migration, appointment mutation routes |
| Plan | Render appointment duration spans from `start_time`/`end_time`; handle overlaps visibly; preserve silent refresh |
| Verification | Browser visual QA desktop/mobile; JS syntax; no spinner flash on auto-refresh |
| Dissent / Risks | Needs stable backend `end_time`; should avoid drag/drop until backend time model lands |
| Status | Integrated |

### Workstream C — Appointment Tests and Security Gates

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` or `claude/appointment-tests` |
| Goal | Add regression tests around auth, practice scoping, appointment conflicts, and slots |
| In Scope | Test framework setup if absent, appointment/consultation route tests, fixture seed helpers |
| Out of Scope | UI implementation |
| Plan | Create minimal pytest suite using FastAPI TestClient or direct route/service tests; cover P0/P1 fixes |
| Verification | Tests pass locally in `.venv`; failures are actionable |
| Dissent / Risks | Existing app imports initialize Vertex AI; tests may need dependency overrides/mocking |
| Status | Integrated |

### Workstream D — Gemini SDK Migration Spike

| Item | Value |
|---|---|
| Owner | Codex or Claude Code |
| Branch | Separate branch after Sprint 1 starts |
| Goal | Replace deprecated Vertex AI `generative_models` usage before the 2026-06-24 removal date |
| In Scope | `app/routers/consultation.py`, config, minimal smoke test |
| Out of Scope | Prompt redesign, SNOMED deterministic mapping |
| Plan | Identify current supported Google Gen AI client path for Vertex; migrate with behavior preserved |
| Verification | App import without deprecation warning; analyze/scribe smoke test with credentials |
| Dissent / Risks | Needs careful check against current Google docs and installed SDK versions |
| Status | Proposed, urgent technical debt |

## Sprint 2: Diary App Foundation

### Workstream E — Independent Diary Grid

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-independent-diary-grid.md` |
| Goal | Replace shared table-row diary rendering with independent positioned columns |
| In Scope | `docs/diary/diary.{html,css,js}` only |
| Out of Scope | Backend changes, drag/drop, booking/status mutations |
| Verification | JS syntax plus desktop/narrow browser visual QA |
| Status | Integrated |

### Workstream F — Canonical Time Regression Tests

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-time-model-regression-tests.md` |
| Goal | Prove legacy `start_time` and new `appointment_date + start_time_local` behavior |
| In Scope | Tests and minimal fixtures/helpers; tiny production fixes only if blocked |
| Out of Scope | Frontend, schema redesign, Room/DiaryRoster |
| Verification | `.venv\Scripts\python.exe -m pytest tests` |
| Status | Superseded by integrated canonical time test coverage |

### Workstream G — Diary Template API Foundation

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/diary-template-api` |
| Task Packet | `orchestration/agent_inbox/codex/codex-diary-template-api.md` |
| Goal | Add backend Room/DiaryRoster/template foundation compatible with current diary config |
| In Scope | Backend models/schemas/router/migration/tests as needed |
| Out of Scope | Frontend consumption, drag/drop, booking mutations |
| Verification | compileall, relevant pytest, Alembic head/current/upgrade if migration added |
| Status | Integrated |
