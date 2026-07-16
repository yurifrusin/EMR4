# LC4V9 Third Post-Veto Ordinary-Interface Amendment

Date: 2026-07-16
Status: `fresh_fourth_veto_required_before_content`

During the final pre-authoring audit of all five semantic outcomes, Sol found
that `validate_gold_cross_field_consistency` required a `no_action` projection
to contain no tools at all. The accepted ordinary policy intentionally retains
one `search_patients` read lookup when a fully identified patient's requested
action is negated. This identifies the subject of the negation; it does not
perform or claim the requested mutation.

No protected V9 surface existed or was read. This is an ordinary-interface
authoring-contract defect, not parser or holdout evidence.

## Sol amendment

- `no_action` accepts only `[]` or exactly `["search_patients"]`.
- It still requires read authority, no downstream outcome, no clarification,
  no mutation tool, zero appointment/audit deltas, and no simulated write.
- Adversarial tests reject `find_slots`, `request_clarification`, duplicate
  lookups, and any downstream action claim in a `no_action` projection.
- The other four semantic outcomes and every evidence/threshold/binding guard
  are unchanged.

The previous exact-head reviews remain preserved but cannot authorize this
amendment. One fresh named-file-only Gemini veto is required before Sol-only
authorship begins.
