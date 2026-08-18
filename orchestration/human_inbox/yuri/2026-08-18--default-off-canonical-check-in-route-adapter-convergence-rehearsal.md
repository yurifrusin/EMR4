# Default-off canonical check-in route-adapter convergence — lay and technical summary

Date: 2026-08-18

Timestamp: 2026-08-18T13:39:45.6642329+10:00 (Australia/Brisbane)

Status: accepted; sprint engine continuing

Yuri attention required: no.

## Lay summary

Raisa's existing development-only check-in doorway now uses the same accepted
inner check-in mechanism instead of maintaining a second copy of that logic.
The doorway is still switched off by default and remains restricted to the
exact synthetic practices used for development. When it is off, denial still
happens before any appointment lookup or write preparation.

When the closed route is deliberately exercised in tests, it now asks one
canonical mechanism to recheck the receptionist, appointment, evidence and
waiting-area facts, then keep the appointment change, audit, event and receipt
together. A genuine retry returns the original outcome; conflicts and
uncertainty still stop safely. There is no hidden second route-local write
path.

Nothing has been enabled for ordinary practices. The general status control
cannot newly set `Arrived`; no Diary or Word client changed; moving or removing
a waiting area remains a separate action. No patient or clinical data, live
provider, deployment, release, Pages or protected branch was touched.

## Technical summary

`confirm_check_in_proposal_route` retains `_a5_check_in_gate_open` and exact
idempotency-key normalization before dependency construction, then calls
`compose_product_check_in` exactly once. `_a5_check_in_dependencies` binds the
existing command claim, practice/appointment/actor locks, in-transaction
Receptionist reauthorization, same-practice area lookup, HMAC verifier,
Arrived/area effect, audit, patient-free committed event, completion,
commit/rollback and exact readback. Response mapping preserves the existing
200/404/409/503 and fail-closed 500 behavior.

The adapter now classifies structurally valid same-key replay/conflict states
before semantic envelope validation so the route contract remains exact. A
newly started invalid envelope rolls back, and explicit body evidence retains
its legacy precedence while server-side binding remains mandatory.

Acceptance includes 103/103 focused tests, 35/35 database-backed A5.1 checks,
85/85 API-Spine/plan checks, compilation, Ruff, whitespace and the complete
435-entry incident-register suite. A fresh Gemini 3.7 Flash/high veto passed
all eight commands and left the clean exact candidate unchanged.

DeepSeek through Claude Code again returned exit 1 with no worker result or
source after the bounded wait. That failure is preserved as transport evidence
and Sol implemented the frozen package under the declared recovery lease. The
next operation is the very short native DeepSeek Harness rehearsal Yuri just
authorised: one isolated authored-synthetic task, with exit/stdout/stderr and
durable trace evidence captured. It cannot read EMR4 or patient/product data
and will not change the default worker transport without a later comparison
and decision.
