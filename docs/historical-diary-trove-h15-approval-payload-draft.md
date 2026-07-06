# Historical Diary Trove H15 Approval Payload Draft

Date: 2026-07-06
Status: draft only; H15 remains blocked
Decision authority: Yuri

## Purpose

This packet gives Yuri a concrete shape to review before deciding whether H15
may move from `blocked` to `approved_for_semantic_fixture_promotion`.

It is not an approval. The companion JSON keeps `decision` as `blocked` and
keeps the approval acknowledgement false:

```text
docs/historical-diary-trove-h15-approval-payload-draft.json
```

## Proposed Scope If Yuri Approves Later

The proposed approval would allow only:

- one tiny local-only prototype slice;
- at most one root and one dense day;
- at most 80 samples;
- action-grammar candidate fixture families only;
- relative day indexes;
- synthetic resource IDs;
- bucket flags and coarse confidence labels;
- no memory, RAG, GraphRAG, provider prompts, route wiring, or full-trove pass.

The proposed approval would still forbid:

- raw or extracted diary text;
- raw filenames or paths;
- exact source timestamps;
- patient labels;
- staff labels;
- phone numbers, Medicare numbers, or addresses;
- committed redacted diary records;
- external-provider processing of raw or extracted diary material;
- autonomous writes or backend authority changes.

## Required Validation Before Any Approval

Before the JSON can be converted from draft to approved, these must pass:

```text
.venv\Scripts\python.exe scripts\historical_diary_deidentification_gate.py docs\historical-diary-trove-h15-approval-payload-draft.json
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\pytest.exe tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py -q
```

The first command validates that the draft is still a safe blocked payload. A
future approved payload must also pass after `decision`, reviewer, acknowledgement,
scope, and expiry are explicitly updated by Yuri's decision.

## Manual Decision Required

If Yuri approves later, the approval patch should:

- change `decision` to `approved_for_semantic_fixture_promotion`;
- set `approval.reviewer` to `yuri`;
- set `approval.semantic_labelling_acknowledged` to `true`;
- move the reviewed semantic scope into `approval.semantic_scope`;
- set `approval.approval_expires_on` to a reviewed `YYYY-MM-DD` date;
- remove or supersede the draft-only `draft_review` object.

No agent should make that approval patch without Yuri explicitly instructing it
to approve H15.
