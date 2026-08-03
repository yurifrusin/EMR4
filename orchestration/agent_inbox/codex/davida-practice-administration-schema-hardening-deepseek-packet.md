# Davida architecture schema-hardening repair — DeepSeek worker packet

Source/candidate head: `19444399778dbd07b62223ca9b8a118a03d92d5b`

Worktree: `C:\Users\sarashera\EMR4-worktrees\davida-practice-administration-architecture`

Branch: `codex/davida-practice-administration-architecture`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.

## Rehydration and authority

Read `AGENTS.md` completely and state the five exact rehydration sources before
editing. Re-read the candidate contract, schema and test completely. This is a
bounded repair under the accepted lane authority. Root Sol alone accepts and
integrates. Do not inspect prior Gemini output.

## Concrete root finding

The candidate instance is safe and the tests pass, but the JSON schema does not
enforce the security-critical contract it purports to validate. For example,
it admits arbitrary operation codes; `closed: false`; `mutable: true`;
authority/identity/emission/event boolean reversals; incomplete future command
fields; arbitrary tranche entries; and incomplete nested objects. A malicious
or accidental authority-bearing mutation can therefore remain schema-valid.

## Owned repair files only

- `orchestration/continuity/davida-practice-administration-boundary/capability-contract.schema.json`
- `tests/test_davida_practice_administration_boundary.py`

Do not edit any other file. Do not touch `docs/branding/`, `AGENTS.md`, runtime,
API Spine artifacts, harness settings, protected evidence or another worktree.

## Required repair

- Make every security/authority-bearing nested object explicit with `required`,
  typed or `const` fields and `additionalProperties: false`.
- Encode the exact six operation codes, their exact kind/risk/mutable tuple and
  exact array order/length (e.g. `prefixItems` plus `items: false`).
- Encode exact authority, topology, forbidden-authority, context-desk, emission,
  future backend envelope, event, API Spine, four-tranche, execution-control and
  blocked-gate values. Arrays that are contractual must reject missing,
  reordered, unknown or duplicate elements as appropriate.
- Require the exact source head and accepted parent/authority posture for this
  frozen architecture candidate, not merely any 40-hex string where a changed
  binding would be unsafe.
- Add adversarial mutation tests using `Draft202012Validator` that prove at
  minimum: arbitrary operation, `closed=false`, `mutable=true`, DB credential
  authority, confirmation/write emission, event payload as truth, missing human
  confirmation construction, missing optimistic-concurrency field, altered
  tranche, unknown nested field and missing nested field all fail schema
  validation.
- Preserve the original contract JSON byte-for-byte and preserve architecture-
  only/no-runtime claims.

Do not run pytest; root serializes it. Run Ruff/py_compile, parse and validate
the unchanged contract, run the mutation tests directly only if that does not
load `conftest.py`, and run diff hygiene.

Stage exactly the two owned files with explicit paths, verify the staged list
has no `docs/branding/`, and commit. Never use `git add -A` or `git add .`. Do
not fetch, merge, rebase, switch or push. Return exact checks/commit and end with
one `DECISION: pass` or `DECISION: revision_required`.
