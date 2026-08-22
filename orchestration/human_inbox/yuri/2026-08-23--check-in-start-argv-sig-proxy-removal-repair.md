# Check-in Docker start option repair — lay and technical closeout

Date: 2026-08-23

Timestamp: 2026-08-23T02:48:38.4129265+10:00 (Australia/Brisbane)

Status: `accepted`

## Lay summary

The specific Docker command defect found in the last tranche is now fixed. We
removed the one option that this version of `docker start` does not support.
Nothing else in the database rehearsal harness changed.

The repair was proved without creating a container or starting a database. Its
attachment, password-input and cleanup behavior were exercised with
deterministic substitutes, and 94 current tests pass. The old failure record
remains intact and is now checked against the exact historical source where it
occurred.

The next step can be a separately planned attempt 007, still limited to one
disposable authored-synthetic run with no retry. This repair is not itself
permission to run it.

## Technical summary

- Removed token: `--sig-proxy=false`.
- Added tokens: zero.
- Other harness changes: zero.
- Repaired argv:
  `<executable> start --attach --interactive <container_id>`.
- Pre/post harness SHA-256:
  `839a9a17b22aa132ea5bddf878f59f4741412cb1ee464020f34aa2aefbdff8e2` /
  `1b7ec51cfd97fa6a54398ab0587acf79d3b0b8d34fa5609a2bad2abe17e91c16`.
- Attestation SHA-256:
  `73d5773d3662509ec2cdb8d8f109651b77ef79be42f5b641f07e36d7ca8bcf91`.
- Current focused validation: 94 passed; Ruff/compile/schema/canonical bytes
  passed.
- Docker metadata/object, PostgreSQL, database, provider, product and ordinary
  counts: all zero.

## Efficiency reading

The useful part was direct: one diagnosed token, one exact deletion, no blind
database rerun. The remaining friction was procedural—one plan sentence
needed source-based correction, one report assertion repeated line-wrap
sensitivity, and one explicit staging path was mistyped and rejected by Git.
The first closeout form also used a descriptive stage outside the closed
vocabulary; the clockwork rejected it before publication and accepted the
registered value on the same transaction. These are concrete candidates for
typed lifecycle prose, a shared normalized document predicate,
machine-generated staging manifests and enum-backed form selectors.

No Yuri attention is required. The standing next tranche is the separately
frozen, checkpointed attempt 007 plan; ordinary-practice, product-data,
provider, production, deployment, Pages and protected-ref surfaces stay
closed.
