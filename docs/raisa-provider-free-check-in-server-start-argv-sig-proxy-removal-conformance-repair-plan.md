# Provider-free check-in server start argv sig-proxy removal conformance repair plan

Date: 2026-08-23

Timestamp: 2026-08-23T02:37:52.8034054+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`fb195aeb4d5ef9f7e25ce5def7656a165cc1b293`

Accepted diagnosis source:
`2ab8707e2ac03be3b1a4c9c538dfa45382d7d92d`

Protected source:
`2e34bdad732fdab32fbf778280b3d3c70d66d602`

Operation:
`raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-conformance-repair`

Target result:
`raisa_provider_free_check_in_server_start_argv_sig_proxy_removal_conformance_repair_pass`

Reasoning level: High is sufficient because the accepted diagnosis has fixed
one exact source defect and this plan permits only its mechanical removal plus
tightly coupled deterministic conformance.

## Authority and exact defect

The accepted read-only diagnosis proves that Docker client/server 29.5.3
`start --help` advertises `--attach` and `--interactive` but not
`--sig-proxy`. The exact current `_start_attached` vector nevertheless supplies
`--sig-proxy=false`. Its option-surface mismatch explains the attempt-006
nonzero host process with unchanged OCI `created`, `running=false` state.

Yuri's standing uninterrupted-development authority admits the smallest
dependency-satisfied repair. The database harness is exact pre-repair SHA-256
`839a9a17b22aa132ea5bddf878f59f4741412cb1ee464020f34aa2aefbdff8e2`.
The accepted diagnosis evidence is exact SHA-256
`924ca23b361770fa31037232aa342e39c377e91685ac7137d1bb4da264647bb0`.

## Narrow repair

The only executable harness edit is deletion of the literal
`"--sig-proxy=false",` element from `_start_attached`'s `subprocess.Popen`
argv. The resulting exact vector is:

`<executable> start --attach --interactive <container_id>`

No other harness expression, constant, function, timeout, credential write,
stdin lifetime, readiness predicate, transaction path, teardown path, evidence
shape or output path may change.

Exact conformance bindings and tests may change only where required to:

- bind the new five-element source vector and new harness SHA-256;
- preserve the accepted diagnosis against its historical source commit rather
  than falsely requiring the mutable current harness to keep the defect;
- prove `stdin=PIPE`, `stdout=DEVNULL`, `stderr=DEVNULL`, `shell=False` and
  `cwd=ROOT` remain exact;
- prove each credential line is encoded, written and flushed while stdin stays
  open until the existing sole teardown owner closes it;
- prove normal control and cleanup do not synthesize or send a host signal;
- record that Docker's advertised `--attach` default forwards signals while
  the harness adds no unsupported signal option; and
- prove the existing ownership-checked teardown still terminates/waits for the
  attachment and removes captured resources on success or failure.

Historical diagnosis contract/evidence/report bytes and attempts 001 through
006 remain immutable. A closed diagnostic executable may fail its live-source
check after the accepted repair; historical conformance must read its exact
Git source instead of weakening the old binding.

## Provider-free execution boundary

No Docker object command is authorised. The only optional Docker subprocesses
are the already admitted fixed metadata readings `docker.exe version` and
`docker.exe start --help`; neither may name an object. All Popen, stdin,
poll/wait/terminate, signal and cleanup behavior is exercised through
deterministic fakes or static AST/source inspection.

No container, network, image, volume, PostgreSQL process, SQL, database,
provider, browser, product route or application runtime may be created or
started. No caller-supplied command, object identity, output path or free-form
state is accepted.

## Deterministic proof

One source-owned repair contract and attestation schema must close:

1. exact pre-repair diagnosis and full-Git ancestry bindings;
2. exact one-token diff and post-repair argv;
3. Docker 29.5.3 help-surface booleans for attach, interactive and absent
   sig-proxy;
4. unchanged Popen stream/cwd/shell relations;
5. credential write/flush and open-stdin lifecycle;
6. default signal-forwarding observation with zero harness-generated signals;
7. one sole teardown owner and exact attachment/resource cleanup relations;
8. historical diagnosis immutability and source-commit conformance;
9. zero Docker object, PostgreSQL, database, provider, product and ordinary
   effects; and
10. repair implemented but attempt 007 still unauthorised.

Hostile tests must mutate every argv position and option, Popen stream, shell,
cwd, write, flush, close, poll, wait, terminate, signal and teardown predicate.
They must reject short Git identifiers, source/hash drift, old diagnostic
reclassification, raw output retention, object-bearing Docker commands,
attempt-007 language and product/provider authority.

## Acceptance

Pass requires:

- a fresh five-source receipt with all three lane dispositions;
- exactly one executable source-line deletion and no other harness semantic
  diff;
- one closed canonical repair attestation proving every deterministic item;
- focused repair, diagnosis-postterminal and lifecycle lineage tests pass;
- Ruff, compile, JSON/schema and `git diff --check` pass;
- the repaired candidate contains no `--sig-proxy` start token and no Docker
  object or PostgreSQL action occurred; and
- protected refs, product surfaces and every unrelated untracked path remain
  unchanged.

The repair may be accepted without Gemini because it is one diagnosed token,
fully provider-free and exhaustively source/fake testable. Reassess Gemini only
if deterministic evidence reveals a material alternative or contradiction.

## Parallelism assessment

- **DeepSeek native Harness:** `declined`, negative leverage. The worker lane
  is paused and packet/review overhead exceeds the one-token serial repair.
- **Gemini:** `declined`, neutral leverage before a candidate. Deterministic
  exact-diff and hostile conformance own this repair; reassess on contradiction
  or a materially broader candidate.
- **Native subagents:** `declined`, negative leverage. Developer policy
  prohibits proactive delegation and source plus conformance are tightly
  coupled.
- **GPT Sol:** owns plan, repair, deterministic proof, acceptance, clockwork
  and Git.

## API Spine, protected and continuation boundaries

This security/audit rehearsal changes no REST/OpenAPI command, GraphQL read
model, async contract, route, application schema, migration, feature flag,
authored-synthetic allowlist, action grammar, first-party client, waiting-area
behavior or product configuration. Dedicated check-in remains default-off;
generic status does not gain `Arrived`; no ordinary practice is enabled.

No product, patient, appointment, clinical, historical or protected data;
live provider; production runtime; deployment; release; Pages; protected
evidence access; or protected-ref movement is authorised. Local/origin
`master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Closeout uses clockwork as sole canonical governance writer. Sol writes the
paired lay/technical Yuri summary, sends the usual non-PHI Pushover, stages
only explicit paths and preserves `docs/branding/` plus every unrelated
untracked file. Any attempt 007 requires a new operation, frozen plan, fresh
five-source preexecution receipt and distinct one-run checkpoint after this
repair is accepted.
