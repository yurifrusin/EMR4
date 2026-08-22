# Provider-free check-in server start argv sig-proxy removal conformance repair closeout

Date: 2026-08-23

Timestamp: 2026-08-23T02:48:38.4129265+10:00 (Australia/Brisbane)

Status: `accepted`

Operation:
`raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-conformance-repair`

Exact reviewed source:
`8814d4b5d62885f8f8eca4cf02fe5a49ccdc013b`

## Result

The repair passes. Exactly one executable harness token,
`--sig-proxy=false`, was deleted. Zero tokens were added and byte comparison
against the accepted diagnosis source proves zero other harness changes.

The repaired exact vector is
`<executable> start --attach --interactive <container_id>`. It now lies inside
Docker 29.5.3's accepted advertised start-option surface. The canonical repair
attestation SHA-256 is
`73d5773d3662509ec2cdb8d8f109651b77ef79be42f5b641f07e36d7ca8bcf91`.

## Deterministic proof

The Popen profile remains `cwd=ROOT`, `stdin=PIPE`, `stdout=DEVNULL`,
`stderr=DEVNULL`, `shell=false`. Deterministic fakes prove one payload write,
one flush, stdin open after delivery, zero normal-path terminate/kill, then the
existing teardown's one stdin close, one terminate, one wait, zero kill and
attachment absence.

The historical diagnosis remains exact and is tested against its full Git
source. Its live-source checker now correctly rejects the repaired current
harness rather than weakening or reclassifying old evidence.

Current repair, diagnosis, postterminal and lifecycle validation passes 94/94.
Ruff, compilation, canonical JSON and JSON Schema pass. No Docker metadata or
object command, Docker object, PostgreSQL process, SQL/database attempt,
provider request, product effect or ordinary admission occurred.

## Workflow efficacy

The expensive path was eliminated: the repair needed no database retry and
the executable diff was exactly one deletion. Four low-cost construction
events remained visible. Plan prose initially conflated normal-path signals
with the existing teardown termination; source inspection corrected it before
the code change. A new report test repeated the prior line-wrap sensitivity
and required normalized semantic assertions before the clean 94-test rerun.
One first explicit staging command misspelled a path and Git rejected it before
any staging. The first closeout intent used the descriptive stage `planning`;
the clockwork rejected it before publication and accepted the registered
`dispatch` value on the same transaction.

These events did not change the repair, attestation, external state or
canonical governance. They point to the next workflow controls: AST-derived
lifecycle prose, a shared normalized-Markdown predicate, staging generated
from the exact clockwork surface manifest and enum-backed form selectors.

DeepSeek was declined because its lane is paused and packet/review overhead
exceeded a one-token repair. Gemini was declined after deterministic proof
because no material alternative or contradiction remained. Native subagents
were declined under developer policy. GPT Sol retained sole custody.

## Next gate and protected boundary

The repair does not authorise attempt 007. The next dependency-satisfied
operation may separately freeze
`raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-attempt-007`.
Only a fresh five-source preexecution receipt, deterministic admission and
distinct one-run checkpoint may permit exactly one new disposable authored-
synthetic PostgreSQL execution with zero retry.

Dedicated check-in remains default-off. No route, feature flag, allowlist,
action grammar, first-party client, waiting-area behavior, REST/OpenAPI,
GraphQL, product configuration, product/patient/appointment/clinical/
historical/protected data, provider call, production runtime, deployment,
release, Pages or protected ref changed.

Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. `docs/branding/` and every
unrelated untracked path remain preserved.
