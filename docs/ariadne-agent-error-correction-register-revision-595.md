# Ariadne agent error and correction register — revision 595

<!-- ariadne-agent-error-register-reading
revision: 595
incident_count: 828
new_incident_ids: AER-0821,AER-0822,AER-0823,AER-0824,AER-0825,AER-0826,AER-0827,AER-0828
open_incident_count: 0
-->

This revision note binds eight corrected or contained attempt-005 observations
to the prospective clockwork-projected register. The canonical JSON register
and pattern report remain clockwork-owned. One clockwork tick advances the
register once, irrespective of the number of observations.

## AER-0821

The first read-only attempt-005 absence check addressed non-existent
`disposable_root` and `evidence_root` properties instead of the controller's
actual `attempt_root` and `evidence_root` coordinates. The query failed before
any preparation or process activity. The corrected query consumes the exact
exported configuration keys.

## AER-0822

The first Node-process absence query searched a broad command-line string and
matched the PowerShell observation command itself. The result was not used as
an admission fact. All subsequent process readings filter exact `node.exe`
processes and then the Harness, broker, attempt-root or package coordinates.

## AER-0823

The first widened attempt-005 packet included attempt 004's deliberately
live-latch-bound provider-free selector. It failed because the latch correctly
named attempt 005. The exact historical applicability record now deselects
that one selector together with the two already-known pre-repair digest
selectors; all 97 widened and 219 admission tests passed.

## AER-0824

The first draft of the attempt-005 postterminal test contained an accidental
dead conditional around the baseline digest assertion. It was removed before
test execution, staging or acceptance, leaving one direct exact-digest
assertion. The final postterminal packet passes.

## AER-0825

The accepted custom runner's post-HMR catch converts every pre-request
exception to the generic `CUSTOM_RUNNER_FAILURE` code. Attempt 005 therefore
proved HMR and runner activation but could not distinguish service, preset,
agent-setup, initial-idle or follow-up failure. The consumed attempt is
contained with no retry; the successor tranche is provider-free and must add a
closed sanitized stage diagnostic before any later occupied attempt.

## AER-0826

The first pre-commit incident-bearing closeout intent used the descriptive
category `orchestration_failure`, which is outside the register's closed
category vocabulary. Direct schema admission rejected the draft before commit
or publication. The runner diagnostic observation now uses the admitted
`harness_failure` category, and the pre-commit admission is rerun on the full
intent.

## AER-0827

The first postpublication regression packet retained attempt 005's
prelaunch-only provider-free check after clockwork had correctly moved the
active latch to the successor. That one selector failed and every other one
passed. The closeout generation was rolled back byte-exactly; both command
manifests now exclude the historical live-latch selector and retain the
postterminal, register, clockwork, active-latch and baton checks.

## AER-0828

The first rollback command incorrectly supplied `--intent`, although rollback
selects the recorded predecessor generation and accepts no intent argument.
Argument parsing rejected the command before state change. The corrected
`--rollback` invocation completed byte-exactly at lease 122, and its receipt is
preserved.
