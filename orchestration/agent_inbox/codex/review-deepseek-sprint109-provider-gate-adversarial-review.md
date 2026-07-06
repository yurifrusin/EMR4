# DeepSeek Sprint 109 - Provider-Gate Adversarial Review

| Item | Value |
|---|---|
| Author | DeepSeek Flash (adversarial review lane) |
| For | Ariadne / Codex orchestrator + Yuri |
| Mode | Review only - no production code, no provider wiring, no route edits |
| Date | 2026-07-07 |
| Inputs read | AGENTS.md, protocol_alerts.md, parallel_workstreams.md, sprint_closeout.md (Sprint 108), bernie_release_gates.md, interpretation-harness-runtime-gate.json, task packet deepseek-sprint109-provider-gate-adversarial-review.md, Fable strategy review, H58 readiness gate review, H53 runtime gate tests |
| Engine state at read | Continuing (Sprint 108 local integration verified) |

---

## 1. Executive Verdict

**The runtime-provider/live-smoke gate is structurally sound but has a dangerous soft surface: partial or silent boundary creep.** The gate JSON's `blocked` decision, its explicit forbidden use list, and the test-level static assertions are all well-designed. The risk is not that an obvious live-provider switch is flipped - it is that a sprint opens "just one" provider-adjacent capability (fake-provider-now-with-real-config, read-only H15-adjacent context in a prompt, Access AI audit with a live fallback) that crosses the gate line without a corresponding gate review, because no *runtime* enforcement exists.

The gate is enforced today through static tests and manual review artifacts. That is correct for the current provider-free phase. But it means every sprint closeout must actively re-state which gates are still blocked and confirm no drift occurred, because the enforcement is all pre-commit and pre-deploy, not in-flight.

---

## 2. Concrete Failure Modes If Gate Opens Too Early

### 2.1 Access AI invocation without typed audit event catalog

The Access AI service exists and is wired through `GeminiVertexBookingInstructionInterpreter`. Sprint 108 proved the route persists Access AI audit events. If a live provider is enabled before the *typed audit event catalog* is hardened (each event has a fixed schema, forbidden-key blocklist, and no-raw-instruction-text guarantee), a provider response error could leak PHI, raw prompt text, or internal identifiers into an untyped audit log.

**Severity:** High. Silent data leakage into an append-only audit table is the hardest to remediate.

**Current guard:** Sprint 108 tests prove `live-provider audit metadata excludes forbidden key fragments and raw instruction text` - but only for the existing audit paths. A new provider-returned error field not yet in the blocklist would pass through.

### 2.2 Live smoke without a deterministic offline oracle

If `scripts/smoke_bernie_interpreter.py` or the Margaret Thompson / Dr Shera gate is run against a live provider before a deterministic reference oracle exists (non-provider script that produces the same expected output shape), every live failure is ambiguous: provider API issue, prompt regressions, config drift, or genuine logic bug. The team has no way to triage quickly.

**Severity:** Medium-High. Sprint 98's screenshot-blocker pattern repeats - failures that cannot be reproduced offline stall the closeout.

**Current guard:** The release gates document requires the gate to be "deterministic, provider-backed, or both". It does not require a deterministic oracle *before* any live run, which is a gap.

### 2.3 Fake-provider routing bypass via configuration drift

The existing gate distinguishes fake-provider (mocked, `live_provider=false`) from live-provider (`live_provider=true`). If a future sprint changes a configuration default, environment variable, or service-layer default from fake to live without updating the gate test, a route could silently start calling a live provider. The existing tests assert static `live_provider: false` on fake paths - they do not assert that *no route ever calls a live provider when the gate says blocked*.

**Severity:** High. Silent live provider activation with no kill-switch in the request path.

**Current guard:** Test-level static assertions only. No runtime guard in the request path or middleware.

### 2.4 Provider output interpreted as write authority

The interpretation harness correctly projects provider-free frames as `writes_authorized=false`, and H45 asserts this. But those are test-only assertions on authored synthetic fixtures. If a live provider prompt is wired to a route, there is no runtime guard that strips `writes_authorized` from the provider's response before the route processes it. The route contract (H37) says confirm actions route to proposal and signed-confirm surfaces, but that is a static inventory, not a runtime interceptor.

**Severity:** Critical. A hallucinated confirmation response from the model could be treated as authority to write a booking.

**Current guard:** Route authority static inventory + test-level frame assertions only. No runtime enforcement between provider output and route dispatch.

### 2.5 Cost/rate-limit spike before instrumentation

The gate JSON requires a `focused_tests_and_manual_review_plan` and `rollback_or_kill_switch_plan` before unblocking. These are not yet implemented. If a live provider is wired without usage caps, a buggy loop (e.g., polling, retry storm, confirmation-loop re-prompt) could generate thousands of billable provider calls in minutes.

**Severity:** High. Financial and operational.

**Current guard:** The requirement exists in the gate JSON but is not yet tested or deployed.

### 2.6 H15 semantic-gate creep via provider context

The H15 approved prototype is one tiny local-only pass with `action_grammar_candidates` only. If a live provider prompt includes even an aggregate reference to historical diary content, or if the provider adapter reads an H15 fixture for "context", the H15 gate is silently widened without a new review. The memory boundary test (H31) guards against H15 fixtures being imported by runtime modules - but a live provider prompt string could mention diary patterns learned from reading docs, not just importing fixtures.

**Severity:** Medium. Gradual erosion of the semantic boundary.

**Current guard:** Static import guard (H57). No runtime guard on what a provider prompt string references.

### 2.7 Staff confirmation affordance not yet in production UI

The Bernie panel's staff confirmation affordance (H46/H47 frame contracts show "staged for review, not booked") is proven in test frames and route-intercepted Playwright coverage only. If a live provider is wired before the production UI actually renders that affordance, staff see a raw booking result and may believe the appointment is confirmed when it is only proposed.

**Severity:** Critical. Clinical/operational - staff act on a false confirmation state.

**Current guard:** The release gates document requires "a visible path back" (choose-another-slot) but not a specific "not yet confirmed" visual treatment. The route-intercepted Playwright tests prove the candidate path works; they do not test the live-provider-produced proposal visual state.

---

## 3. Minimum Blocking Checks Before Any Gate Opening

These are the structural prerequisites from the gate JSON, ordered by the risk they mitigate. All must pass before any gate scope item changes from `false` to `true`.

| # | Check | Mitigates | Status Today |
|---|---|---|---|
| 1 | **Explicit Yuri approval** documented with date and scope | All 2.1-2.7 | Pending (blocked) |
| 2 | **Bounded no-write runtime plan** reviewed and committed | 2.1, 2.4, 2.7 | Not yet drafted |
| 3 | **Deterministic offline oracle** for Margaret Thompson / Dr Shera gate | 2.2 | Not yet built (Sprint 98 evidence is route-intercepted, not offline oracle) |
| 4 | **Typed audit event catalog** with forbidden-key blocklist, no-raw-text guarantee, and provider-error coverage | 2.1 | H58 says typed audit catalog is pending; Sprint 108 covers limited audit paths |
| 5 | **Kill-switch / feature flag** to cut provider calls without deploy | 2.3, 2.5 | Not yet implemented |
| 6 | **Cost instrumentation** (per-call cost tracking, spike detection, hard cap) | 2.5 | Not yet implemented |
| 7 | **Route authority runtime guard** - middleware or adapter that blocks writes from provider-shaped frames | 2.4 | Static only (H37/H38) |
| 8 | **Staff confirmation affordance in production Bernie panel UI** | 2.7 | Route-intercepted Playwright proof only |
| 9 | **Provider-privacy-and-cost review** covering prompt PHI risk, model data retention, and per-call cost bounds | 2.1, 2.5, 2.6 | Not yet performed |
| 10 | **Focused regression tests** covering every forbidden-gate path with a negative test | 2.3, 2.4, 2.6 | Some exist (H53 gate test checks static JSON); no route-level forbidden-path tests |

---

## 4. Blockers vs. Nice-To-Haves

### Blockers - gate must not open until satisfied

- Checks 1-10 from section 3
- H15 semantic-gate H22 review packet must be re-verified for any new provider prompt scope
- Historical diary material access remains blocked; no provider prompt should reference raw/aggregate trove content
- Access AI must remain in fake/disabled default mode; any live-provider default change is a gate-opening event
- GraphQL mutations must remain undeployed; no provider output should reach a mutation resolver

### Nice-To-Haves - valuable but not blocking

- Full GraphRAG memory integration (Band 7/8 in Fable map - correctly deferred)
- Broad full-trove mining (H22 gate review not yet triggered - correctly blocked)
- External patient client routing (Band 9 - strictly downstream of internal spine)
- Every interpretation harness fixture case having a contract (current 44/44 - coverage is excellent; 1-2 missing contracts would not block gate safety)
- Wiley/Cochrane knowledge base integration (Band 6 - spike only)
- Multi-tenancy FGA before first live provider (enterprise feature, not blocking for a bounded single-practice live trial)
- Kiosk/online booking UI
- Claude Fable re-review of the gate posture (Fable access limited - reserve for the actual gate-opening review, not a pre-gate check)

---

## 5. Invariant Assertions

These must remain true in every sprint closeout until explicit Yuri approval changes any single one:

1. **`runtime_gate_decision` = `blocked`** in the gate JSON and snapshot
2. **`runtime_or_provider_wiring_ready` = `false`** in the readiness check
3. **`raw_trove_access_ready` = `false`** in the readiness check
4. **`sprint_engine` = `continuing`** (pause required if any gate-mandated value changes)
5. No production `app/` Python file imports interpretation harness report/readiness/gate tooling, H15 fixtures, H-series profile fixtures, historical diary candidate builders, or `local_data` paths (H57 guard)
6. No live provider default is enabled in any configuration path
7. No historical diary raw content is committed to `tests/`, `docs/`, or `app/`
8. No semantic-gate payload from H15 is wired to a route, provider prompt, memory module, or RAG/GraphRAG pipeline

These eight assertions are the sprint-closeout gate-check. If any is false without Yuri approval, the closeout is blocked.

---

## 6. Dissent / Risks

**Risk of overreliance on static enforcement.** The entire gate stack (gate JSON, snapshot test, readiness check, runtime isolation guard, leakage lint) is pre-commit and pre-deploy. None of it runs in the request path. If a configuration drift, environment variable change, or unintended deployment occurs, the gate silently fails open. The current design is appropriate for a provider-free development phase, but the team should not assume it protects against operational mistakes. A runtime gate assertion (middleware or health check that fails if a live provider is configured when the gate says blocked) would close this gap.

**Risk of gate fatigue.** After 30+ sprints of provider-free harness work, there is natural pressure to open "just one" live capability. The gate JSON is designed to make that an explicit Yuri decision. But if the team starts describing "small live experiments" as not-gate-opening events (e.g., "it's just a dry run, not a live route"), the gate's categorical style becomes ineffective. Every use of a configured provider - whether through a route, a script, a dev endpoint, or a manual test - that produces model output from a non-fake provider path counts as crossing the gate line. The release gates document and protocol alerts already say this; the risk is interpretation drift.

**Risk of the gate itself becoming a comfortable ritual.** The gate tests pass, the readiness check passes, the snapshot matches - and the team relaxes vigilance about *what changed between check and closeout*. The H57 runtime isolation guard helps, but it only covers imports, not prompt content or configuration values. Every closeout should ask: "Did anything cross the fake-provider boundary, even for debugging?" If yes, it is a gate event and must be reported as such.

---

## 7. Verdict

**Keep all provider/runtime/trove/memory/model-write gates blocked pending Yuri.** The gate infrastructure (JSON, readiness check, snapshot, isolation guard, leakage lint) is correct discipline for the provider-free phase. The blocking checks in section 3 are not yet satisfied; the nice-to-haves in section 4 are correctly deferred. No sprint should propose opening any gate without first satisfying checks 1-10 and re-running the full readiness/verification stack.

The next safe step for the gate stack itself (not the gates it protects) is to add a runtime assertion - a health check or middleware test that confirms the configured provider path matches the gate decision at startup. That would close the configuration-drift gap (failure mode 2.3) without opening any live capability.

---

## 8. Files Changed & Verification

**Files changed:**
- `orchestration/agent_inbox/codex/review-deepseek-sprint109-provider-gate-adversarial-review.md` (new, this artifact).

No production code, tests, scripts, app, frontend, database, configuration, or provider files were touched. No raw/ignored `local_data` or historical diary material was read. No blocked gate was opened or recommended for opening.

**Verification:**
- `git diff --check` passed in the DeepSeek worker worktree before Ariadne
  integration.


