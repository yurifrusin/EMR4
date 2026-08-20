# Ariadne agent error and correction register — revision 575

Date: 2026-08-20

<!-- ariadne-agent-error-register-reading
revision: 575
incident_count: 706
new_incident_ids: AER-0701,AER-0702,AER-0703,AER-0704,AER-0705,AER-0706
open_incident_count: 0
-->

This revision records six corrected control incidents exposed while joining the
accepted DeepSeek Harness preset service to the effective-tool guard. None
contacted a model or provider, accessed product data or moved protected refs.
None remains open.

## AER-0701 — literal vocabulary checks produced false boundary failures

Several early deterministic guards treated audit literals and package names as
runtime behavior. In particular, the installed `@deepseek-ai/dsh-scope`
package name was initially counted as a provider boundary, and descriptive plan
text and post-root guard failures were classified from token presence rather
than execution structure.

Correction: structural source checks now distinguish imports and launch sites
from audit strings, while tests bind the actual boundary fields and terminal
classification. The final twelve-command ledger passes without relaxing the
provider-free boundary.

## AER-0702 — review manifests depended on fallible implementation-name recall

Successive draft review commands named a nonexistent checkpoint loader, used
over-broad nested schemas and matched the `subprocess.Popen` type annotation
rather than the launch statement. These were orchestration vocabulary errors,
not candidate behavior failures.

Correction: the final manifest uses exact inspected symbols, closed schemas and
the literal launch assignment. The shell-free validator owns these mechanical
facts; Gemini owns only the semantic veto.

## AER-0703 — a staged whitespace failure did not stop the commit command block

`git diff --cached --check` reported trailing whitespace, but a semicolon-
separated PowerShell block continued to commit because the native exit code was
not asserted. The content was corrected immediately in a descendant commit.

Correction: staged checks and commits are separate commands, and a commit is
issued only after an independently observed zero exit code. This repeats the
existing machine-control lesson rather than adding a new ceremonial step.

## AER-0704 — attempt 001 had conflicting installation-root ownership

The controller created `installation/proof` before the accepted offline
installer exclusively claimed `installation`, so the first authorised identity
failed before checkpoint consumption or native process creation. The original
controller also lacked a reliable prelaunch terminal for that failure class.

Correction: the failure is preserved as immutable zero-native-process evidence;
materialisation owns the installation root before proof creation, and every
prelaunch exception now maps to a sanitized terminal path.

## AER-0705 — attempt 002 coupled npm timeout, child ownership and cleanup

The accepted offline npm materialiser exceeded its bound and left one exact npm
child holding the disposable root. Cleanup then raised `PermissionError` before
the controller could publish its intended terminal. No native Harness process,
agent or provider request started.

Correction: the exact child was identity-verified and terminated, the exact
disposable root was removed, and attempt 003 eliminated npm from the proof by
copying a content- and lock-bound accepted package tree with zero materialiser
processes. Cleanup is bounded and terminal publication survives failure.

## AER-0706 — the first recovery deletion command crossed shell-safety bounds

The initial cleanup procedure combined PowerShell enumeration, identity checks
and recursive deletion in a form rejected by the command safety layer; a later
`Remove-Item` attempt was also denied. No broad or unresolved deletion ran.

Correction: process identity, resolved absolute target containment and target
absence were checked separately. The already verified temporary root was then
removed by one explicit language-local operation. Future cleanup keeps target
resolution and deletion in one bounded implementation and never uses a computed
broad path.
