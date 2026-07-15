# LC4V4Q1 Sol Recovery Amendment

Date: 2026-07-15

Worker candidate: `4dc5ac8dbbcbfa9e8a06cea717402866d8719b3d`

Adopted as: untrusted candidate under the Ariadne recovery lease

Worker decision: `candidate_complete`

Sol decision: `revision_required` — conceptual failure; no Flash correction
loop is authorized.

## Preserved failures

1. `RenderedTurn.full_text` was computed directly as `prefix + core + suffix`,
   so its integrity assertion compared an expression with itself and could not
   detect a renderer that had already corrupted the core.
2. Multi-turn token coordinates were not evaluated against the addressed turn;
   the implementation contained a no-op condition and always checked turn
   zero.
3. Expected tools were copied from `facts.selected_tool_sequence` instead of
   being independently derived from canonical semantic facts.
4. The aggregate authoring receipt retained every detailed finding and its
   detail text, contrary to the aggregate-only contract.
5. Entity relation validation treated ambiguous, negated, and mismatched
   relations as requiring no surface evidence and therefore could not prove
   the relation assertion.
6. No category-completeness or distinct-cell validator existed.
7. The CLI created manifests and seals only in memory, printed them, never
   performed exclusive durable writes, never accepted a pre-existing
   unconsumed seal, and never wrote a consumed seal.
8. The evaluation CLI passed the corpus hash as the manifest hash.
9. No report-first/consumed-seal-last one-shot lifecycle existed or was tested.
10. The durable worker receipt recorded the source commit as the candidate
    commit; the launcher receipt preserved the actual candidate hash.

## Sol recovery scope

Sol will replace the authoring-quality validator with an independent rendered
text/core model, true multi-turn span validation, policy-derived tools and
outcomes, explicit relation evidence, coverage/identity checks, and an
aggregate-only hashed receipt. Sol will bind that quality receipt into the v4
manifest and seal chain, add an exclusive one-shot lifecycle and exact CLI,
and replace the self-confirming tests with mutation and lifecycle tests.

The candidate's exact failure and receipt remain preserved. No actual v4
content exists. No protected holdout surface was accessed. Independent Gemini
veto remains mandatory on the recovered exact head before content.
