# Check-in start/attach diagnosis — lay and technical closeout

Date: 2026-08-23

Status: `accepted`

## Lay summary

We found the specific reason the last database rehearsal never started. The
command asked Docker to use an option that this version of `docker start` does
not support. Docker rejected the command while the disposable container was
still merely created, which exactly matches the safe failure record from
attempt 006.

This is genuine forward movement rather than another database circle. The
diagnosis needed only two read-only Docker information readings. It created no
container, started no database, made no provider request and did not retry the
failed attempt.

The next step is small: remove that one unsupported option and prove, with
deterministic tests, that attachment, stdin, signal handling and cleanup still
have the required shape. That repair is not yet a licence to run attempt 007;
any later database rehearsal will still need its own plan and one-run gate.

## Technical summary

- Coordinate: `cli_option_surface_mismatch`.
- Exact harness argv:
  `<executable> start --attach --interactive --sig-proxy=false <container_id>`.
- Docker client/server: `29.5.3` / `29.5.3`.
- `docker start --help`: `--attach=true`, `--interactive=true`,
  `--sig-proxy=false` in the advertised-surface reading (meaning absent).
- Attempt-006 projection: host attachment exited nonzero; stdin remained open;
  OCI status remained `created`; running remained false.
- Evidence SHA-256:
  `924ca23b361770fa31037232aa342e39c377e91685ac7137d1bb4da264647bb0`.
- Current validation: 58 focused postterminal/lineage tests passed after 10
  initial focused tests; Ruff, compile, schema and canonical JSON passed.
- Docker object/database/provider/product counts: all zero.

The next operation is
`raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-conformance-repair`.
It is static/provider-free and may change only the unsupported argument plus
its exact conformance bindings. Protected refs and all product/ordinary-
practice surfaces remain closed.

## Efficiency reading

Clockwork prevented the expensive failure mode: there was no blind Docker or
database retry. The remaining procedural friction was a single validation
selection rerun after old preterminal/hash assertions were mixed with current
postterminal tests, plus two local overly literal test predicates. These are
good candidates for generated lifecycle-aware validation manifests, and they
did not alter canonical evidence or external state.
