# Reception One selected-appointment cancellation composition closeout

Date: 2026-08-17

Timestamp: 2026-08-17T15:49:00.1044374+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `856ebc3d832d5b64ce65c2e0732eaa63d926c600`

Result: `raisa_reception_one_selected_appointment_cancellation_composition_pass`

## Outcome

Reception One now presents a fifth, deliberately destructive `Cancel
appointment` action for one selected current appointment. It collects one
allowlisted administrative reason and an optional bounded note, then uses only
the dedicated delete proposal and canonical delete-confirm route. Every
admissible proposal stops at visible staff confirmation. No raw `DELETE`,
status-cancellation fallback or optimistic removal exists in the new bridge.

Terminal and uncertain outcomes always trigger a fresh scoped Diary read. A
successful cancellation disappears only when that read reports current truth;
blocked, stale, cancelled, malformed and transport outcomes likewise reconcile
before another action. Failed reconciliation disables the console and makes no
success or non-commit claim.

## Projection and adapter architecture

The native Reception One rendering is now explicitly a first-party reference
client, not the universal form of Raisa's UX. Raisa supplies a minimized typed
projection/action envelope. A contained creative renderer may vary layout,
wording, hierarchy, interaction sequence, accessibility treatment and modality;
an external Siri-like client may own nearly all presentation. Neither may alter
facts or provenance, current/proposed/committed state, action identity or
consequence, required warnings or blocks, confirmation, current-authority/source
rechecks, receipts or fresh reconciliation.

This establishes the durable split: creative presentation above deterministic
semantics, with all effects remaining behind the authority kernel.

## Verification

- The dedicated cancellation browser packet passes 15/15 cases.
- The combined selected-action browser packet passes 84/84 cases: 15 new and
  69 existing.
- Forty-three focused UI, API Spine and canonical delete-confirm checks pass.
- The canonical fast profile passes 200/200 tests, Ruff, 217 maintained-source
  compilation checks, JavaScript syntax and Git whitespace.
- Native desktop, tablet and phone inspection passes at 1280x720, 768x1024 and
  390x844 with 44-pixel targets, no horizontal overflow and no console error.
- One fresh nine-command Gemini 3.7 Flash/high exact-candidate veto returns one
  terminal `pass` and leaves source and review worktree unchanged.
- Typed evidence validates against the frozen recursively closed schema and is
  bound to exact candidate `856ebc3d832d5b64ce65c2e0732eaa63d926c600`.

Browser evidence remains `route_intercepted_browser`, not live backend or
database evidence.

## Parallelism and incidents

DeepSeek V4 Flash/high completed the separable browser-test artifact after one
preserved transport non-result and one bounded clean-source retry. Gemini 3.7
Flash/high supplied the independent veto. Sol retained product semantics,
source, admission, integration and acceptance. Native subagents remained
declined under current developer policy.

AER-0382 preserves the initial DeepSeek transport failure. AER-0383 preserves
two correctly rejected pre-verifier receipt drafts before the valid dispatch
receipt. AER-0384 preserves and corrects one recurrence of direct repository
pytest after an unconditionally chained failed prerequisite; that run was
stopped and excluded, and the accepted register test used the serial launcher.
The register is at revision 337 with 384 contained incidents and none open.

## Next tranche

The next dependency-satisfied architecture-strengthening step is a narrow
provider-free read-only review of the ordinary Diary cancellation compatibility
consumer. It will determine how `deleteBooking()` and
`applySignedDeleteProposal()` can converge on the same canonical delete-only
interaction now used by Reception One, without editing or calling the raw
compatibility `DELETE` path. This is repository analysis and plan freeze only;
any later source change must remain separately bounded.

Yuri's attention is not presently required.

## Claim boundary

This proves provider-free authored-synthetic first-party client composition,
route-intercepted browser behavior, repository regression and independent
source review only. It does not prove live browser/backend/PostgreSQL operation,
representative usability, external-adapter compliance, product/patient/clinical
data, deployment or production. Providers, ADC, credentials/IAM, external
network, executable model tools, migration/database/source access, raw
compatibility writes, release, Pages and protected-ref movement remain closed.
`docs/branding/` and every unrelated untracked file remain preserved.
