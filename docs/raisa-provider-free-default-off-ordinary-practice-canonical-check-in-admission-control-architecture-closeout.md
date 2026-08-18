# Provider-free default-off ordinary-practice canonical check-in admission-control architecture — closeout

Date: 2026-08-19

Timestamp: 2026-08-19T03:24:22.2795586+10:00 (Australia/Brisbane)

Status: accepted

Reviewed source: `752b521c59f5b44bf46de0cf776a33ac74b8134d`

## Outcome

The narrowest fail-closed architecture is frozen. Ordinary-practice admission
is a server-owned typed record that is distinct from the unchanged authored-
synthetic allowlist. Default denial remains exact, and no ordinary-practice
record is active or authorized.

The four record states are `prepared`, `active`, `suspended` and `withdrawn`.
Exactly six transitions are allowed. There is no resume edge. Withdrawal is a
disable-only rollback and cannot restore admission. A future reactivation must
use a new record, version, generation and complete operational evidence.

The global kill switch is dominant across both lanes and is monotonic within a
generation: `clear` may become `engaged`, while in-place or automatic clearing
is prohibited.

## API Spine and evidence boundary

Five future control operations are named as unmounted REST/OpenAPI commands.
Every operation remains unauthorized now. They require human authority,
dedicated operator role, server-owned practice and environment scope,
correlation and digest-bound idempotency, expected versions, append-only audit,
a bounded patient-free receipt, and a resolved lowercase 40-character Git
commit. Abbreviations and unknown commits release no success. GraphQL remains
read-only and async events remain observational.

The accepted three operational-evidence obligations remain mandatory:

- tenant runtime role and cross-tenant denial;
- rollback and unknown-commit behavior;
- environment and secret posture.

Exactly five low-cardinality non-PHI metric families and six non-actuating
critical alerts are frozen.

## Verification

- deterministic validator: passed;
- source bindings: 11/11 exact;
- focused tests: 20 passed;
- states/transitions/operations: 4 / 6 / 5;
- operational-evidence gates: 3;
- metrics/alerts: 5 / 6;
- hostile mutations: 390 rejected, zero escapes;
- Ruff, Python compilation and diff checks: passed;
- integrated acceptance packet: passed;
- fresh Gemini 3.7 Flash/high read-only veto: passed at the exact reviewed
  source with 9/9 bounded commands, a clean worktree and no P0-P2 finding.
- non-PHI Pushover closeout notification: delivered, request
  `71b837b5-fb9a-482f-be7e-0d5056d5777e`.

AER-0590 records the first verifier manifest's repeated direct-path Python
launcher. The verifier preflight rejected it before provider dispatch; the
module-form command then passed. AER-0591 records a read-only multi-operand
`git rev-parse --verify` rejection; five corrected scalar readings preserved
the exact task and protected-ref objects. Revision 512 contains 591 bounded
incidents, all corrected or contained and none open.

## Clockwork consequence

The accepted shadow clock should ultimately project verifier command grammar,
full Git object identity and aggregate readings from one typed journal. Its
digest-bound WorkOrder may mesh with the DeepSeek native Harness broker as one
causal sequence: the broker accepts only the exact Ariadne tick and returns a
result bound to that tick before either side may advance. This is a design
constraint for a later shadow control-plane migration, not live adoption and
not product admission authority.

## Closed boundaries and successor

No feature flag, allowlist, product/configuration source, route, generic-status
`Arrived` behavior, action grammar, first-party client, waiting-area movement,
database, product/patient/clinical data, live provider, production runtime,
deployment, release, Pages or protected ref changed. `docs/branding/` and all
unrelated untracked files remain preserved.

The next tranche is
`raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal`.
It may rehearse the typed evaluator with zero active records and exact default
denial. It authorizes no enablement or mounted product command.
