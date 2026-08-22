# Check-in server start/attach created-state failure-coordinate diagnosis

Date: 2026-08-23

Status: `passed`

Operation:
`raisa-provider-free-read-only-check-in-server-start-attach-created-state-failure-coordinate-diagnosis`

Exact diagnostic source:
`7cd4d8069fc3983cdb4d2e80384e0f663e917c4e`

Evidence SHA-256:
`924ca23b361770fa31037232aa342e39c377e91685ac7137d1bb4da264647bb0`

## Conclusion

The closed coordinate is `cli_option_surface_mismatch`.

The exact `_start_attached` source constructs this safe-profile argument
sequence:

`<executable> start --attach --interactive --sig-proxy=false <container_id>`

Local Docker client and server version 29.5.3 returned zero for the two frozen
read-only commands. `docker start --help` advertised `--attach` and
`--interactive`, but did not advertise `--sig-proxy`. The help output digest is
`1eb9d7c53bb0c4868463802b84c0a1998ec0dd63f17a4c17c85ca197d5b657cc`;
the raw output is not retained in canonical evidence.

That exact option mismatch explains the attempt-006 safe coordinate: the host
Docker process exited nonzero while the captured OCI state remained
`created`, `running=false`, and stdin remained open after delivery. The CLI
could reject its option surface before a successful engine start transition,
so no further Docker, entrypoint or PostgreSQL cause is required to explain
the observed terminal.

## Observation, inference and non-claim

Observed:

- the exact source supplies `--sig-proxy=false` to `docker start`;
- the installed CLI's `docker start` help does not advertise that option;
- attempt 006 retained `attachment_process=exited_nonzero` and OCI
  `status=created`, `running=false`; and
- readiness and every transaction stage remained unreached.

Bounded inference:

- the start/attach command is syntactically outside the installed CLI's
  advertised option surface; and
- removing that unsupported token is the smallest source repair capable of
  allowing the existing admitted `--attach --interactive` path to proceed.

Not claimed:

- no repaired command has run;
- default signal-forwarding and cleanup semantics have not yet been accepted;
- no container or PostgreSQL behavior after repair has been observed; and
- no attempt 007, database success, product readiness or ordinary-practice
  admission follows from this diagnosis.

## Narrow repair boundary

The next dependency-satisfied tranche is
`raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-conformance-repair`.
It may remove only the unsupported `--sig-proxy=false` argument and update the
exact source/static conformance bindings needed to validate the resulting
`docker start --attach --interactive <container_id>` vector. It must
deterministically verify signal-forwarding, attachment lifetime, stdin and
cleanup expectations without creating a Docker object or starting PostgreSQL.

Only after that repair is independently accepted may a separately named
attempt-007 plan, five-source preexecution receipt and one-run checkpoint be
considered.

## Closed execution reading

This diagnosis executed two read-only metadata commands, named zero Docker
objects, created zero Docker objects, started zero PostgreSQL processes,
executed zero SQL/database attempts, made zero provider requests, released
zero ordinary admissions and produced zero product effects. Attempts 001
through 006 and the database harness remained byte-immutable.
