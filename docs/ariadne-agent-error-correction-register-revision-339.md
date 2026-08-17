# Ariadne agent error and correction register — revision 339

Date: 2026-08-17

Timestamp: 2026-08-17T16:57:03.8650139+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 339 retains 386 bounded known incidents. No incident is open.

- AER-0385 records the rejected preplanning receipt caused by invented Gemini
  leverage value `positive_independence`; no plan or worker followed it.
- AER-0386 records the still-unaccepted correction entry's use of non-schema
  incident stage `planning` and a later invalid one-way peer link. The register
  validator rejected both drafts before tests or a corrected receipt.
- The canonical entry now uses admitted stage `dispatch`, and the corrected
  runtime state uses admitted leverage `required_independence`.

## Boundary

Both corrections affect orchestration evidence only. They grant no product,
data, provider, database, deployment, release, Pages or protected-ref
authority.
