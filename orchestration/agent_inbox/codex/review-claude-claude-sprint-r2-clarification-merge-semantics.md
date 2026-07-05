# review-claude-claude-sprint-r2-clarification-merge-semantics

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-r2-clarification-merge-semantics` |
| Status | queued |

## Review Request

claude-sprint-r2-clarification-merge-semantics ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/routers/appointments.py` — Added `_MERGEABLE_COMMAND_FIELDS`, `_command_to_payload()`, `_clarification_prior_frame_values()` helpers; wired `payload=command_payload` into both `BernieRequestedAppointmentFrame` constructions in `_build_bernie_reception_context()`; added `command_candidate=result.command_candidate` arg to `_build_bernie_reception_context()` call in `_attach_bernie_interpret_reception_context()`; inserted clarification-reply merge block in `_resolve_bernie_interpretation_context()` that gap-fills `command_values` from the first `requested_appointment` context frame and emits a `clarification_merge` assumption when fields are carried forward.
  - `tests/test_bernie_clarification_merge.py` (new) — 8 focused regression tests: turn-1 stores resolved fields in frame payload; interpreted turn stores all fields; turn-2 merges patient/date/time when reply provides practitioner; NL practitioner name + prior frame; new-reply-wins over prior frame; no merge without prior frame; duration carry-forward prevents default; interpret route writes no Appointment/AuditLog rows.

- Verification run:
  - `py_compile app/routers/appointments.py` — OK
  - `py_compile tests/test_bernie_clarification_merge.py` — OK
  - `pytest tests/test_bernie_clarification_merge.py -v` — 8 passed, 0 failed, 0 errors
  - `git diff --check` — no whitespace errors

- Remaining risks:
  - The clarification merge reads only the *first* `requested_appointment` frame in `context_frames`. If the client sends multiple such frames (e.g. multi-turn history), only the earliest is used. This is intentional (simplest correct behaviour) but should be documented in the API contract if multi-turn threading is added later.
  - Field serialisation uses `str(value)` for all mergeable fields. UUIDs, dates, and times all round-trip correctly through the fake interpreter, but a real Gemini provider may return differently-formatted values that diverge from the stored string on the second turn. Codex should verify this path once a real-provider harness is in place.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint-r2-clarification-merge-semantics.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
