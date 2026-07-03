# review-claude-claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments` |
| Status | queued |

## Review Request

claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: coordination artifacts only —
  `orchestration/agent_inbox/codex/plan-claude-claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments.md`
  (revised Fable 5 architecture plan with explicit per-amendment verdicts:
  amendment 1 accepted — frames.py/policy.py rehome into `app/services/diary/`
  joins N1 as a pure move with wire strings `reception_policy` and
  `bernie.reception_context.v1` byte-identical; amendment 2 principle accepted,
  mechanics modified — suggestion invariant adopted verbatim, one new
  `DiaryActionSuggestion` envelope + author-side normalization contract instead
  of three catalog actions, since validate already exists as the propose tier
  and normalization is per-author adapter machinery; amendment 3 met in the
  middle — new K1 sprint builds a typed practice knowledge graph substrate
  (entity/edge tables + single `retrieve_advisory_context` interface +
  `knowledge` frame type, advisory-only) as the honest GraphRAG testbed, with
  vector/extraction machinery still deferred behind that interface under
  explicit escalation criteria; revised N1/N2/N3/K1/N4 sequence; first sprint
  recommendation amended N1 with N1a/N1b split fallback; advisory-only
  adversarial test lands in N1 and extends in K1 and N3) and this packet's
  status/notes. No production code, migrations, UI, schema, or test files
  edited.
- Verification run: read-only re-review grounding the verdicts —
  `app/services/bernie/frames.py` and `policy.py` confirmed pure contract code
  (policy imports only frames; no LLM/DB/session coupling);
  `capabilities.py` registry and `suggest_next_actions` entry;
  `reception_policy` consumer sites in `appointments.py`,
  `schemas/appointments.py`, `docs/diary/diary.js`, and the wire-contract
  assertions in `tests/test_bernie_context_frames.py`,
  `tests/test_bernie_interpret_booking_instruction.py`, and
  `review/test_diary_smoke.py`. No production tests run — plan-only task,
  no production code touched.
- Remaining risks: verdicts await Ariadne/Yuri review; amended N1 is larger
  than the original N1 (N1a/N1b split offered if review units should be
  smaller); the amendment-2 verdict intentionally departs from the literal
  three-action split and needs Ariadne/Yuri sign-off on the
  envelope-plus-adapter form; K1's boundary (no vector/extraction/graph-DB
  machinery) should be enforced at dispatch to prevent scope drift; N4
  PHI/TTL/concurrency decisions remain open and now also gate suggestion
  persistence.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
