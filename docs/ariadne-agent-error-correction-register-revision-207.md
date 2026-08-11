# Ariadne agent error and correction register — revision 207

Date: 2026-08-11

Revision 207 adds AER-0241 and brings the register to 241 bounded incidents.

## AER-0241 — displayed short HEAD was expanded instead of resolved

While drafting the AES-C1 deterministic-gate precommit state, Sol expanded the
displayed `a1a92443` prefix into a nonexistent forty-character value rather
than first capturing the exact repository object ID. The error was detected
before preflight, staging, commit or verifier dispatch. Exact
`git rev-parse HEAD` returned
`a1a924433d6ea9788dcf54bd52bf4f07e3ba8a46`, and the unsubmitted state was
corrected. No receipt or action used the rejected value.

This is a recurrence of the existing short-hash inference signature. The
control remains mechanical: resolve the exact object ID before authoring any
packet or state and interpolate only that captured forty-character value.
