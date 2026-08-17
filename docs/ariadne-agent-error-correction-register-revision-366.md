# Ariadne agent error and correction register — revision 366

Date: 2026-08-18

Timestamp: 2026-08-18T08:54:38+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 366 adds AER-0417. The first successor preplanning receipt correctly
rejected `high` as a parallelism-leverage label for both the planned DeepSeek
lane and reserved Gemini lane. The harness admits the semantic vocabulary
`positive`, `required_independence`, `neutral` and `negative`.

The correction uses `positive` for the bounded implementation package and
`required_independence` for the exact-candidate veto, preserves the failed
receipt evidence, and reruns preflight before any plan freeze or dispatch.

## Population

- incidents: 417;
- corrected or explicitly contained: 417;
- open: 0;
- latest id: `AER-0417`.

No worker, provider, product source, data, deployment or protected ref opened.
