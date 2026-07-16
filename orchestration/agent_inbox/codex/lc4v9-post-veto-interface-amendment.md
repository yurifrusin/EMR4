# LC4V9 Post-Veto Ordinary-Interface Amendment

Date: 2026-07-16
Status: `fresh_second_veto_required_before_content`

Gemini 3.5 Flash/medium returned `DECISION: pass` on exact content-blind head
`4c9283b0a00fcb5a2e3fa44216599fc7efad2abe`. Its review is valid for that head,
but it does not authorize authorship after a material framework amendment.

Before creating any V9 content, Sol checked the framework against the accepted
ordinary LC4V8D1 development interface in the exact named files
`app/services/bernie/lc4v8d1_development_evidence.py` and
`tests/test_bernie_lc4v8d1_development.py`. This was ordinary development
evidence, not protected V8 holdout content. No protected holdout path was
opened, listed, searched, imported, run, or inferred.

## Defects found before content

1. The framework treated canonical `diary_relation` as though it encoded the
   utterance's temporal relation and time bounds. In the ordinary product
   contract it instead encodes diary-state comparison:
   `no_conflict`, `exact_duplicate`, or `field_conflict`.
2. The framework treated any selected tool as mutation evidence. Ordinary
   policy legitimately selects the non-mutating tools
   `request_clarification` and `refuse_instruction` for safe clarification and
   refusal outcomes.
3. Canonical projection type checks were too weak for `authority`,
   `diary_relation`, string-list fields, and nullable resolved/downstream
   fields.

These were authoring-contract defects, not parser defects and not evidence
about any protected holdout case. Had authorship proceeded, valid Gold could
have been rejected or distorted, repeating the authoring/projection mismatch
V9 is intended to prevent.

## Sol amendment

- Temporal relation now validates independently as one of `unspecified`,
  `exact`, `interval`, `not_before`, `not_after`, or `approximate`, with an exact
  `earliest_time`/`latest_time` bounds object and relation-specific shape.
- Canonical diary relation validates independently against the three ordinary
  diary-state values; conflict fields must agree with conflict state.
- Only `create_booking`, `update_appointment`, and
  `change_appointment_status` count as mutation tools.
- Clarification and refusal require their explicit non-mutating tools,
  authority, and downstream outcomes; proposal/read/no-action authority and
  hidden-mutation rules remain fail closed.
- Canonical projection field types now match the ordinary 14-field contract.

The amended focused-plus-taxonomy suite passes 63/63. The ordinary LC4V8D1
development suite passes 74/74 and the selected runtime-isolation gate passes
2/2. Python compilation and `git diff --check` pass. No V9 corpus, evaluator,
authoring module, thresholds, manifest, seal, marker, report, or protected
content exists.

The first Gemini pass is preserved as historical review evidence for
`4c9283b0` only. A second fresh Antigravity project must return
`DECISION: pass` on the exact amended head before Sol-only authorship begins.

