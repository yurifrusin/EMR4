# Sprint 96 Plan Review - Bernie Reception Assistant UX And API Evidence Contract

| Item | Value |
|---|---|
| Status | Plan gate closed; implementation released |
| Reviewed by | Ariadne |
| Reviewed at | 2026-06-30 23:30 +1000 |
| Dispatch commit | `68d3728` |

## Product Read

The screenshots show a working technical foundation but an unsuitable reception
product surface.

Working:

- Bernie can interpret a receptionist instruction into a slot-search intent.
- Candidate slots are generated and can be selected.
- A selected candidate can stage a local diary preview.
- The current backend keeps proposal/search stages non-mutating.
- The confirmed-write endpoint is the only Bernie path that should create an
  appointment and already records appointment audit evidence.
- Access AI audit exists for live model/provider invocation metadata.

Not working:

- Staff-facing language still sounds like an internal safety prototype:
  `Supervised Booking Review`, `BLOCKED`, and warning-code dumps dominate.
- The robot/masked emoji makes the workflow feel less trustworthy and more
  theatrical than the risk actually warrants.
- The provisional diary card wastes visual space on labels such as
  `BERNIE PROVISIONAL BOOKING` instead of patient/time/identity evidence.
- Raw UUIDs, provider labels, autonomy states, and warning codes leak into the
  receptionist workflow.
- Candidate slot cards are visually repetitive and do not yet present enough
  decision information.
- The Confirm action and keyboard shortcut are not obvious enough.
- Identity evidence exists but is not yet shaped as a calm receptionist decision
  aid.

North star:

- API rigor, typed proposal contracts, staff-confirmed writes, RBAC, and audit
  trail are the real guardrails.
- The UI should be calm, useful, and information-rich. It should not perform
  visible safety theatre.
- Caller ID, phone-system integration, OPV/PVM/IHI, and live Medicare checks
  remain placeholder/context-frame vocabulary only in this sprint.

User pulse decision:

- Yuri approved trying a restrained pulse effect on the provisional diary slot
  card.
- Ariadne accepts this only as a temporary attention cue: subtle, short-lived,
  disabled under `prefers-reduced-motion`, and never a substitute for the
  visible patient/practitioner/time/identity evidence or the explicit staff
  Confirm action.

## Plan Results

### Claude - Backend/API Evidence Contract

Branch: `origin/claude/current` at `e2afd8a`

Result: provisionally accepted.

Strengths:

- Correctly identifies that the existing non-mutating proposal and confirmed
  write split is the right foundation.
- Proposes additive evidence fields rather than a rewrite.
- Keeps live Caller ID / OPV / Medicare integrations out of scope.
- Names exact backend files and focused tests.
- Includes no-write/no-audit assertions for proposal stages and exactly-one
  write/audit assertions for confirmation.
- Recommends no migration and reuse of existing appointment audit JSONB for
  bounded identity-confidence evidence.

Required implementation constraints:

- Do not expose raw provider/internal fields to the diary UI.
- Keep patient evidence deliberately bounded: patient name, DOB where useful
  and already held by EMR4, masked contact where available, identity confidence,
  and staff prompt. Do not add live external verification.
- Audit codes must stay enum-like and bounded, not free text.

### Codex Worker / Hypatia - Acceptance Review

Branch: `origin/codex/bernie-reception-acceptance-review` at `aa57c5c`

Result: accepted as review input.

Strengths:

- Confirms the backend architecture is broadly sound.
- Gives useful acceptance criteria for staff-facing language, raw identifier
  hiding, no-write behaviour, candidate selection, and confirmation gates.
- Clearly rejects Caller ID / OPV / Medicare scope creep for Sprint 96.

### Antigravity/Gemini - Reception UX Plan

Branch: `origin/antigravity/current` at `81694c7`

Result: rejected; resubmission blocked by worker channel.

Reason:

- First submitted plan was too brief and generic.
- It named `review/checks_diary.json`, which is not an established current
  sprint surface.
- It centered pulse animation rather than calm information design.
- It did not specify replacement copy, staged-card information hierarchy,
  confirmation-button/shortcut gates, route-intercepted no-write assertions, or
  detailed smoke tests.
- Ariadne sent two resubmission prompts. The first produced only a small
  improvement; the second Antigravity CLI run stalled in a generation loop with
  no file changes.
- Windows automation found no targetable Antigravity GUI window, so Ariadne
  could not safely continue the Gemini plan loop in this turn.

## Gate Decision

Implementation is released after acceptance of:

- Claude's backend/API evidence contract plan.
- Codex/Hypatia's acceptance review.
- The replacement Codex/Ariadne UX plan in
  `orchestration/sprint_96_replacement_ux_plan.md`.

Antigravity/Gemini is explicitly stood down for Sprint 96 implementation because
its submitted UX plan was rejected and its resubmission channel stalled. This is
a documented tooling/quality exception to the usual three-worker release.

## Recommended Next Move

Proceed with implementation:

- Claude owns backend/API evidence fields and focused backend tests.
- Codex owns diary UX/copy/pulse/shortcut and deterministic smoke checks.
- Ariadne integrates, repairs, verifies, and closes Sprint 96 before pushing.
