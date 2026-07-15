# Bernie LC4V4D3 Pre-Plan Protected-Support Search Incident

Date: 2026-07-15

Status: contained metadata/support-code search breach; no holdout reuse or
certification authority.

## What happened

After the LC4V4D2 closeout and before authoring the D3 plan, Sol ran a broad
`rg` search intended to locate ordinary Bernie policy/replay implementation
surfaces. The command scoped both `app/services/bernie` and `tests`. It matched
the protected support module `tests/lc4_holdout_support.py` and printed several
generic matching source lines in the terminal.

This violated the explicit rule that protected support modules must not be
opened, listed, or searched. The broad command should have been restricted to
named ordinary-development and runtime files, with protected paths excluded.

## Exposure and containment

- No protected fixture, manifest, seal, receipt, authoring program, or per-case
  report was opened, imported, run, regenerated, or hash-checked.
- No protected case ID, utterance, expected label, or result was deliberately
  requested.
- The terminal did expose generic support-code matches and one generic
  group-shape expression. They will not be repeated in this document or used as
  evidence.
- The exact 20 D3 development-policy cases, their mismatch fields, and their
  observed/expected values had already been enumerated from the ordinary D1
  development diagnostic before the broad search.
- The search output grants no authority to reuse, rerun, infer from, or tune
  against holdouts v1-v4.

## Process correction

For D3 and later work, searches must use exact named ordinary-development files
or explicit allowlisted paths. Broad searches across `tests` are prohibited
while any protected support population exists. D3 planning and any later
review must cite only the ordinary D1/D2 development reports, named runtime
modules, and newly authored D3 evidence.

Because the exposed generic terms were already present in the ordinary D1/D2
development artifacts and the D3 population was frozen before the incident,
ordinary D3 diagnostic planning can continue. The incident does not validate
any protected result and does not change the requirement for Yuri to approve a
new holdout version or explicit reuse policy before future certification.
