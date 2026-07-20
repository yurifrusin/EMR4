# Reception One combined-scope proof — post-veto Sol amendment

**Candidate reviewed by first Gemini pass:**
`3742d11df811efe3e1f0a480ffbbd090def7ff44`  
**First Gemini verdict:** `pass`  
**Sol disposition:** pass preserved as reviewer provenance but superseded for
acceptance by this material state-machine amendment

## Sol finding

After the first independent veto completed, Sol traced the refinement path from
an already selected availability slot. `refineCurrent()` correctly built and
rendered a fresh `availability_slots` answer, but `setProjection()` did not
clear `state.selectedItem` for a non-selection projection. The stale slot was
not visibly selected and the scoped proposal button was absent; however, a
later typed `prepare` request could still enter the selected-item branch and
prepare a proposal against the pre-refinement slot.

That violates the frozen requirement that any refinement clear stale selection
and proposal state. It is a real client-state defect even though the first
browser population and Gemini review passed.

## Bounded amendment

- `setProjection()` now clears `state.selectedItem` whenever the incoming
  projection is neither `selection_only` nor `proposal_not_committed`.
- The tablet-portrait real-browser scenario now selects a slot, refines the
  time window, proves the projection returned to availability with no scoped
  proposal action, then continues through duration refinement and reversible
  selection/back.
- Focused guards require both the state reset and the new browser evidence
  result `refinement_clears_stale_selection: pass`.

No API, write, event-runtime, provider, PII, protected, historical, Stage 3B,
production, deployment or release boundary changed.

## Amendment verification

- Five-viewport, six-screenshot real local browser/backend/PostgreSQL evidence:
  `browser_pass`.
- Before/after database counts and hashes: identical.
- Forbidden requests, failed API responses, browser console warnings/errors and
  page errors: zero.
- Exact disposable database: marker-verified and dropped.
- New plus inherited functional/live-local focused population: 30/30 passed.
- Node and Ruff checks: passed.

Because the change is acceptance-material state behaviour after the first veto,
a fresh Gemini veto over the amended candidate is mandatory before Sol may
accept it.
