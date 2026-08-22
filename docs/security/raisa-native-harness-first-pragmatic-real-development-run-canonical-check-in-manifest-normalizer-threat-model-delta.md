# Native Harness canonical check-in manifest-normalizer threat-model delta

Date: 2026-08-23

Timestamp: 2026-08-23T09:46:35.7689940+10:00 (Australia/Brisbane)

Status: `frozen_provider_worker_unmounted_manifest_delta`

Operation:
`raisa-native-harness-first-pragmatic-real-development-run-canonical-check-in-manifest-normalizer`

## Boundary

One fresh pinned native DeepSeek Harness session may edit two exact files in a
disposable sparse worktree. Its input is authored, non-PHI repository source
and a reference-only manifest contract. The resulting module is unmounted and
pure. It opens no product runtime, environment, secret, data, command,
deployment or protected authority.

## Threats and controls

### YAML becomes executable or ambiguous

Risk: unsafe constructors, tags, aliases, merges, duplicate keys or YAML 1.1
implicit typing create data-dependent behaviour outside the frozen schema.

Control: a local `SafeLoader` subclass only, token-level anchor/alias/tag
denial, duplicate-key construction guard, merge denial, JSON-shaped values,
closed fields and explicit scalar/type validation. Parser exceptions become
closed denial codes.

### Ambient configuration or secret access

Risk: a “normalizer” reads `.env`, process environment, application settings,
credential stores, secret providers or a database.

Control: the public function accepts exact bytes and has no path or environment
argument. Source/import tests forbid filesystem, configuration, secret,
database, route, network and time dependencies. Reference strings are pattern-
checked but never resolved.

### Secret value smuggled under a near-alias

Risk: case, hyphenation or nesting evades the frozen forbidden-field list.

Control: recursively normalize field names with case folding and hyphen-to-
underscore before checking all forbidden names, then enforce exact unknown-key
denial at every object.

### Abbreviated or wrong Git evidence accepted

Risk: a seven-character abbreviation or mismatched evidence binding appears
plausible.

Control: every Git field is exactly forty lowercase hexadecimal characters and
every rotation row equals the manifest authority object. No Git resolution is
performed in this pure node; the later evaluator owns current evidence.

### Shape validation mistaken for operational truth

Risk: a normalized reference-only document is described as a current manifest,
valid secret binding, role attestation or ordinary-practice admission.

Control: success is named `manifest_normalized`, not satisfied/admitted. The
result has no environment selection, freshness-now, uniqueness, secret
resolution, external evidence or command method. Current instance count and
ordinary admission remain zero.

### Trace quality mistaken for implementation acceptance

Risk: a complete native-Harness terminal hides incorrect or incomplete code.

Control: trace completeness and useful candidate are separate efficacy fields.
Sol independently reviews the exact diff, changed paths and tests and owns
acceptance.

### Containment prevents normal coding

Risk: another one-request ceiling turns a recoverable edit error into a false
worker failure.

Control: natural multi-turn self-correction is allowed inside one 900-second
session. Tool parallelism remains one and automatic provider retries,
fallbacks and auxiliary models remain zero.

### Diagnostic spiral follows a terminal

Risk: a failed real assignment recreates the prior interoperability programme.

Control: no generic boot reproof or diagnostic sequel. Only one direct
pre-packet mechanical envelope defect may receive one correction/fresh run;
otherwise Sol recovers the task and preserves provenance.

### Worker scope escape

Risk: the worker changes plan, harness, broker, route, config or unrelated
files.

Control: exact sparse worktree, full source OID, two owned paths, minimized
tools, broker binding, changed-path readback and automatic rejection of any
extra path. The worker cannot commit, push, accept or move protected refs.

## Explicitly closed

No manifest instance; no secret/reference resolution; no `.env`, process
environment, configuration, credential store, database, Docker, product route,
API, GraphQL, OpenAPI or client; no ordinary-practice enablement, feature flag,
allowlist, command, generic-status `Arrived`, grammar or waiting-area change;
no product, patient, appointment, clinical, historical or protected data; no
production, deployment, release, Pages or protected-ref movement.
