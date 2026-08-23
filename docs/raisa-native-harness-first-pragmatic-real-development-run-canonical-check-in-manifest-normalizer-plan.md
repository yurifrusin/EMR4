# Native Harness first pragmatic real-development run: canonical check-in manifest normalizer

Date: 2026-08-23

Timestamp: 2026-08-23T09:46:35.7689940+10:00 (Australia/Brisbane)

Status: `frozen_narrow_plan`

Operation:
`raisa-native-harness-first-pragmatic-real-development-run-canonical-check-in-manifest-normalizer`

Planning source HEAD:
`27421b3f183011a03ced07e23bfdcc77d5dc884b`

Accepted Harness-adoption source:
`20d03e2ac4134c980461ebb149535ff3e88e7306`

Protected source:
`2e34bdad732fdab32fbf778280b3d3c70d66d602`

Reasoning level: High. The accepted architecture and adoption plan already
freeze the material meaning. This tranche implements one low-risk, unmounted
repository node and measures useful native-Harness work without another
qualification programme.

## Objective

Implement only `closed_manifest_normalizer` as genuine EMR4 source plus focused
tests. One fresh pinned native DeepSeek Harness session may edit exactly:

- `app/services/appointment_check_in_environment_manifest.py`; and
- `tests/test_appointment_check_in_environment_manifest.py`.

GPT Sol freezes this plan, contract and minimal scaffold, performs the exact
pre-dispatch readback, reviews the terminal trace and diff, runs all tests, and
owns acceptance and any recovery.

## API Spine classification

This is a manifest/capability change. An explicitly supplied declarative YAML
document is normalized into immutable typed Python data. The document is not an
environment selector, secret resolver, policy engine, admission record,
activation grant or command. GraphQL, REST/OpenAPI, async events, Access AI and
first-party clients remain unchanged.

No command audit or idempotency envelope is added because the function has no
effect. Its security obligation is deterministic default denial and absence of
ambient reads.

## Exact public contract

The module exports `normalize_check_in_environment_manifest(payload: bytes)`.
It returns one frozen `ManifestNormalizationResult`:

- `outcome == "normalized"`, `reason_code == "manifest_normalized"`, a
  lowercase SHA-256 of the exact accepted bytes, and a complete frozen
  `NormalizedCheckInEnvironmentManifest`; or
- `outcome == "denied"`, one closed denial reason, no normalized manifest and
  no digest release.

It raises no parser/validation exception for caller-controlled bytes. Programmer
misuse is also represented as `manifest_input_type_invalid` rather than an
ambient exception.

The complete machine-readable contract is
`orchestration/continuity/raisa-native-harness-first-pragmatic-real-development-run-canonical-check-in-manifest-normalizer/contract.json`.

## Canonical input envelope

- input type is exact `bytes` and size is 1 through 32,768 bytes;
- UTF-8 is strict; BOM, NUL, CR, tabs and non-UTF-8 are denied;
- the document ends in exactly one LF and contains no trailing blank line;
- exactly one YAML document and one mapping root are permitted;
- anchors, aliases, explicit tags, merge keys and duplicate mapping keys are
  forbidden before construction;
- only string keys and JSON-shaped scalar/list/mapping values are permitted;
- floats, timestamps, binary, sets, ordered-map tags and custom Python objects
  are forbidden; and
- case-folded/hyphen-normalized secret-value field names are forbidden at any
  depth before ordinary unknown-key validation.

PyYAML `6.0.3` may be used only through a locally defined `SafeLoader`
subclass with the controls above. `unsafe_load`, `full_load`, object
constructors and implicit timestamp construction are forbidden.

## Accepted normalized shape

The exact top-level and nested fields remain those in the accepted Draft
2020-12 schema. Unknown or missing fields deny. The normalizer additionally
enforces the architecture's cross-field invariants:

- schema version, logical role, credential slot, required booleans and
  deny-only break-glass constants are exact;
- every Git object is exactly 40 lowercase hexadecimal characters;
- the three secret bindings and rotation rows appear in the frozen slot order;
- provider namespace, secret reference and key identifier are each distinct
  across the three slots;
- every rotation row matches its secret row's slot, key, version and evidence
  reference;
- every rotation row matches the manifest environment, generation and
  authority Git object;
- RFC 3339 timestamps are timezone-aware and normalized to exact UTC `Z` text;
  `fresh_until` follows `observed_at`, and `expires_at` follows `issued_at`;
  no comparison with current time occurs here; and
- all identifier/reference patterns and integer lower bounds match the accepted
  schema.

The later `pure_environment_evidence_gate_evaluator` owns current-time
freshness, uniqueness across manifest instances, role attestations, external
evidence validity and the final `evidence_gate_satisfied` reading. None of
those semantics may migrate into this node.

## Closed denial vocabulary

Exactly these reason codes are returned:

1. `manifest_input_type_invalid`;
2. `manifest_size_invalid`;
3. `manifest_encoding_invalid`;
4. `manifest_bytes_non_canonical`;
5. `manifest_alias_or_tag_forbidden`;
6. `manifest_duplicate_key`;
7. `manifest_yaml_structure_invalid`;
8. `manifest_forbidden_field`;
9. `manifest_shape_invalid`;
10. `manifest_git_object_invalid`;
11. `manifest_binding_invalid`; and
12. `manifest_normalized` for success.

Precedence is the order above except that successful normalization is last.
This keeps hostile inputs deterministic without exposing parser exceptions or
secret-like content.

## Minimal focused verification

The worker adds only the tests needed to prove the real contract:

- one canonical accepted document with complete frozen nested readback and
  exact byte digest;
- one focused case for every denial code and precedence-sensitive envelope
  class;
- parameterized coverage for every forbidden secret-field spelling, all three
  slot positions, non-full/mixed-case Git objects, duplicate/unknown/missing
  keys and representative cross-field mismatch;
- determinism and input non-mutation; and
- a source/import guard proving no filesystem, process environment,
  configuration, credential, database, route, network or time source is used.

Sol runs the focused file, `tests/test_api_spine_artifacts.py`, the accepted
environment-manifest architecture and gap-decomposition tests, Ruff/compile and
`git diff --check` serially outside the worker. Because the historical
gap-decomposition tripwire denied every later `app/**` descendant, this tranche
may update that one test to allow only the exact unmounted normalizer path while
continuing to deny every route, API Spine, Diary, sidebar and environment-file
change. No separate Gemini veto is required unless API meaning changes, an
owned path is crossed, evidence conflicts or another normal risk trigger
arises.

## Native Harness execution shape

- exact pinned `@deepseek-ai/dsh@0.1.0-rc.7`, accepted profile and runner hashes;
- one fresh sparse worktree at the committed scaffold's full source OID;
- one fresh `emr4-bounded-worker` session, visible tools only `read`, `glob`,
  `edit`, one tool call at a time and approval `never`;
- natural multi-turn read/edit/error/reread/edit inside 900 seconds;
- broker-held credential, zero automatic provider retry, fallback or auxiliary
  model and no model-facing shell;
- exact changed-path, sanitized request/tool/result/usage/terminal and cleanup
  readback; and
- no worker integration, commit, push or self-acceptance.

No generic boot reproof, per-step clockwork tick, diagnostic sequel or
subcoordinate closeout is allowed. Only a directly attributable pre-packet
mechanical envelope defect may receive one correction and at most one fresh
run. Otherwise preserve the terminal and Sol recovers the source task without
silently changing transport.

## Matched efficacy reading

Closeout records:

- `useful_candidate`;
- `task_completion`;
- `trace_complete`;
- `correction_cost`; and
- `scope_integrity`.

These fields judge this real assignment; they are not a new qualification gate
or a claim that the native Harness is the default worker.

## Parallelism assessment

- DeepSeek native Harness: `planned`, positive leverage, owns implementation
  and focused tests only after the serial scaffold and pre-dispatch gate.
- Gemini 3.7 Flash/high: `declined`, neutral leverage; reassess only on the
  listed risk triggers.
- Native subagents: `declined`, negative leverage under developer policy.
- GPT Sol owns architecture, scaffold, dispatch, review, deterministic tests,
  recovery, acceptance, clockwork and Git.

## Acceptance and stop conditions

Accept only when the changed path set is exactly the two owned implementation
paths plus the one historical tripwire test named above, all
required focused/surrounding checks pass, the terminal trace and cleanup are
complete, and source review confirms no ambient or forbidden capability.

Stop the native lane on source drift, extra path, missing terminal/cleanup,
secret/environment/configuration/database/route/network access, contract
meaning drift, runner/broker/guard archaeology, or a non-mechanical terminal.
An in-scope but incomplete candidate may be recovered by Sol under separately
recorded provenance; it is never accepted merely because the trace is good.

## Protected boundary

No operational manifest instance, secret value or reference resolution,
`.env`, environment variable, app configuration, credential store, database,
Docker, route, API, GraphQL, OpenAPI, client, ordinary-practice admission,
feature flag, allowlist, command mounting, generic-status `Arrived`, action
grammar, waiting area, product/patient/appointment/clinical/historical/
protected data, production, deployment, release, Pages or protected-ref
movement is authorized.

Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage exact paths only; never `git add .` or
`git add -A`.
