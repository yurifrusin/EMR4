# Check-in server start argv sig-proxy removal conformance repair

Date: 2026-08-23

Timestamp: 2026-08-23T02:45:30.9661732+10:00 (Australia/Brisbane)

Status: `passed`

Exact repair source:
`022d780726c74cb285d5b626cd004821b4e5ff47`

Attestation SHA-256:
`73d5773d3662509ec2cdb8d8f109651b77ef79be42f5b641f07e36d7ca8bcf91`

## Result

The repair removes exactly one token, `--sig-proxy=false`, from the accepted
database harness's Docker start argv. The exact post-repair vector is:

`<executable> start --attach --interactive <container_id>`

The pre-repair and post-repair harness SHA-256 values are
`839a9a17b22aa132ea5bddf878f59f4741412cb1ee464020f34aa2aefbdff8e2`
and
`1b7ec51cfd97fa6a54398ab0587acf79d3b0b8d34fa5609a2bad2abe17e91c16`.
Byte comparison against the accepted diagnosis source proves zero other
harness changes.

## Deterministic conformance

The exact Popen profile remains `cwd=ROOT`, `stdin=PIPE`,
`stdout=DEVNULL`, `stderr=DEVNULL`, `shell=false`. A deterministic attachment
fake observed one newline-terminated two-line payload write, one flush and
stdin remaining open with no normal-path terminate or kill.

The unchanged teardown fake then closed stdin once, terminated the attachment
once, waited once, did not kill and observed attachment absence. Docker's
accepted help evidence says `--attach` forwards signals by default; the repair
adds no new signal operation. Any propagation is confined to the existing
bounded teardown, where captured-container termination is intended and exact
resource cleanup still owns the final state.

Historical diagnosis bytes remain unchanged. Its exact source still contains
the invalid token and its accepted evidence is not reclassified. Its live-
source checker now correctly fails on source-binding drift, while historical
postterminal tests read the full committed diagnosis source.

## Closed boundary

The repair ran no Docker metadata or object command, created no Docker object,
started no PostgreSQL process, executed no SQL/database attempt, called no
provider and released no product or ordinary-practice effect. Attempt 007 is
not authorised.

The next admissible operation may freeze a separately named one-run attempt
007 only after this repair receives closeout acceptance and a fresh
five-source preexecution receipt plus distinct clockwork checkpoint. It may
not reuse or resume attempts 001 through 006.
