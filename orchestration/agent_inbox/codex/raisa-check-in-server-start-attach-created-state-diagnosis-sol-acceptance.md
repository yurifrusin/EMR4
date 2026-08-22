# Sol acceptance — check-in server start/attach created-state diagnosis

Date: 2026-08-23

Timestamp: 2026-08-23T02:22:13.0856700+10:00 (Australia/Brisbane)

Decision: `accepted`

GPT Sol accepts the provider-free read-only diagnosis at exact reviewed source
`2ab8707e2ac03be3b1a4c9c538dfa45382d7d92d` and evidence SHA-256
`924ca23b361770fa31037232aa342e39c377e91685ac7137d1bb4da264647bb0`.

The exact closed coordinate is `cli_option_surface_mismatch`. Docker 29.5.3
`start --help` advertises the harness's `--attach` and `--interactive`
options, but not the supplied `--sig-proxy=false` option. This is sufficient
to explain the attempt-006 nonzero host process with unchanged `created` OCI
state without attributing a later Docker-engine, container-init or PostgreSQL
failure.

The diagnosis named no Docker object, created none, started no PostgreSQL
process, executed no SQL/database attempt, called no provider and released no
product or ordinary-practice effect. Attempts 001 through 006 and the database
harness remain immutable.

Sol accepts removal of the unsupported start-argv token as the narrowest
future repair surface. The repair is not implemented here, and attempt 007 is
not authorised. The next admissible work is a separately frozen provider-free
static conformance repair that validates source, signal, attachment, stdin and
cleanup semantics without a Docker object or database run.
