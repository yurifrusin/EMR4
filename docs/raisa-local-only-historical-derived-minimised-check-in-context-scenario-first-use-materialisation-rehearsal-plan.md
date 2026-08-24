# Raisa local-only historical-derived minimised check-in-context scenario first-use materialisation rehearsal — plan

Date: 2026-08-24

Timestamp: 2026-08-24T11:28:39.9415173+10:00 (Australia/Brisbane)

Status: `frozen_one_run_no_retry`

Reasoning level: `extra_high_private_access_and_first_write_freeze_then_high_mechanical_execution`

## Objective

Perform exactly one metadata bind and one local content run over the already
bounded dense-day source. Derive one minimised structural check-in-context
candidate in memory, obtain an exact digest-bound decision from the accepted
first-use gate, and atomically write one ignored local-test fixture only when
the gate admits that exact digest. Every other terminal writes no fixture.

## Exact authority and bindings

- active clockwork source:
  `85ea931cd1a743f8d1fd2dff077c09d2d8fc1182`;
- materialiser contract:
  `orchestration/continuity/raisa-provider-free-governance-clockwork-historical-derived-first-use-materialisation-subgate-rehearsal/next-tranche-contract.json`;
- exact contract SHA-256:
  `3e07a40f3e7c722e89cf7e082c2e9399a6836998c7b061350423ce54a813ba5f`;
- gate implementation source:
  `abcd4206a363b0c565c070e0f2cb9c54d627b3b3`;
- gate declaration source:
  `7f9a526e57a4c10502f01b0e7c1cc5ec6910f00c`;
- accepted measurement source:
  `a9e00638b960306766260d6df674c3489be58b86`; and
- task/origin planning HEAD:
  `0bd9ffd6c90dcf7435e4cd0ba3c01339dcf6666f`.

The committed gate module must be byte-equal to its exact Git-source blob
before private access. The active latch must contain the complete eight-member
materialisation mode and no denial or measured-probe mode.

## Exact local paths

- source root:
  `local_data/historical-diary-trove/raw/pilot_01`;
- owned attempt root:
  `local_data/historical-diary-trove/first-use-attempts/2026-08-24-check-in-context-v1`;
- owned ignored fixture root:
  `local_data/historical-diary-trove/derived-scenarios/2026-08-24-first-use-check-in-context-v1`;
- sole possible fixture: `scenario.json` within that fixture root.

Both owned roots must be absent before the bind. No pre-existing ignored output
is reused. Cleanup may remove only exact children of these two roots after
resolved-path containment checks.

## Implementation

1. Parameterize the accepted metadata binder with explicit attempt, core and
   extractor paths while preserving its current defaults and behavior.
2. Add one exact `HistoricalFirstUseMaterialisation` Word profile bound to the
   owned attempt root. Preserve invisible, alerts-disabled, macros-forced-
   disabled, link-updates-disabled, read-only document and owned-process
   cleanup controls.
3. Add a local materialiser that uses the accepted private extraction and
   projection models without persisting the projection, token key, content
   token or mapping.
4. Compare adjacent snapshots in memory and form only the six closed structural
   event kinds already known to the gate. Select 3–12 events within a 10–120
   relative-minute window, at least three distinct minutes and two event kinds,
   at most four ephemeral subject slots and two resource slots.
5. Persist only relative day zero, relative minutes, closed event kinds and
   small numeric synthetic subject/resource slots. Do not persist source text,
   token values, exact dates/times, filename/path, coordinates, keys or a slot
   mapping.
6. Compute the gate candidate digest and utility independently, evaluate the
   exact envelope, and require `admitted_for_exact_declared_artifact_only` with
   an exact matching non-transitive binding.
7. Serialize the candidate with the same sorted compact UTF-8 JSON used by the
   digest, write to a temporary file, verify its SHA-256, atomically replace
   `scenario.json`, and verify the fixture root contains that one file only.
8. On block, revision requirement, mismatch or exception, remove any owned
   temporary/fixture output and emit only a sanitized terminal reading.
9. Remove the private manifest, Word control/progress files and parent cleanup
   artifacts after the content terminal. Retain only sanitized local attempt
   readings and, on admission, the sole ignored fixture.

## Pre-access acceptance

Before `--bind`:

- authored-synthetic positive, block, revision, atomic-write and cleanup tests
  pass;
- every existing historical-Diary control passes serially;
- Ruff, compileall, JSON-schema/static source-boundary and Git-diff checks pass;
- gate Git-blob equality, contract hash and latch mode pass;
- source root is the exact allowed non-reparse leaf root;
- both owned roots are absent;
- protected refs remain exact and `docs/branding/` remains excluded; and
- no provider, model, network, clipboard, telemetry, database, client or
  product surface is present.

## Occupied execution

Run exactly:

1. one `--bind` command; then
2. if and only if it passes, one `--execute` command under the 1,800-second
   parent ceiling.

There is no second bind, no second content run, no retry and no fallback. A
failed or non-admitted terminal is accepted as a zero-write result for this
tranche. Do not repair and rerun against private content inside this tranche.

## Evidence and claim ceiling

Commit only sanitized aggregate evidence: counts, closed decisions/reasons,
candidate utility, candidate/output digest equality, cleanup facts and absence
flags. Never commit or transmit the fixture, private manifest, extraction,
projection, raw stdout, filenames, exact source dates/times, paths, source text,
tokens, keys or mappings.

Passing proves one local-test fixture or a clean zero-write terminal. It does
not prove patient de-identification in general, whole-day replay, practice
validity, product behavior, ordinary-practice readiness, provider safety,
runtime integration or production suitability.

## Parallelism assessment

- DeepSeek Flash: `declined_negative`; the native Harness remains paused,
  Claude is not a silent fallback, and no external worker may receive private
  content or the one-run lease.
- Gemini verifier: `not_applicable_neutral`; private inputs are forbidden and
  deterministic local verification owns acceptance.
- Native subagents: `declined_negative`; one metadata bind, Word child,
  in-memory projection, gate and writer share one serial mutable state.
- GPT Sol owns the plan, implementation, preflight, occupied run and acceptance.
  Reassess only before dispatch, on deterministic pre-access failure, or at the
  next named tranche boundary—not during the consumed content run.

## Forbidden surfaces

No protected evidence; no second day/root or more than 80 files; no source
mutation; no provider/model/network release; no fine-tuning, memory or RAG; no
product, patient, appointment, clinical, database, route, client, runtime,
ordinary-practice or waiting-area change; no deployment, release, Pages or
protected-ref movement. Preserve all unrelated untracked files and stage only
explicit paths.
