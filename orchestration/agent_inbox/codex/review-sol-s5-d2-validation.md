# S5 D-2 Orchestrator Validation

Date: 2026-07-12

D-2 completed under the unchanged allocation with no artifact deadline. The
typed PTY receipt recorded artifact observation, turn completion, mailbox event,
and confirmed process cleanup.

Sol validated the proposed terminal-status rollback test with:

```text
.venv/Scripts/python.exe -m pytest -p tests.conftest review/test_raw_status_terminal_rollback_guard.py -q
```

Result: one allowed non-terminal transition passed; two terminal-to-active
expectations failed because the raw PATCH route returned `200`, confirming the
observed behavior for `Completed -> Booked` and `DNA -> Confirmed`.

This proves current behavior, not yet that it is incorrect product policy. The
test remains a failing-test proposal. A-1 usability evidence and the existing
S5 conditional-repair gate must be considered before selecting or implementing
the sprint's optional single repair.
