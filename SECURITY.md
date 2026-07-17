# Security Policy

## Project status

EMR4 Centaur is under active development and is not yet approved for
production clinical use. Security fixes are applied to the current `master`
branch; no released version currently receives a separate maintenance stream.

## Reporting a vulnerability

Please use GitHub's **Report a vulnerability** function in this repository's
Security tab. Private vulnerability reporting is enabled. Do not disclose
suspected vulnerabilities, credentials, patient information, or exploit
details in a public issue.

Include, when safe and available:

- the affected component and revision;
- reproduction conditions and required privileges;
- potential impact and data involved;
- a minimal proof of concept without real patient data; and
- any mitigation or fix you have already tested.

The project will acknowledge the report, validate scope and reachability,
coordinate remediation and disclosure, and preserve an evidence record. A
report is not considered resolved until the fix and relevant regression or
security tests have been verified.

## Security boundaries

The backend remains authoritative for clinical and diary data, identity,
authorization, collisions, confirmations, writes, and audit. LLM/provider
execution, protected evaluation evidence, historical diary material, and
product write authority are separately gated. Security reports do not grant
access to patient data, protected holdouts, provider credentials, or production
systems.

For current engineering controls and known structural work, see
`docs/security/emr4-secure-sdlc-review-2026-07-17.md`.
