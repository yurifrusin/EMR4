# review-codex-codex-bernie-slot-normalize-endpoint-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-slot-normalize-endpoint` |
| Source Task | `codex-bernie-slot-normalize-endpoint-contract` |
| Status | integrated |

## Review Request

Sprint 40 Codex worker implementation ready for Ariadne review. Verified with project venv: py_compile app/routers/appointments.py app/schemas/appointments.py app/services/bernie_slot_normalizer.py tests/test_slot_search_normalize_endpoint.py; pytest tests/test_slot_search_normalize_endpoint.py tests/test_bernie_slot_normalizer.py tests/test_slot_search_proposal.py -q --tb=short -p no:randomly -> 58 passed; git diff --check passed.

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-bernie-slot-normalize-endpoint-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated. The route is a thin authenticated adapter from `SlotSearchCommandIn` to `SlotSearchCommandResult`, requires explicit `reference_date`, invokes only `normalize_slot_search_command`, and adds focused tests for auth, shape, deterministic reference-date handling, invalid command blocks, no slot search/LLM execution, and no appointment/audit writes.
- Follow-up required: None for Sprint 40. Later Bernie slices can wire this endpoint into UI/tool flows and decide whether non-mutating normalization should be available to a broader authenticated role set.
