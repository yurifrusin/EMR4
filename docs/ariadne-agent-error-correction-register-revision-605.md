# Ariadne agent error and correction register — revision 605

Date: 2026-08-22

Timestamp: 2026-08-22T05:42:33.3788104+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 605
incident_count: 890
new_incident_ids: AER-0881,AER-0882,AER-0883,AER-0884,AER-0885,AER-0886,AER-0887,AER-0888,AER-0889,AER-0890
open_incident_count: 0
-->

This revision binds ten corrected or contained operator/harness incidents
from the failed-closed sanitizer tranche. The clockwork owns the canonical JSON
register and pattern report.

## AER-0881

The first read-only source lookup appended a logical evidence path directly to
the package cache root and found no file. The accepted predecessor contract
contains the intervening package-seed and `node_modules/@deepseek-ai` path. No
source or process was touched. Descendants now copy the physical seed path from
that contract rather than infer it from logical binding names.

## AER-0882

A focused plan assertion searched raw Markdown for a phrase split by line
wrapping. Pytest rejected it before Node execution. The correction normalizes
document whitespace before prose assertions.

## AER-0883

The first whitespace correction changed only the immediately failing assertion
and left the adjacent `null detail` assertion on raw text. The next test run
failed for the same representation reason. The completed correction uses one
normalized reading for every plan-prose assertion.

## AER-0884

Attempt 001 placed an all-or-nothing expected-vector comparison inside the
fixture and the controller retained neither a safe vector nor a process
envelope. The orchestrator then described exit 2 from fixture source as though
it were observed. The immutable attempt record now states only the observed
outer terminal and marks exit 2 as inferred, not factual.

## AER-0885

Attempt 002 removed the internal comparison but the controller still checked a
nonzero exit before retaining numeric exit or stream sizes. Its safe terminal
remained insufficiently traceable. Attempt 003 added a content-free process
envelope before semantic admission.

## AER-0886

All three processes were launched with a completely empty Windows environment,
diverging from the accepted repository Node fixture convention. Attempt 003
observed exit 134, zero stdout and 715 stderr bytes. The empty environment is a
source-supported recovery hypothesis, not a proven cause. The successor admits
only five required Windows runtime keys and no ambient secrets.

## AER-0887

The first negative-evidence test synthesized “Exactly one successor process”
instead of quoting the recovery plan's authored wording. Pytest rejected it.
The corrected assertion binds the normalized exact phrase “one local Node
process in this successor.”

## AER-0888

The first clockwork closeout intent used descriptive values such as
`uncommitted_candidate`, `committed_failed_candidate` and `medium` outside
the incident schema's closed vocabularies. Clockwork `--check` rejected the
intent at `tick_incident_candidate_state` before command execution,
generation, publication or canonical mutation. The corrected intent copies the
live enum values from the validator and records this rejection in the same
atomic revision. Future closeout construction reads the typed incident enums
before authoring observations rather than translating descriptive prose into
new labels.

## AER-0889

After adding AER-0888, the next intent draft incorrectly advanced the
prospective register revision from 605 to 606. A clockwork publication advances
the register revision once per atomic projection while its incident count
advances by the number of accepted observations. Clockwork `--check` rejected
the mismatched path at `tick_incident_revision_path` before commands,
generation, publication or canonical mutation. The corrected reading remains
revision 605 and advances the prospective incident count from 880 to 889.
Future intent construction derives both values from the clockwork's canonical
predecessor plus one projection and the exact observation count.

## AER-0890

The first candidate commit command placed `git diff --cached --check` and
`git commit` sequentially in one PowerShell process without an explicit exit
check. The whitespace check reported four new blank lines at end of file, but
PowerShell continued and created a local, unpushed commit. No publication or
canonical clockwork mutation occurred. A follow-up explicit-path repair removes
the blank lines, records this incident and reruns the final check with an
explicit `$LASTEXITCODE` stop before any push. Future multi-command
verification/commit sequences must guard the verification exit explicitly.
