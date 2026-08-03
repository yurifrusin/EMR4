# Native-Diary architecture schema-hardening repair — DeepSeek worker packet

Source/candidate head: `2d8ffecd796461ee3987c16c56e3c290cb731923`

Worktree: `C:\Users\sarashera\EMR4-worktrees\diary-application-session-architecture`

Branch: `codex/diary-application-session-architecture`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.

## Rehydration and authority

Read `AGENTS.md` completely and state the five exact rehydration sources before
editing. Re-read the candidate contract, schema and test completely. This is a
bounded repair under the accepted lane authority. Root Sol alone accepts and
integrates. Do not inspect any reviewer output.

## Concrete root finding

The candidate instance is safe and the tests pass, but the JSON schema leaves
nearly every nested security object unconstrained. It admits, for example, a
wrong surface/policy/action/resource, default-on or mounted composition,
inactive enumeration, a GraphQL mutation/command tunnel/event actuator,
authority/privacy boolean reversals and an incomplete implementation boundary.
Those mutations must not remain schema-valid.

## Owned repair files only

- `orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-composition/composition-contract.schema.json`
- `tests/test_raisa_provider_free_native_diary_application_session_practitioner_composition.py`

Do not edit any other file. Do not touch `docs/branding/`, `AGENTS.md`, runtime,
Diary assets, API Spine artifacts, harness settings, protected evidence or
another worktree.

## Required repair

- Make every nested object explicit with `required`, exact `const` values where
  frozen, types and `additionalProperties: false`.
- Encode the exact native Diary surface, accepted policy/action/resource, exact
  query variables/projection, default-off/unmounted preservation, forbidden
  dependencies, fail-closed behaviour, closed/blocked gates, API Spine posture,
  acceptance cases, risks and implementation handoff.
- Make contractual arrays reject missing, reordered, unknown or duplicate
  values as appropriate using Draft 2020-12 constructs.
- Require the exact source head and parent binding for this frozen architecture
  candidate.
- Add adversarial mutation tests using `Draft202012Validator` proving at
  minimum: wrong surface, changed policy/action/resource, inactive enumeration,
  default-on, mounted, REST-fallback replacement, GraphQL mutation, command
  tunnel, event actuator, missing privacy restriction, unknown nested field and
  missing nested field all fail schema validation.
- Preserve the original contract JSON byte-for-byte and all no-runtime/no-
  usability claims.

Do not run pytest; root serializes it. Run Ruff/py_compile, parse and validate
the unchanged contract, run mutation tests directly only if that does not load
`conftest.py`, and run diff hygiene.

Stage exactly the two owned files with explicit paths, verify the staged list
has no `docs/branding/`, and commit. Never use `git add -A` or `git add .`. Do
not fetch, merge, rebase, switch or push. Return exact checks/commit and end with
one `DECISION: pass` or `DECISION: revision_required`.
