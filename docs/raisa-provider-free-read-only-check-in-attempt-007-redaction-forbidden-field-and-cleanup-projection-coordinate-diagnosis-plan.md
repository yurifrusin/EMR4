# Provider-free read-only check-in attempt-007 redaction forbidden-field and cleanup-projection coordinate diagnosis plan

Date: 2026-08-23

Timestamp: 2026-08-23T03:47:43.2463123+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`edfa7ae33c0df8aefaea6490dc2d54b05d233dd5`

Accepted attempt-007 occupied source:
`b7c37a76c41d399c4b198d3ab6b526c5510b434b`

Accepted attempt-007 terminal source:
`6657ee5061265d732096e9987f327d82feed800c`

Protected source:
`2e34bdad732fdab32fbf778280b3d3c70d66d602`

Operation:
`raisa-provider-free-read-only-check-in-attempt-007-redaction-forbidden-field-and-cleanup-projection-coordinate-diagnosis`

Target result:
`raisa_provider_free_read_only_check_in_attempt_007_redaction_cleanup_projection_coordinate_diagnosis_pass`

Reasoning level: High is required to keep immutable observed evidence, static
control-flow inference and the future repair boundary separate. No material
product, provider, authority or architecture choice is made.

## Starting fact and authority

Attempt 007 is consumed once and immutable. Its single occupied invocation
failed closed at `redaction/forbidden_field`, retried zero times, wrote no
transaction attestation or success evidence, and released no ordinary
admission, product record or success. Its terminal and envelope SHA-256 values
are respectively
`86e5e1342eb54e062e35d73390ebceb141d097d03e180e4fe3c0ed64b465f422`
and
`3338c58054dea96b3845827dacfe184889ee328e5a4463966464b560d0a2c2c5`.

Independent postterminal read-only Docker inspection found zero matching owned
containers and networks. The immutable wrapper envelope nevertheless reports
`cleanup_status=not_started`; that contradiction is not repaired or
reclassified here. It bounds the second diagnostic question.

Yuri's standing uninterrupted-development authority admits this read-only
successor. It authorises no retry, resume, attempt 008 plan or checkpoint,
Docker object creation, PostgreSQL process, SQL, database operation, worker or
provider call.

## Narrow objective

Bind the exact attempt-007 source and terminal, then produce one deterministic
diagnosis that answers two closed questions:

1. Which exact prospective success-evidence key paths collide with the source-
   owned forbidden-field predicate, and at what control-flow coordinate can
   that collision escape after cleanup?
2. Which exact wrapper projection converts the escaped post-finalization error
   into a new failure document whose cleanup state is `not_started`, and what
   minimum typed bridge would preserve only already-validated cleanup state?

The diagnosis must enumerate the complete prospective final-result key-path
surface, distinguish source observation from inference, and select the
narrowest future deterministic repair. It must not implement that repair or
authorise an occupied successor.

## Immutable source and evidence bindings

The diagnosis binds these inputs byte-for-byte:

| SHA-256 | Exact source |
|---|---|
| `1b7ec51cfd97fa6a54398ab0587acf79d3b0b8d34fa5609a2bad2abe17e91c16` | `scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py` |
| `ed7d84993d3b89037db09d0af2e7a0de32b0fb00c5da01a00731d100dcc14295` | `scripts/raisa_provider_free_check_in_relay_free_recovery_attempt_007.py` |
| `bed2a89a3814ba9e9ac006d0fdb0c68d204fec53d8c21b6128190605b6ad9ec2` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/contract.json` |
| `4c62319a372a96897add7908159510b269ffca7f2a19d4f98facf03020d186c5` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/attempt-007-execution-envelope.schema.json` |
| `86e5e1342eb54e062e35d73390ebceb141d097d03e180e4fe3c0ed64b465f422` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/rehearsal-failure-evidence.json` |
| `3338c58054dea96b3845827dacfe184889ee328e5a4463966464b560d0a2c2c5` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/attempt-007-execution-envelope.json` |

Every Git binding must be a machine-resolved full 40-character commit object
and an ancestor of the diagnostic candidate. The attempt-007 namespace remains
immutable and mechanically closed.

## Read-only evidence model

The diagnostic implementation may read only the six exact inputs above, the
current repository Git graph and its own contract/schema. It may use Python
AST, JSON Schema and deterministic in-process fakes. It may not invoke Docker,
PostgreSQL, a network, a provider, an application route or a product runtime.

The retained evidence must separate:

- **observed source facts:** exact AST nodes, key paths, exception edges and
  terminal fields;
- **deterministic reproductions:** redaction predicate output and wrapper
  projection output over sanitised structural values;
- **bounded inferences:** the latest supported control-flow coordinate; and
- **unproved claims:** transaction semantics, role absence before teardown,
  internal cleanup history and successful result content.

No raw exception, source dump, environment value, command vector, credential,
Docker identity or unbounded stream may enter retained evidence.

## Closed diagnostic vocabulary

One source constant must own the exact coordinate vocabulary shared by the
classifier, schema, evidence and hostile tests:

- `prospective_success_projection_forbidden_field`
- `post_cleanup_result_redaction_escape`
- `wrapper_untyped_post_finalization_cleanup_collapse`
- `insufficient_closed_evidence`

The expected combined diagnosis passes only when all of these predicates hold:

1. the exact contract-derived path
   `closed_boundaries.live_secret_existing_hosted_or_product_database_used`
   is the sole prospective result key that collides with the exact forbidden
   key vocabulary;
2. the collision is reproduced by the source-owned `_assert_redacted`
   predicate with `stage=redaction` and `code=forbidden_field`;
3. AST control flow proves `result` receives the contract's
   `closed_boundaries` projection before the `finally`, cleanup is finalized in
   the `finally`, and final result redaction is invoked after that `finally`;
4. no enclosing base-harness handler converts that post-finalization
   `RehearsalFailure` into failure evidence with the finalized cleanup object;
5. wrapper AST and a pure fake prove the caught base error is passed through
   `_sanitized_failure`, which supplies only `{"status": "not_started"}` to
   `_failure_evidence`; and
6. the immutable attempt-007 terminal and envelope match that exact stage,
   code and collapsed cleanup projection.

Missing, additional, conflicting or drifted evidence must classify as
`insufficient_closed_evidence` or reject.

## Narrowest future repair boundary

The diagnosis may select a future repair only if it consists of both of these
deterministic gears:

1. a pure, source-owned prospective-success projection gate exercised during
   static admission, before any Docker object or database work, that runs the
   complete final evidence key-path surface—including every contract-derived
   projection—through the exact final redaction predicate; and
2. a typed post-finalization terminal bridge owned by the base harness that
   converts redaction or schema failure after cleanup into sanitised failure
   evidence carrying the already-finalized cleanup projection, so the wrapper
   cannot invent or collapse it.

The future repair must rename or otherwise safely project the exact conflicting
closed-boundary field without weakening the forbidden-field predicate or
changing the boundary's false/default-denial meaning. It must add a hostile
mutation proving any newly introduced conflicting key fails before occupied
work. The diagnosis does not choose an attempt number, modify source or
contract, or declare the repaired database behavior accepted.

## Construction and proof

The tranche may add only:

- one deterministic read-only diagnostic module;
- one closed contract and one closed evidence schema;
- one canonical diagnosis evidence document and technical report;
- focused plan, source-binding, AST, classifier, projection and hostile tests;
- closeout, Sol acceptance, efficacy, clockwork and Yuri-summary artifacts.

The diagnostic CLI exposes only `--check` and one provider-free read-only
`--execute` path, accepts no caller output path, and writes only its fixed new
Continuity namespace by exclusive creation. Construction and tests must prove
zero subprocess calls except Git object resolution, zero Docker/PostgreSQL/
database/provider/product actions, exact source hashes, full-object ancestry,
closed schemas, canonical JSON and immutable predecessor bytes.

Hostile coverage must include every closed coordinate, key-token prefix and
suffix collisions, exact-token collision, safe near misses, missing/extra
paths, source/digest drift, short Git identifiers, altered AST order, invented
cleanup, a non-dictionary cleanup projection, raw exception leakage, symlink or
path escape, overwrite and noncanonical bytes.

## Acceptance

Acceptance requires:

1. the fresh five-source receipt and explicit DeepSeek, Gemini and native-
   subagent dispositions pass;
2. every immutable input hash and full-object ancestry binding matches;
3. complete prospective success key-path enumeration identifies exactly one
   conflict and the exact redaction predicate reproduces the terminal stage and
   code;
4. AST evidence proves the post-cleanup escape coordinate without executing
   the occupied harness;
5. deterministic wrapper projection proves the cleanup collapse without
   overwriting or reclassifying attempt 007;
6. the report names the two-gear future repair and keeps attempt 008 closed;
7. focused tests, Ruff, Python compilation, JSON/schema validation and
   `git diff --check` pass;
8. no Docker object, PostgreSQL, SQL, database, provider or product activity
   occurs; and
9. task/protected refs, `docs/branding/` and every unrelated untracked path
   remain unchanged.

## Parallelism assessment

- **DeepSeek native Harness:** `declined`, negative leverage. Its worker lane
  is paused pending a distinct stock-headless-to-custom-runner boot proof, and
  this provider-free read-only diagnosis grants no worker or provider call.
- **Gemini:** `declined`, neutral leverage. Deterministic source, AST, schema and
  fake evidence precede any independent material veto surface. Reassess only if
  a successor repair changes acceptance meaning or another static judgment is
  genuinely useful.
- **Native subagents:** `declined`, negative leverage. Developer policy
  prohibits proactive delegation and the two coordinates form one serial
  evidence chain.
- **GPT Sol:** owns plan meaning, exact bindings, deterministic diagnosis,
  acceptance, clockwork and Git.

## API Spine, protected and continuation boundaries

This tranche changes no REST/OpenAPI command, GraphQL read model, async
contract, route, application schema, migration, feature flag, authored-
synthetic allowlist, action grammar, first-party client, waiting-area behavior
or product configuration. Dedicated check-in remains default-off. Generic
status does not gain `Arrived`; no ordinary practice is enabled.

No product, patient, appointment, clinical, historical or protected data;
Docker object; PostgreSQL process; SQL; database operation; attempt 008;
DeepSeek worker; provider call; production runtime; deployment; release;
Pages; protected-evidence access; or protected-ref movement is authorised.
Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Closeout uses clockwork as the sole canonical governance writer. Sol writes
the paired lay/technical Yuri summary, sends the usual non-PHI Pushover,
stages only explicit paths, and preserves `docs/branding/` plus every unrelated
untracked file. A future repair requires its own fresh five-source
rehydration, exact frozen plan and deterministic admission; attempt 008 remains
closed.
