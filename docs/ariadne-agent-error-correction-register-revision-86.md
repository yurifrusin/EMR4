# Ariadne agent-error register revision 86

Date: 2026-08-07

Status: disposable PostgreSQL plan recovery active

## AER-0093 is contained

The first exact-HEAD Gemini 3.6 Flash/high plan challenge returned `pass` but
missed two material mechanics inside its expressly assigned PostgreSQL
atomicity challenge. It accepted a rollback case scheduled after successful
creation of cluster-scoped roles in another database, and it accepted plain
stdin with psql `--single-transaction` even though that option requires a
`-c`/`-f` input.

Sol rejected the pass before Docker or database contact. The recovered plan
runs the failed installation first while accepted roles are absent, checks
database-local fabric and cluster-wide role absence, then runs success. Every
artifact stream now uses exact `--file=-`, `ON_ERROR_STOP=1` and
`--single-transaction`. A genuinely fresh exact-HEAD replacement veto is
mandatory.

The review also said there were zero provider calls while its own receipt
records one Antigravity verifier call. That sentence is treated only as an
overbroad wording error; the authoritative boundary is zero provider *product*
calls and the review transport remains transparently recorded.

## Register posture

Revision 86 contains 93 bounded incidents: 75 agent-behavior observations,
five harness failures, five repository defects and eight transport timeouts.
No incident is open. AER-0093 resembles AER-0085's earlier exact-contract
underreport but is not a formally linked attempt pair and uses a distinct
recurrence signature because the missed mechanics and prevention control
differ.

This register change supplies no Docker, PostgreSQL, SQL execution, migration,
database/source, product/patient data, application/runtime, command, provider
product, deployment, production, release, Pages or protected-ref authority.
