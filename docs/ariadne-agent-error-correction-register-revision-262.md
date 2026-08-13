# Ariadne agent error and correction register — revision 262

Date: 2026-08-14

Timestamp: 2026-08-14T08:19:20+10:00 (Australia/Brisbane)

Revision 262 records AER-0300. The register now contains 300 bounded known
incidents, all corrected.

AER-0300 records a second recurrence of the PowerShell statement-inside-
expression parser trap during post-compaction read-only Git ref verification.
The shell rejected the command before any statement executed, so no file,
repository ref, runtime, provider, database or product state changed. The
corrected probe executed every Git read and merge-base check as a separate
statement, captured `LASTEXITCODE` in named scalar variables, and verified the
task ancestry plus exact protected refs before the fresh five-source receipt
passed.

The prevention control is strengthened for the remainder of this tranche: no
Git command, semicolon or conditional may appear inside a PowerShell assignment
expression. Ref and worktree probes use newline-separated scalar statements
only.

No protected output, prompt, secret, credential, patient, clinical, document or
product-derived value is retained in this revision or its sanitized receipt.
