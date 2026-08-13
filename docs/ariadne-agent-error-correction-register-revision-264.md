# Ariadne agent error and correction register — revision 264

Date: 2026-08-14

Timestamp: 2026-08-14T09:12:10+10:00 (Australia/Brisbane)

Revision 264 records AER-0302. The register now contains 302 bounded known
incidents, all corrected.

AER-0302 records recurrence of the Python package-script path invocation
pattern during a local Antigravity help inspection. Direct filesystem-path
execution stopped immediately with `ModuleNotFoundError` before the help parser
ran. No Antigravity project, model, provider call or external side effect
started. The corrected `python -m scripts.ariadne_antigravity --help`
invocation completed normally.

For the remainder of this tranche, every repository Python harness is invoked
only as `python -m scripts.<module>` from the repository root. Filesystem paths
remain data arguments, not Python script entry points.

No protected output, prompt, secret, credential, patient, clinical, document or
product-derived value is retained in this revision or its sanitized receipt.
