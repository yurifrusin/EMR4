# Raisa AES-C1 provider-free admission rehearsal plan

Date: 2026-08-11

Source HEAD: `648c8ec9805af63729264ea9c22fd695f062a741`

Status: `frozen_for_authored_synthetic_unmounted_execution`

## Purpose

Prove the smallest deterministic admission decision beneath the accepted AES-C0
authority grammar. AES-C1 may instantiate and challenge exact AES-C0 message
objects, but it may not implement or start a broker, work cell, adapter,
provider, source, listener, watcher, tool or command.

The evidence label is `authored_synthetic_provider_free_unmounted`. No input is
patient-, clinical- or product-derived. No operation admitted by the rehearsal
is executed.

## Exact inherited inputs

AES-C1 consumes these accepted AES-C0 artifacts without changing them:

| Artifact | Required SHA-256 |
|---|---|
| `architecture-contract.json` | `403c7ddac2399760395d60a8094ffe42d2519a4a809bc8a59104acd2883eb9ae` |
| `architecture-contract.schema.json` | `344d88c59a5d781ebb205de575b66f2e3d64f3878f73c9c0bf4d86eb996b1740` |
| `authored-synthetic-contract-examples.json` | `f77801d2d752ca2daeed1b3116d78a965441bc1996f6b6da60eccf72fbee9f3e` |

The rehearsal imports the AES-C0 validator and its exact closed definitions for
`GenerationManifest`, `CapabilityLease`, `BudgetState`, `BrokerDecision`,
`RevocationRecord` and `AuditEvidenceEnvelope`. A source digest mismatch is a
terminal `revision_required` result, not an invitation to rewrite AES-C0.

## Selected boundary

AES-C1 adds one pure admission function over JSON-compatible authored-synthetic
objects. It performs no I/O beyond reading the committed fixture packet and
printing or writing deterministic minimized evidence.

The function receives a closed `AdmissionAttempt` containing:

- one exact AES-C0 `GenerationManifest`, `CapabilityLease` and `BudgetState`;
- an external authored-synthetic `CurrentGenerationState` binding the current
  generation, manifest identity/digest and supply-chain identities;
- an external authored-synthetic `CurrentAuthorityState` binding the principal/
  purpose digest, purpose, Bureau and work-cell identity at the check time;
- zero or one exact AES-C0 `RevocationRecord` for that generation;
- one proofreader result and one closed typed candidate;
- one broker-observed requested operation identity, source/field set and exact
  prospective cumulative-counter delta; and
- the deterministic evaluation timestamp.

The candidate may contain only closed typed arguments, proposal fields and
bounded explanation codes. It cannot supply a capability, adapter, operation,
destination, URL, method, media type, audience, credential, path, SQL,
executable, tool definition, command route, cleanup target or policy amendment.

## Manifest digest rule

AES-C1 strengthens the contract with one deterministic content-binding rule.
The manifest digest is SHA-256 over canonical JSON (UTF-8, sorted keys and
compact separators) after replacing both `manifest_digest` and
`supply_chain_identity.generation_manifest_digest` with the same fixed
`sha256:` plus 64-zero sentinel. The calculated digest must equal both stored
fields and the current-generation binding.

Candidate and budget-before/budget-after digests use the same canonical JSON
rule without a sentinel. This rule is evidence-only and creates no signing,
credential or runtime authority.

## Ordered fail-closed decision

The evaluator uses this fixed precedence:

1. reject malformed or non-closed input before semantic evaluation;
2. stop on an AES-C0 artifact digest mismatch;
3. stop on external kill, matching revocation, non-current/superseded
   generation, manifest-content digest mismatch or supply-chain mismatch;
4. stop when the manifest or lease is not temporally valid at the evaluation
   time;
5. stop when current authority is absent, stale or no longer matches the
   generation, purpose, Bureau, work cell or authority-binding digest;
6. deny a forbidden capability or any missing/non-exact manifest grant;
7. deny a missing, inactive or non-exact lease intersection;
8. deny a proofreader rejection or candidate-controlled operation identity;
9. stop before an operation when any positive cumulative ceiling is already
   reached, any prospective count would exceed its ceiling, or the requested
   capability has a zero disabled ceiling;
10. otherwise allow exactly the broker-observed operation without executing it.

For a non-terminal denial, the evaluator increments the applicable cumulative
denial/boundary-probe/repeated-failure counters. Reaching a positive denial
ceiling makes the returned after-state terminal and blocks the following
attempt. No budget transfers to another generation. Encoded, compressed,
chunked and exception-shaped output shares the one egress total.

Every result contains an exact AES-C0 `BrokerDecision` and minimized
`AuditEvidenceEnvelope`. An allow never carries command authority and never
means that an adapter ran.

## Frozen scenario catalogue

The authored-synthetic packet must contain these exact 45 scenario IDs and
expected decisions:

### Allow

1. `exact-inert-intersection-allow` — `allow`;
2. `exact-inert-second-within-budget-allow` — `allow`.

### Default denial

3. `grant-missing-deny`;
4. `grant-class-mismatch-deny`;
5. `grant-operation-mismatch-deny`;
6. `grant-adapter-mismatch-deny`;
7. `grant-destination-mismatch-deny`;
8. `grant-method-mismatch-deny`;
9. `grant-media-type-mismatch-deny`;
10. `grant-audience-mismatch-deny`;
11. `grant-source-class-mismatch-deny`;
12. `grant-input-field-overreach-deny`;
13. `grant-output-field-overreach-deny`;
14. `grant-call-limit-deny`;
15. `grant-request-byte-limit-deny`;
16. `grant-response-byte-limit-deny`;
17. `candidate-operation-identity-deny`;
18. `proofreader-not-admitted-deny`;
19. `forbidden-capability-class-deny`;
20. `lease-state-inactive-deny`;
21. `lease-manifest-mismatch-deny`;
22. `lease-generation-mismatch-deny`;
23. `lease-capability-mismatch-deny`;
24. `lease-class-mismatch-deny`;
25. `lease-audience-mismatch-deny`;
26. `lease-authority-mismatch-deny`.

### Terminal stop

27. `lease-outlives-manifest-stop`;
28. `lease-expired-stop`;
29. `manifest-expired-stop`;
30. `manifest-content-digest-mismatch-stop`;
31. `generation-superseded-stop`;
32. `cross-generation-replay-stop`;
33. `authority-binding-changed-stop`;
34. `authority-purpose-changed-stop`;
35. `authority-bureau-changed-stop`;
36. `authority-work-cell-changed-stop`;
37. `authority-stale-stop`;
38. `supply-chain-identity-mismatch-stop`;
39. `existing-revocation-stop`;
40. `external-kill-switch-stop`;
41. `cumulative-budget-already-exhausted-stop`;
42. `prospective-budget-overflow-stop`;
43. `zero-disabled-capability-stop`;
44. `denial-ceiling-reached-after-deny` — current result `deny`, terminal
    after-state and no following operation;
45. `attempt-after-denial-ceiling-stop`.

Malformed additional/missing-key and wrong-type attacks are generated
independently from the canonical attempts and must all fail closed. The
scenario registry must be exact: no undeclared scenario may be silently
ignored and every expected reason code must match.

## API Spine classification

This is a manifest/capability and security-admission artifact only.

- GraphQL remains a read-only context graph and is never invoked.
- Events remain signals for fresh authorized reads and are never consumed.
- Access AI remains a future backend-brokered provider command; AES-C1 makes no
  provider call.
- REST/OpenAPI commands remain separately authorized, human/policy-gated,
  idempotent, audited and deterministically read back. AES-C1 cannot prepare or
  confirm one.
- YAML/JSON remains declarative input; the pure evaluator supplies deterministic
  validation and cannot become a generic rules language.

## Security review tier and allocation

AES-C1 is `dual_review` because it exercises authorization, budget, revocation,
audit and future provider/tool admission controls.

- GPT Sol owns this frozen boundary, final implementation review, recovery,
  acceptance and Git closeout.
- DeepSeek V4 Flash/high through Claude Code `--bare` owns one bounded blue
  implementation/test candidate or defensive bypass review in an exact
  disposable worktree. It receives no acceptance or integration authority.
- Gemini 3.6 Flash/high through a fresh Antigravity project owns one exact-head,
  read-only red/veto review after deterministic gates pass. It receives no
  implementation authority and must emit exactly one `pass` or
  `revision_required` decision.
- Sol may adopt a rejected worker candidate only under the recorded recovery
  lease, preserving the rejection and every amendment before a fresh veto.

## Owned files

- this plan;
- `docs/security/raisa-agent-execution-surface-containment-gate-aes-c1-provider-free-admission-threat-model-delta.md`;
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/`;
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py`;
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c1.py`;
- exact AES-C1 receipts, worker/reviewer packets and decisions;
- a closeout, Sol acceptance, dated Yuri mailbox message, Continuity/Compass
  updater and focused continuity tests if the tranche passes; and
- exact current-baton/implementation-plan/fast-profile bindings required by an
  accepted closeout.

Existing AES-C0 files are read-only inherited inputs. The 494 pre-existing
untracked paths are not owned, including `docs/branding/` and the AES-C0
pre-push receipt/state pair.

## Forbidden surfaces

- no protected-evidence access, enumeration, search, import, execution or
  inference;
- no historical Diary or local PHI access;
- no patient, clinical, product-derived, financial or licensed content;
- no runtime broker, work cell, container, adapter, route, listener or watcher;
- no provider/model call, raw prompt/response, credential, IAM, metadata,
  network or external retrieval;
- no database/source access, migration, persistence or SQL;
- no filesystem capability, executable tool, shell/process capability,
  command/write or cleanup actuator;
- no deployment, production, release, Pages or protected-ref movement; and
- no broad Git staging, `git add .`, `git add -A`, staging of `docs/branding/`
  or adoption of unrelated untracked evidence.

## Deterministic acceptance

AES-C1 passes only when:

1. the three inherited AES-C0 inputs match their frozen hashes and the full
   AES-C0 acceptance remains green;
2. the new contract, scenario registry and result/evidence shapes are closed
   and exact;
3. both allow scenarios pass only the complete manifest/grant/lease/current-
   generation/current-authority/proofreader/budget intersection;
4. all 24 default-denial scenarios return their exact deny reasons without
   executing an operation;
5. all 19 stop/terminal scenarios return their exact stop reasons and block the
   following operation where applicable;
6. manifest, candidate and budget digests are independently recomputed rather
   than trusted from candidate content;
7. prospective accounting covers all reasoning, information, egress, action,
   denial and elapsed-time counters; zero means disabled and a reached positive
   ceiling blocks the next operation;
8. revocation, external kill, stale authority, supersession and cross-
   generation replay always outrank an otherwise valid grant;
9. evidence contains only closed IDs, decisions, reason codes, cumulative
   counts and digests, with no prompt, reasoning, credential, exception, patient
   or product value;
10. malformed and hostile mutations all fail closed with zero admitted attacks;
11. the focused AES-C1/AES-C0/API Spine packet, maintained static CI packet,
    canonical fast profile, Ruff, compile/syntax and Git whitespace checks pass;
12. the blue artifact and fresh red/veto decision satisfy the dual-review
    contract with no unresolved critical or high issue;
13. tracked scope is exact, all pre-existing untracked files are preserved, and
    protected refs remain `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

## Recovery, stop and cleanup

A deterministic failure blocks external review. A mechanical implementation
defect may receive one bounded DeepSeek revision; a conceptual or authority
defect moves immediately to Sol's recovery lease. Any scope expansion,
protected-evidence need, real adapter/provider/data requirement, contradictory
acceptance evidence or exhausted bounded recovery stops the tranche.

There is no runtime cleanup because no runtime starts. Closeout must prove zero
provider calls and zero product/patient data, compare the final untracked set to
the captured baseline, explicitly stage only owned paths, and leave protected
refs unchanged.

## Claim boundary and next work

Passing AES-C1 will prove only that the exact AES-C0 admission intersection and
terminal behavior can be evaluated deterministically over authored-synthetic
unmounted objects. It will not prove a broker process, adapter custody,
container/kernel isolation, atomic distributed budgets, provider behavior,
product-data safety, command safety, deployment or production readiness.

After acceptance, AES-C2 provider-free broker simulator is the next planned
candidate. It must receive a fresh five-source receipt and freeze one inert
allowlisted adapter with no external effect. AES-C1 itself grants no AES-C2
runtime or adapter authority.
