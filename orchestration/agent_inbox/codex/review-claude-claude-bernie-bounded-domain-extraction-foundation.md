# review-claude-claude-bernie-bounded-domain-extraction-foundation

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-bernie-bounded-domain-extraction-foundation` |
| Status | queued |

## Review Request

claude-bernie-bounded-domain-extraction-foundation ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: added the bounded `app/services/bernie/` package with facades for the existing interpreter, patient context, evidence, normalizer, pilot gate, and transition table modules; added `session.py` persistence-shaped session/event contract scaffolding; added `capabilities.py` registry skeleton; updated `app/routers/appointments.py` imports to use the bounded package; added `tests/test_bernie_domain_package.py`.
- Verification run: `python -m py_compile` over `app/services/bernie/*.py` passed; `python -m pytest tests/test_bernie_domain_package.py -q` passed (25 tests); `git diff --check` passed. The requested broader Bernie suite was also run; it reached 100/105 passing but `tests/test_slot_search_proposal.py` failed on pre-existing local test DB fixture contamination (`users_email_key` duplicate `gp@test.local` and deleted ORM user objects), not on the new Bernie domain assertions.
- Remaining risks: this is a foundation extraction only. Legacy flat modules remain the implementation, so later sprints still need to move logic behind the bounded package, consolidate temporal policy, and decide PHI retention/concurrency policy before adding persisted server-side Bernie sessions.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-bernie-bounded-domain-extraction-foundation.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
