# Reception One same-update-family multi-change editor composition closeout

Date: 2026-08-15

Timestamp: 2026-08-15T04:08:00+10:00 (Australia/Brisbane)

Status: accepted

Accepted reviewed source: `daed421954d65c159871585559f45caa32d95aee`

Result: `raisa_reception_one_same_update_family_multi_change_editor_composition_pass`

## Lay summary

Reception One can now prepare a single appointment change containing any
combination of doctor, start time and appointment length. These are three views
of one clearly provisional draft. Moving between them preserves the unfinished
draft without contacting the server; closing the editor, changing appointment,
crossing into the separate status action or an interruption discards it.

Reviewing the draft sends one proposal through the existing appointment-update
path. Even a safe proposal stops at the familiar confirmation dialog. Only the
visible `Confirm & Save` button can authorise the write. Cancel, Escape, a stale
appointment, a blocked proposal or a transport failure cannot promote any
draft value into Diary truth. Every terminal outcome is reconciled from fresh
authoritative appointment data.

This closes the visible bridge between the four-button semantic console and the
already proved multi-field transaction kernel. It adds no second command path
and does not give Raisa, a model or an external channel independent write
authority.

## Technical result

- `docs/diary/meta-grid.js` now owns one local `selectedUpdateDraft` shared by
  the time, duration and practitioner editors, one patient-minimized draft
  summary and one `executeSelectedUpdateAction` submission path.
- One review passes the three effective values to the bounded
  `metaGridUpdateAppointmentDetails` bridge in `docs/diary/diary.js`.
- The bridge validates the effective same-day interval, freshly reloads the
  practitioner directory when reassignment is requested, admits one exact
  active target and calls existing `handleMoveResize` exactly once.
- `forceConfirmation: true` makes every admissible combined proposal stop at
  the existing dialog. Only its visible `Confirm & Save` control calls the
  existing allowlisted update-confirm route.
- Status remains outside the draft and continues through its separate proposal
  and confirmation family.
- Terminal handling uses the existing exact appointment/current-projection
  refresh. No requested field is patched optimistically into current truth.
- No backend, REST/OpenAPI, GraphQL, database, migration or event contract was
  added or changed.

## Verification

- Focused Reception One route-intercepted UI packet: 70 passed.
- Widened Reception One, parity, composition and API packet: 173 passed.
- API Spine, active-latch, orchestrator and correction-register packet: 391
  passed before the final workflow incident was recorded.
- Full post-incident correction-register suite: 242 passed.
- Canonical fast profile: 196 passed, plus Ruff, 209 maintained Python-source
  compilation, Diary JavaScript syntax and Git whitespace checks.
- Final closeout packet: 356 passed across nine continuity, register, index,
  latch, orchestrator, Compass and live-baton modules.
- Fresh Gemini 3.6 Flash/high independently passed the exact 173-test packet at
  unchanged clean source `daed421954d65c159871585559f45caa32d95aee`.
- Browser evidence label: `route_intercepted_browser_authored_synthetic`.

## Workflow incidents and corrections

- AER-0312 records DeepSeek's recurring fenced-JSON egress breach. Sol used
  only its bounded Git candidate and independently examined and repaired the
  test.
- AER-0313 records Sol's guessed nonexistent orchestrator module; exact module
  discovery preceded the successful receipt generation.
- AER-0314 records an invalid parallelism vocabulary value, corrected to the
  schema's `negative` value before admission.
- AER-0315 records JavaScript paths being mistakenly sent to Ruff; language-
  appropriate checks then passed.
- AER-0316 records a detached verifier worktree. Mandatory preflight stopped it
  before any provider call; the unchanged candidate was attached to a named
  disposable review branch and then passed.
- AER-0317 records the closeout node's initially invalid contract-evidence
  category links. The Continuity report gate stopped acceptance; exact contract
  types were linked and all seven continuity tests then passed.
- AER-0318 records one missed register aggregate fixture after AER-0317. The
  focused suite stopped; every exact register fixture was then reconciled and
  the complete register suite was rerun.
- AER-0319 records the invalid terminal-latch enum and stale predecessor-bound
  global Compass/baton fixtures found by the first final aggregate packet. The
  exact schema enum and all global fixtures were corrected before rerun.

No incident supplied product evidence, changed candidate behavior, reached
protected data or broadened authority.

## Parallelism efficacy: planned versus actual

- **DeepSeek V4 Flash/high:** negative net leverage. Its isolated test seed was
  useful, but required substantial Sol correction and output-contract
  containment.
- **Gemini 3.6 Flash/high:** positive leverage. It provided the required fresh
  exact-candidate veto and reproduced the 173-test/static packet without
  changing the worktree.
- **Native subagents:** declined as planned because no independent package
  remained after the tightly coupled client work began.
- **Sol:** retained plan, threat, product implementation, deterministic
  admission, repair, acceptance, continuity and Git authority.

## Next tranche

Proceed under standing authority with a provider-free, read-only
`raisa_post_combined_editor_compass_baton_orientation`. Reconcile the accepted
Reception One command families, Context Fabric/event-cue horizon, patient-
channel foundation and remaining Yuri-owned gates, then freeze the narrowest
dependency-satisfied next product tranche. It may not itself activate a model,
channel, command family, real-data source or runtime.

## Claim boundary

This proves the authored-synthetic, route-intercepted Reception One client
composition over the existing update proposal/confirm family. It does not prove
a live backend/browser round trip, production RLS or concurrency, representative
staff usability, conversational execution, patient or delegated-assistant
identity, live delegation revocation, a new event/command family, deployment or
production readiness. Product/patient/clinical data, provider/ADC, credentials,
IAM, network, watcher/database runtime, release, Pages and protected-ref
movement remain closed.

Yuri attention required: no.
