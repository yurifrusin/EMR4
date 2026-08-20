# Ariadne agent error and correction register — revision 570

Date: 2026-08-20

This revision records three corrected procedure incidents from the DeepSeek
native Harness provider-free complete-composition native-boot recovery. The
canonical machine register now contains 670 incidents and none is open.

## AER-0668 — unadmitted mock-Node tests in an execution-sensitive tranche

Sol ran a widened neighbouring suite before and after the sole native boot.
Three historical tests in each run started synthetic Node drivers even though
the frozen plan prohibited Node from deterministic checks and unit tests. The
drivers did not execute `lib/bin.js`, `--profile headless`, the Harness or
provider code and did not change the immutable terminal, but their six process
starts were outside the admitted test boundary.

Correction: the verifier and closeout manifests excluded the three exact
modules. Future execution-sensitive manifests must statically classify
`subprocess`, `Popen` and resolved Node launch sites and exclude them unless the
frozen plan explicitly admits their executable boundary and count.

## AER-0669 — verifier substituted the wrong incident module names

Gemini correctly adjudicated AER-0668 as a contained P3 procedure incident but
named three nearby non-spawning test modules. Direct source evidence shows the
actual modules were the effective-tool native-boot proof, HMR-boot proof and
preterminal-observable recovery-boot tests.

Correction: Sol preserved the first immutable veto, corrected the exact names
in acceptance and closeout, and did not spend a second provider call on a
narrative-only restatement. Future incident-review packets must bind exact
filenames or identifiers and returned receipts must echo them without
substitution before acceptance.

## AER-0670 — next-operation legacy boundary token omitted

The first clockwork publication expressed the next default-off authority with
narrower controls but omitted the exact compatibility token
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`.
The retained 630-test postpublication session found one exact current-baton
consistency failure.

Correction: lease 58 is preserved and rolled back byte-exactly at lease 59.
The corrected intent adds the exact token. Future closeouts must validate the
prospective next latch against the complete compatibility-boundary subset, not
only semantically equivalent tranche-specific wording.

All three incidents have `control_added` corrections and `corrected` status. They do
not reopen the sole successful Harness attempt, authorise a retry, or change
any product, data, production, deployment, Pages or protected-ref boundary.
