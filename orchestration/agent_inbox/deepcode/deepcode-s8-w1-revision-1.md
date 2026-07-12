# S8 W1 Revision 1 - Test and Behavior Repair

Resume the same W1 implementation in this worktree. The first completion is
rejected. Do not discard the existing candidate.

Sol ran:

`C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest review\test_taskpane_diary_launch.py -q --tb=short`

Result: 5 passed, 8 failed.

Failures:

- five error-message tests call `Page.evaluate()` with too many positional
  arguments;
- three visibility/retry tests cannot make `#diary-error` visible;
- the 12007 test therefore does not prove a bounded retry.

Repair the implementation and tests so they test actual browser behavior and
all focused tests pass. Do not weaken assertions to manufacture a pass. Confirm
the retry test proves exactly one automatic retry after 12007 and no loop.
Re-run the focused suite using the shared venv command above, plus `node
--check` and `git diff --check`.

Update the existing completion artifact with corrected exact counts and any
changed risk assessment. Commit all owned candidate files and the artifact on
`deepcode/s8-w1-launch`; record the real candidate commit. End with
`STATUS: complete`.

No scope expansion and no integration authority.
