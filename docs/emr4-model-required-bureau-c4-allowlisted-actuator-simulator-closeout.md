# EMR4 Bureau C4 allowlisted-actuator simulator closeout

Date: 2026-08-05

Result: `model_required_bureau_c4_allowlisted_actuator_simulator_pass`

Accepted source HEAD: `955b6a566f7097f58929dcb2fa9c4ed0aaad8b29`

## Accepted result

C4 passes at its frozen provider-free, local, in-memory and
authored-synthetic boundary. It accepts one opaque one-use execution-evidence
reference for exactly `restart-api-synthetic.v1`, targeting only
`isolated_authored_synthetic / service / synthetic:api-service`, with an exact
empty parameter object. The sole effect is the pure in-memory state transition
`degraded -> healthy`; the only rollback is
`restore-api-synthetic-lkg.v1`.

The runtime has no filesystem, process, shell, SQL, socket, network, database,
container, cloud, IAM, secret-store, provider, external-event or product-route
capability. It does not import `app`, mount a route or create a product
actuator. The API Spine artifact remains explicitly `not_mounted`, and GraphQL
remains read-only.

## Authority, one-use and verification properties

- Scalar admission fails closed before lookup, fingerprinting, evidence
  consumption, idempotency or audit.
- Evidence issuance uses non-caller-selectable cryptographic reference and
  nonce values and one locked issuance check-and-insert.
- Plan, decision, policy, catalog, actor, exact reviewer role, observations,
  target, freshness and expiry are revalidated against current in-memory
  authority; the evidence record remains only a binding.
- One shared execution store owns the transaction lock, evidence state,
  idempotency records, supersession state and monotone attempt sequence across
  every runtime instance sharing that store.
- Current authority is locked for the complete execution decision, transition,
  audit, fresh readback and any rollback, so revocation cannot interleave
  between validation and effect.
- Success releases only after a distinct fresh read verifies the exact target,
  revision and health tuple. Failure uses only the exact rollback and another
  fresh read. Effect audit survives only verified success; evidence consumption
  and attempt audit remain monotone.

## Preserved rejected attempts and Sol recovery

The first DeepSeek V4 Flash/high worker self-pass remains rejected as AER-0025.
Independent review reproduced seven material admission, target, authority,
audit, schema, entropy and issuance gaps. Its one bounded repair corrected
those seven but again self-passed while exact reviewer-role revocation,
execution-time authority mutation and cross-runtime one-use races remained;
AER-0026 preserves that second rejection.

Sol adopted both commits only as untrusted source under the recorded recovery
lease, added the three narrow transactional/authority repairs and direct
adversarial regressions, and regenerated the acceptance evidence. Revision 21
of the agent-error register marks AER-0025 and AER-0026 corrected only through
this completed recovery lease; neither failed candidate nor receipt is
relabelled as accepted.

## Deterministic and independent evidence

- The focused C4 simulator suite passes 31 tests.
- The widened C4, C3/D3, Gate-zero, API Spine and agent-error-register suite
  passes locally.
- Acceptance evidence regenerates and `--check` reproduces exactly.
- Ruff, compilation, Bandit, JSON validation and `git diff --check` pass.
- The fresh Gemini 3.6 Flash/high exact-HEAD veto independently passed 389
  tests, found zero material finding, emitted one terminal decision and left
  the verifier worktree clean at exact accepted HEAD.

Candidate-runtime external effects were zero. The only non-zero external
activity was the authorised Gemini/Antigravity source-review transport over
repository source and authored-synthetic evidence.

## Claim boundary

This proves a single provider-free authored-synthetic actuator simulator and
its deterministic authority, replay, rollback and verification properties. It
does not prove a provider model, live diagnosis, live observer, product or
patient data, real database, real service target, development recovery action,
C5, production, deployment, release, Pages, protected evidence or protected-ref
movement.

`docs/branding/` and every unrelated untracked receipt/state artifact remain
preserved and excluded.

## Planned successor

Standing programme authority opens planning for the narrowest C5 live-
development-recovery descendant. Planning must first freeze an exact disposable
non-PHI isolated target, reversible injected fault, model/provider boundary,
human authority, rollback, cost, audit and cleanup. C4 itself grants no live
action. A human handback is required only if the exact disposable target or an
external credential/console action cannot be derived and completed within the
recorded programme boundary.
