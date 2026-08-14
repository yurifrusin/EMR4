# Sol recovery — selected-action-console worker test artifact

Date: 2026-08-14

Timestamp: 2026-08-14T18:05:00+10:00 (Australia/Brisbane)

Status: `recovery_closed`

Parent worker commits:

- `954bbdd7766bc26034427cc85fdcf1211ef39683` — initial admitted test-only candidate;
- `195cd09d2a55edfd4cf675e09c086227e767b0c7` — its one admitted same-lane mechanical correction.

## Preserved rejection

The first integrated execution produced thirteen failures. The product's four
existing route-intercepted suites had already passed 49/49. Exact failure
inspection found four worker-test causes:

1. the assertion lowercased the announcer value but compared it with mixed-case
   `Diary`;
2. a 30-minute current duration used 35 minutes as a target although the
   existing renderer intentionally admits 15-minute deltas, making 45 the
   nearest valid changed target;
3. three focus-return checks omitted the existing asynchronous
   `wait_for_function` used by the accepted field-specific suites; and
4. the static guard expected four literal choice IDs even though the reviewed
   implementation intentionally constructs the frozen IDs from the explicit
   four-action tuple and a single template literal.
5. the busy-dialog case expected cancellation to reset the still-visible field
   control, although the accepted field renderers retain an explicitly
   cancelled draft for staff review; the security invariant is unchanged
   authoritative fixture truth and zero confirmation/write, not erasing that
   visible cancelled value.

The failing run is not recharacterised as worker success. Its two worker
receipts and both commits retain their original identity and claims. The one
same-lane correction is exhausted; no further DeepSeek revision is permitted
for this artifact.

## Sol amendments

Under `docs/ariadne-orchestrator-recovery-lease.md`, Sol changes only
`review/test_reception_one_selected_action_console.py`:

- compare the lowercase announcement with lowercase expected text;
- use the valid 45-minute authored-synthetic target;
- wait for the existing asynchronous focus return before asserting it; and
- bind the static choice guard to the explicit four-action tuple plus its one
  ID template; and
- replace the unsupported post-cancel control-reset assertion with exact
  unchanged status, start, duration and practitioner fixture truth alongside
  the existing zero-confirm and zero-raw-write assertions.

No scenario, route count, command-trace requirement, field family, responsive
case, evidence label or product assertion is removed. Product source is not
changed to satisfy these harness defects.

## Closure gate

The lease may close only after Python compilation, Git whitespace, the complete
recovered new browser contract and the four existing browser suites pass. The
fresh exact-candidate Gemini veto remains separately required after the full
deterministic and rendered gate.

## Closure result

- Python compilation and Git whitespace pass.
- The complete recovered console contract passes 23/23 collected cases.
- The four original field-specific browser suites pass 49/49.
- No product source was changed during the Sol test recovery.

No new agent-error-register incident is opened. These were ordinary candidate
test defects discovered by the expected first integrated execution, which the
register's inclusion rule expressly excludes. The worker transport completed,
its worktree and ownership postconditions were clean, its receipt claimed no
acceptance and no scope breach, evidence conflict or protected-boundary breach
occurred. The immutable worker receipts, commits, failing pytest output in this
recovery record and Sol diff preserve the failure without misclassifying it as
a qualifying process incident.
