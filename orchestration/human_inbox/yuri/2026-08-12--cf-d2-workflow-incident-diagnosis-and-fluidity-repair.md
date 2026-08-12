# CF-D2 workflow incident diagnosis and fluidity repair

Date: 2026-08-12

## Lay summary

Your instinct was right. CF-D2 was not trivial, but our process made it harder
than it needed to be. We were very good at proving that each attempt stayed
inside its safety boundary, yet not strict enough about asking whether the next
attempt would tell us something genuinely new. In effect, we documented the
same blurry observation several times.

The repair keeps the safety rails and removes much of the ceremony. Before a
diagnostic retry or correction can proceed, it must now show how its outcome
will distinguish the remaining explanations. Reviews use one exact executable
checklist whose individual results are machine-verified. Routine local fixes no
longer trigger a chain of planning, formatting and implementation reviews; one
final independent veto is used when risk warrants it.

So the answer to the angels-on-a-pin question is: yes, we had drifted a little
too far toward formality. The formality was valuable at the perimeter but had
become counterproductive inside the safe workspace. The new rule is **rigid at
authority boundaries, fluid inside them, and evidence-led at every retry**.

CF-D2 itself remains unproved. We did not run another database attempt or claim
to know its remaining cause. Because the dependent key-rotation and retention
work cannot safely start, the next programme direction is a genuine choice for
you rather than something I should invent under standing authority.

## Technical summary

- Accepted result:
  `ariadne_cf_d2_workflow_incident_diagnosis_and_fluidity_repair_pass`.
- Exact independently reviewed source:
  `018099dd6c5f0502121360732feb602252eb34cc`.
- The retrospective evidence gate rejects the CF-D2 correction path because
  four viable internal anchor hypotheses share the same observable result.
- Hard and adaptive controls are separated in
  `orchestration/harness_settings/evidence_led_workflow.yaml`.
- `scripts/ariadne_evidence_gate.py` enforces hypothesis discrimination and
  exact command-result admission.
- The Antigravity wrapper now uses a provider-admissible uniform array schema;
  exact ID, argv, order and zero exits remain a local release condition.
- Fresh Gemini 3.6 Flash/high returned no P0-P2 finding; 46 workflow tests, 228
  register tests, Ruff, format, compilation, whitespace and clean Git state all
  passed through nine exact manifest commands.
- The final canonical repository fast profile passed all 191 selected tests,
  Ruff, maintained-source compilation, Diary JavaScript syntax and whitespace.
- Register revision 255 contains 288 bounded known incidents and none open.
- CF-D2 attempt 003 is ineligible; key rotation and retention/purge remain
  blocked; protected refs remain `2e34bdad732fdab32fbf778280b3d3c70d66d602`.
