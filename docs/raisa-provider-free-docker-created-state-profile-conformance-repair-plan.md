# Raisa provider-free Docker Created-state profile conformance repair plan

Date: 2026-08-19

Timestamp: 2026-08-19T22:26:59.3728655+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `84a66372fa15419051f4dd59754ccf93ab681ed4`

Operation:
`raisa-provider-free-docker-created-state-profile-conformance-repair`

Target result:
`raisa_provider_free_docker_created_state_profile_conformance_repair_pass`

Reasoning level: Extra High freezes the ownership, credential-redaction,
Docker-representation and historical-evidence boundaries. High is sufficient
for the fixed implementation, one no-credential Created-state execution,
mechanical predicate correction, exact cleanup, review and closeout while this
plan remains unchanged.

## Objective

Close only the two pre-start containment-predicate defects exposed by the
consumed attempt 002:

1. determine how Docker Engine 29.5.3 represents one exact internal-network
   attachment while a container remains in `created` state;
2. prove that credentials and the ownership nonce are different classes: no
   credential or in-memory non-credential canary may appear in Docker
   configuration, while the nonce must appear at its one exact ownership label
   and nowhere else;
3. remove the captured container and network exactly and prove zero labelled
   residue; and
4. correct and bind only the relay-free harness predicates justified by that
   sanitized evidence.

This tranche does not repeat the database attempt. It may not start or attach
the container, deliver stdin, create a credential, start PostgreSQL, execute
SQL or classify any transaction outcome.

## Causal and immutable floor

| SHA-256 | Exact source |
|---|---|
| `fe9ff969e21e8ee90126c2f58475aaea11b0ddb4a979035a51fc84eeac5b493f` | `docs/raisa-provider-free-check-in-relay-free-recovery-attempt-002-blocked-closeout.md` |
| `9ad525f1e2d004ac1a8b7c1f5b93ce1a7b0866d138b597ac4ffa9319d1f8a673` | `orchestration/agent_inbox/codex/raisa-check-in-relay-free-recovery-attempt-002-sol-blocked-assessment.md` |
| `7efb9853beee9723dbb01fac1f03c4392216bfcc15e9f490f4cb0baae08920ff` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/rehearsal-failure-evidence.json` |
| `6418ecf2e2356b6c875a70106136cdc65d6e545ead5fceeb2c793db45ebe2e40` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/attempt-002-execution-envelope.json` |
| `5c60e6e4b0d554b3c323a932e8aa5a96943705e30a4d09afb2d6b8794a1503f4` | accepted relay-free database harness before this repair |
| `a12694cb898fc9e8ed48641bc94569e4367c77851ba587bf78fc6d59428e10a5` | consumed attempt-002 fixed-output adapter |
| `bed2a89a3814ba9e9ac006d0fdb0c68d204fec53d8c21b6128190605b6ad9ec2` | accepted relay-free database contract |

The failure artifact, execution envelope, occupied count, retry count, old
harness digest and exact sources remain immutable. The old digest is resolved
from its full Git source when historical compatibility is checked; no
seven-character or caller-authored Git abbreviation is admissible.

## Frozen no-credential execution

The implementation creates a distinct Continuity namespace and one exact
contract. The one Docker execution may create only:

- one internal bridge network with a new conformance-specific name prefix,
  the accepted ownership labels and one additional conformance label; and
- one container from cached `postgres:16-bookworm` image ID
  `sha256:64154d0babcb1741988719e703419af0382b19953706149f9872fbd0f438efa8`,
  using pull policy `never`, the accepted server containment switches and a
  conformance-specific name prefix.

The admitted Docker server version is exactly `29.5.3`. The container is
created once and must remain `created`, `Running=false`, never started and
never attached. No port, external network, bind mount, volume, host data,
Docker log, restart, `.env`, credential environment value or credential
argument is permitted.

Two random controller-only canaries may be generated solely to prove absence.
They are not credentials, are never used for authentication, never cross into
Docker and are not retained or hashed. The ownership nonce is separately
required in the exact label and must be absent after that one label entry is
removed from a defensive copy of `Config`/`HostConfig`.

## Sanitized representation reading

Raw Docker inspect output, object IDs, names, nonce, canaries, paths, arguments
and environment values are never written. The closed evidence may retain only:

- exact admitted Docker and image versions already frozen above;
- booleans for captured object, label, image, containment and Created-state
  predicates;
- network-map cardinality;
- a closed relation enum for its sole map key:
  `captured_network_name`, `captured_network_id`, `other` or `missing`;
- a closed relation enum for `HostConfig.NetworkMode` with the same relation
  vocabulary;
- a closed relation enum for `EndpointSettings.NetworkID`:
  `captured_network_id`, `empty`, `other` or `missing`;
- exact pass/fail scenario names, execution count one and retry count zero;
  and
- closed cleanup booleans and matching labelled-resource count zero.

The evidence schema denies any extra property. A failure writes one separate
sanitized terminal artifact and consumes this plan's one execution; it does
not authorise a rerun.

## Evidence-derived predicate correction

Source correction occurs only after the Created-state evidence passes and
cleanup is independently re-read as exact. Only these semantics may change in
the accepted relay-free database harness:

1. the function must receive the captured network name as well as ID and
   require exactly one network-map member whose key is the captured name;
2. `HostConfig.NetworkMode` must match the exact representation proved by the
   occupied evidence;
3. `EndpointSettings.NetworkID` may be only the two lifecycle states justified
   by the Created-state proof and deterministic attached-state fixture: empty
   before start or the captured ID after attachment, never another value;
4. the Docker-configuration secret scan receives only actual credential
   values; and
5. the ownership nonce remains mandatory at the exact label and must be absent
   everywhere outside that label.

The controller retains a broader artifact-redaction tuple containing both
credentials and nonce, so removing the nonce from the Docker credential scan
cannot weaken durable-evidence redaction.

The consumed attempt-002 adapter may receive only a compatibility check that
continues to bind its old harness bytes at the exact historical Git source and
the repaired current harness separately. Its terminal namespace remains
occupied, so its execution path remains fail-closed and cannot be rerun.

One post-correction repair attestation binds the immutable representation
evidence digest, old harness digest, corrected harness digest, exact corrected
predicate set and passing deterministic tests. It grants no database
execution.

## Fixed acceptance matrix

1. `CSPR-S01` — all full Git and SHA-256 causal bindings pass;
2. `CSPR-S02` — closed contract and evidence schemas reject hostile extras,
   abbreviated Git IDs, raw inspect fields and credential-like fields;
3. `CSPR-S03` — source inspection proves no Docker start, attach, exec, logs,
   port publication, database or network egress path;
4. `CSPR-S04` — exact cached image and Docker 29.5.3 are admitted;
5. `CSPR-S05` — one exact internal network and one exact Created-state
   container are captured and ownership-verified;
6. `CSPR-S06` — sanitized network-key, network-mode and endpoint-ID relations
   are classified without retaining raw identities;
7. `CSPR-S07` — controller canaries are absent, nonce presence is exact and
   nonce outside its label is absent;
8. `CSPR-S08` — container and network cleanup succeed by captured ID after
   ownership reinspection and independent labelled residue count is zero;
9. `CSPR-S09` — corrected pure predicates accept Created and attached exact
   states and reject wrong key, wrong mode, foreign ID, leaked credential,
   missing nonce and nonce outside its label;
10. `CSPR-S10` — the immutable attempt-002 envelope and historical harness
    digest remain exact and attempt 002 remains non-runnable;
11. `CSPR-S11` — no process, credential, SQL, database, product or ordinary
    effect occurred; and
12. `CSPR-S12` — one fresh Gemini 3.7 Flash/high exact-candidate veto, clockwork
    closeout, paired Yuri summary and non-PHI notification pass.

## Exact owned outputs

Sol may create or update only:

- this plan and its threat-model delta;
- `orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/`
  contract, schemas, evidence or sanitized failure, repair attestation and
  clockwork artifacts;
- `scripts/raisa_provider_free_docker_created_state_profile_conformance_repair.py`;
- focused tests and plan tests for this operation;
- only the two evidence-proven profile predicate paths in
  `scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py`;
- the consumed attempt-002 adapter/test only as needed to preserve exact
  historical-versus-repaired digest compatibility while forbidding rerun;
- required Ariadne and Gemini review receipts; and
- closeout, Sol acceptance, paired Yuri summary and error-register artifacts
  only if a qualifying incident occurs.

No `app/**`, migration, `.env*`, `docs/api-spine/**`, product test, OpenAPI,
GraphQL, async, client, provider, deployment or existing runtime source is
editable.

## Deterministic admission and one-execution rule

Before Docker creation:

1. a fresh five-source preexecution receipt and all three lane dispositions
   pass;
2. every immutable file and full 40-character Git binding passes;
3. contract/schema/source checks and at least 128 hostile contract/evidence
   mutations deny with zero escapes;
4. focused tests, Ruff, compilation, `git diff --check`, exact Docker/image
   readback and zero pre-existing conformance-labelled resources pass; and
5. the clockwork advances to the exact one-execution stage.

Then exactly one execution is authorised. Cleanup runs in `finally`, retains
the primary failure coordinate, and is independently read back. No failure may
be reclassified as representation evidence and no execution may be repeated
under this plan.

After a pass, source correction and repair attestation are deterministic and
provider-free. A fresh clean-worktree Gemini veto follows only after every
local gate passes.

## Explicit parallelism assessment

- **DeepSeek:** declined. The native Harness still requires its separately
  frozen stock-headless-to-custom-runner boot proof, Claude Code is not a
  fallback, and this single mutable Docker lifecycle is not separable.
- **Gemini:** reserved for one fresh Gemini 3.7 Flash/high read-only veto after
  the no-credential evidence, correction and deterministic packet pass.
- **Native subagents:** declined under current developer policy and because
  one orchestrator must own the captured Docker IDs and cleanup.

Reassess at preexecution, pre-verifier and closeout. No worker receives
execution, cleanup, acceptance, integration or protected-ref authority.

## Fail-closed and continuation rule

Any source, engine, image, object identity, Created-state, network relation,
canary, nonce, redaction, hostile-mutation or cleanup mismatch consumes the one
execution and closes blocked with sanitized evidence. A pass proves only the
two repaired containment predicates. It does not prove PostgreSQL startup,
credentials, transaction recovery, product compatibility or ordinary-practice
admission.

After successful closeout, proceed under Yuri's explicit continuing authority
to the narrowest dependency-satisfied successor. A truly extraordinary,
genuinely non-inferable or safety-critical fork is the only reason to pause.

All staging uses explicit paths only. `git add .` and `git add -A` are
forbidden. Preserve `docs/branding/` and every unrelated untracked file.
