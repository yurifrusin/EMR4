# DeepSeek native Harness provider-free emr4-bounded-worker preset materialisation recovery plan

Date: 2026-08-20

Timestamp: 2026-08-20T10:30:02.1366272+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`b8505d3df4f0d7fce07cc7d1318748bbe2d97dff`

Accepted required-service recovery source:
`ae608b4a8cc4004693813a83e518c71eb2ff06f3`

Accepted effective-tool guard source:
`dc167c20f5b54b783a57fccb7843f434136c8ca8`

Operation:
`deepseek-native-harness-provider-free-emr4-bounded-worker-preset-materialisation-recovery`

Reasoning level: Extra High freezes the distinction between preset-provided
tools, the accepted post-mount restriction and the future native-process
boundary. High is sufficient for bounded deterministic implementation, tests,
independent veto and clockwork closeout while this plan remains unchanged.

## Objective and exact claim

The accepted required-service recovery proves how a future headless host must
provide `agentPresets` and delay the runner until `hmr`, `agentPresets` and
`tools` are all active. It deliberately leaves `emr4-bounded-worker`
unmaterialised.

This tranche may only produce and prove one repository-retained, installation-
ready preset payload whose future Harness-home relative destination is exactly
`.agent-presets/emr4-bounded-worker/agent.cordis.yml`. The file contains the
official rc.7 filesystem and filesystem-search tool rows. Exact rc.7 source
must prove that those rows provide the selected tools and that the already
accepted effective-tool guard, applied immediately after mount, reduces the
inherited model-facing schema to exactly sorted `edit`, `glob`, `read`.

The preset is not itself the authority boundary. The filesystem plugins have a
broader inherited surface: `tool-fs` unconditionally registers `read`, `write`
and `edit` and may additionally register `read_image` when attachments are
active; `tool-fs-search` unconditionally registers `glob` and `grep`. The
accepted guard is the second mandatory stage that excludes `write`, `grep` and
any optional `read_image`. The outer broker's exact three-name allowlist remains
independently mandatory.

## Immutable inputs and exact local-source boundary

The implementation must bind these accepted predecessor facts without changing
their artifacts:

- `@deepseek-ai/dsh-agent-presets@0.1.0-rc.7` exact cached package and
  `lib/index.js` digest from the required-service recovery;
- `@deepseek-ai/dsh-tools@0.1.0-rc.7` exact cached package and
  `lib/index.js` digest from the accepted effective-tool guard;
- the exact accepted effective-tool helper and contract, including preset id
  `emr4-bounded-worker`, sorted selection `edit`, `glob`, `read`, mount-before-
  view-before-restrict-before-schemas ordering and closed coordinates; and
- both consumed native attempts and their retained failure evidence.

The tranche adds exact local-cache bindings for:

- `@deepseek-ai/dsh-tool-fs@0.1.0-rc.7`, tar SHA-1
  `0df84033fddee766d88dd3bf9e8c660d348663c9`, SHA-512 integrity
  `sha512-/Uf2z6OZckk0Nz7XjVbzf/yUnvDeY58CkUjAqy2FxgGuNc0rvIR6VzRER5NZ+30bXeB8TPnjMuCVB+j/8zltrw==`
  and tar SHA-256
  `1b163810c5065fdf90a08f0d4e3c7341071c4e839c796773ab462c6356328d59`;
- `@deepseek-ai/dsh-tool-fs-search@0.1.0-rc.7`, tar SHA-1
  `1691fff576a6f250c9b87e072ead0770238205fc`, SHA-512 integrity
  `sha512-0Lo6bbpPcSMKZlWkBGx2KjwyLy5zYJKMH8fmwz8orwOKHjbfYQT51GV9cpdhLq6NYTwKeMUaxTZC4xPlZ03SAg==`
  and tar SHA-256
  `961279d53a23a2a1d73f6ce31e76300b26f4c5dd7f667571572e9aee9d6c4d13`.

Every blob must match its registry identity and every retained `package.json`
and `lib/index.js` member must match exact bytes and SHA-256 before semantic
inspection. Package members remain in memory. Evidence may retain only package
identities, digests, safe service/plugin/tool names, booleans, counts and the
exact materialised preset bytes.

No registry, external network, npm command, Node process, package install or
package extraction to disk is authorised. The existing local npm cache is the
only package source.

## Exact materialised payload

The repository-retained payload path is:

`orchestration/continuity/deepseek-native-harness-provider-free-emr4-bounded-worker-preset-materialisation-recovery/materialised-home/.agent-presets/emr4-bounded-worker/agent.cordis.yml`

Its complete UTF-8/LF bytes are:

```yaml
- id: tool-fs
  name: '@deepseek-ai/dsh-tool-fs'
- id: tool-fs-search
  name: '@deepseek-ai/dsh-tool-fs-search'
  config:
    sampleOverCapGlobResults: false
```

The directory id must match rc.7's exact
`^[a-z0-9][a-z0-9-]*$` preset-id grammar. The filename must be exactly
`agent.cordis.yml`. The document must be a top-level list with exactly two
non-group plugin rows in the shown order. The first row has only `id` and
`name`; the second has only `id`, `name` and the one exact required boolean
configuration. No metadata file, hidden row, alias, anchor, JavaScript tag,
environment expansion, absolute path, dynamic plugin, permission statement,
shell, command, provider or credential may appear.

This path is a durable repository payload only. The script may write this exact
owned file under the continuity directory; it must not create or modify a real
Harness home, the user's `%USERPROFILE%/.agent-presets`, a disposable Harness
installation, or any external directory.

## Frozen deterministic proof

The controller must perform these checks without executing JavaScript:

1. validate full 40-character planning and accepted predecessor Git object ids;
2. validate the accepted predecessor script/contract/evidence bytes and both
   consumed native-attempt bindings;
3. resolve every npm blob from the exact owned local cache, reject missing,
   symlinked, substituted or malformed tar content, and validate registry
   SHA-1, SHA-512 integrity, tar SHA-256 and exact member byte/digest bindings;
4. prove from `dsh-agent-presets` source that the user root is
   `.agent-presets`, the composition filename is `agent.cordis.yml`, the
   directory name is the preset id, the id grammar is exact, discovery rereads
   the user root, invalid or unloadable compositions are broken rather than
   skipped, earlier configured roots win duplicate ids, and `mount()` resolves
   a mountable preset before binding the agent scope to its standing parent;
5. prove from the exact two tool packages that their plugin names are
   `tool-fs` and `tool-fs-search`, that the search configuration requires
   `sampleOverCapGlobResults`, and that their dependency declarations and
   unconditional tool registrations remain exact;
6. prove the mandatory inherited selection sources are exactly:
   `edit` and `read` from `tool-fs`, and `glob` from `tool-fs-search`;
7. separately record the deliberately unselected unconditional names `write`
   and `grep`, plus conditionally possible `read_image`, so evidence never
   mistakes the raw preset surface for the effective boundary;
8. validate the materialised payload byte-for-byte, parse it with a safe YAML
   loader, reject aliases/tags and require exact key sets, values and order;
9. bind the accepted effective-tool guard source and symbolically apply its
   exact restriction to both the minimal inherited set and the attachment-
   present superset, yielding exactly sorted `edit`, `glob`, `read` in both;
10. reject hostile variants including invalid/traversing preset ids, wrong
    directory or filename, symlink payloads, missing/duplicate/reordered/surplus
    rows, renamed plugins, groups, extra keys, unexpected config, missing or
    non-false search sampling, selected-name drift, missing mandatory inherited
    names, scope-local names and bypass/reordering of the accepted guard; and
11. emit contract/schema-valid evidence and a concise report with zero counts
    for Node/native-Harness processes, agents, sessions, turns, broker/model/
    provider requests, occupied workers, network, Docker and database actions.

The controller's `--write` mode may create or replace only its named contract,
schemas, evidence, report and the exact repository-retained preset payload.
`--check` must be read-only and byte-compare every generated artifact. Any
unexpected existing path type, symlink, mismatched byte or out-of-contract
field fails closed.

## Owned artifact surface

The tranche owns only:

- this plan and its threat-model delta;
- `scripts/deepseek_native_harness_provider_free_emr4_bounded_worker_preset_materialisation_recovery.py`;
- `tests/test_deepseek_native_harness_provider_free_emr4_bounded_worker_preset_materialisation_recovery.py`;
- contract, schemas, exact materialised payload, evidence, report and efficacy
  reading under the operation's continuity directory; and
- normal Ariadne runtime-state, receipt, verifier, closeout, acceptance,
  clockwork, register-if-required and Yuri-summary artifacts.

No predecessor file or product source is writable.

## Acceptance

Acceptance requires:

1. exact package, member, predecessor and immutable-attempt bindings pass;
2. all discovery, row-shape, registration, dependency and guard-order source
   predicates pass;
3. the repository payload is byte-exact and its future Harness-home relative
   location is unambiguous;
4. mandatory inherited names are present, surplus names are recorded, and the
   accepted guard's symbolic result is exactly `edit`, `glob`, `read` for every
   admitted attachment posture;
5. every hostile preset or mapping mutation fails closed;
6. provider/runtime/action counts are all zero;
7. focused tests and exact neighboring required-service, guard, native-proof,
   profile-contract and broker tests pass serially with Ruff, Python compile,
   JSON/schema validation and `git diff --check`; and
8. one fresh Gemini 3.7 Flash/high isolated read-only veto passes on the exact
   clean candidate and leaves HEAD and worktree unchanged.

A P0-P2 review finding requires bounded Sol correction and one fresh corrected
veto. A qualifying rejected review, transport or worktree postcondition enters
the clockwork-owned incident register before acceptance. No model may implement
or accept its own candidate.

## Explicit parallelism assessment

- **DeepSeek:** `declined`, negative leverage. The native Harness and bounded
  preset are the provider-free evidence subjects. No native process, occupied
  worker, model/provider request or Claude Code fallback is authorised.
- **Gemini:** `reserved`, required independent leverage. It owns one fresh
  exact-candidate read-only veto only after deterministic acceptance.
- **Native subagents:** `declined`, negative leverage. Current developer policy
  prohibits proactive delegation, and cache semantics, exact payload and the
  accepted guard form one small serial proof boundary.

Sol owns plan, offline inspection, implementation, tests, recovery,
acceptance, clockwork and Git. Reassess all three lanes at deterministic
candidate, pre-verifier and closeout.

## Claim ceiling, protected boundaries and successor

Passing this tranche proves only that one exact rc.7 custom preset payload is
materialised and that its accepted post-mount restriction deterministically
maps the inherited surface to `edit`, `glob`, `read`. It does not prove that a
native Harness can discover or mount it in a live process, that all injected
services activate together, that a scope or effective schema is observed at
runtime, or that any DeepSeek worker is reliable.

No Node/native-Harness process, agent/session/turn, broker/model/provider
request, occupied worker, registry/network access, credential, Docker,
PostgreSQL, SQL or database execution; no product source/configuration/API/
OpenAPI/GraphQL/schema/client/waiting-area change; no ordinary-practice
enablement, feature flag, allowlist, command mounting, generic-status `Arrived`,
action grammar or first-party-client change; no product, patient, appointment,
clinical, historical or protected data; and no production, deployment,
release, Pages, protected evidence or protected-ref movement is authorised.

Local/origin `master` and `handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage explicit paths only; `git add .` and
`git add -A` are forbidden.

At closeout the clockwork is the sole canonical governance writer and must run
a separate `--check` before `--publish`, followed by postpublication tests and
an idempotent check. Sol writes the paired Yuri summary and sends the usual
non-PHI Pushover notification. A future native composition attempt, if it
becomes the narrowest successor, requires its own freshly frozen one-process
plan and latch; this tranche grants it no execution authority.
