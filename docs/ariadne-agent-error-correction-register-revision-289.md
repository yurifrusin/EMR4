# Ariadne agent error and correction register — revision 289

Date: 2026-08-15

Timestamp: 2026-08-15T14:34:20+10:00 (Australia/Brisbane)

Revision 289 records AER-0328. The register now contains 328 bounded known
incidents, all corrected or contained by an explicit control.

AER-0328 preserves a command-manifest admission error in the corrected Gemini
review attempt. Sol supplied five unique lowercase command identifiers, but the
evidence gate admits only identifiers matching
`^[A-Z][A-Z0-9_-]{0,31}$`. The Antigravity wrapper therefore rejected
`command[0]` locally before project creation or any provider/model call. It
created no review receipt, and candidate
`bc066a1b639c5c57cc72f2697c063c5842511840` remained clean and unchanged.

Only the five identifiers have been replaced with uppercase admitted tokens.
The exact manifest must now pass `scripts.ariadne_evidence_gate` before a second
distinct corrected pre-verifier receipt is constructed and the fresh occupied
review is attempted.

The durable control is simple: validate every verifier command manifest through
the evidence gate before receipt construction, rather than allowing the
Antigravity wrapper to become its first grammar check.
