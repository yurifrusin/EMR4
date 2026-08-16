# DeepSeek correction packet — exact private-receipt byte admission

Date: 2026-08-16

Timestamp: 2026-08-16T17:00:07.6054524+10:00 (Australia/Brisbane)

Model: DeepSeek V4 Flash/high through Claude Code `--bare`

Semantic source: `5aaed2a859c64062d40dd2fe1b419d48dcc5d821`

Rejected candidate: `aabb6b26e4a216092c4c7efbc79f6c5caa01ba79`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r194`

## Admission finding

The isolated candidate is rejected for one exact defect. The frozen plan says
the public pure projection validates the stored private bytes and preserves the
accepted exact ordered six-field physical byte contract. The candidate test
constructs the private receipt with `json.dumps(..., sort_keys=True)` and the
projection accepts that reordered, whitespace-padded byte sequence. Independent
reproduction showed both the accepted compact physical sequence and the
noncanonical sorted/whitespace sequence return a public envelope.

## Bounded correction

Read `AGENTS.md` completely and the four frozen architecture authorities. Then
modify only these two already-owned files:

1. `scripts/raisa_provider_free_unmounted_delete_confirm_response_compatibility_product_adapter_architecture.py`
2. `tests/test_raisa_provider_free_unmounted_delete_confirm_response_compatibility_product_adapter_architecture.py`

In `project_public_envelope`, after strict decoding and semantic validation,
reconstruct the exact accepted private payload in this insertion order:

`appointment_id`, `status`, `status_reason_code`, `cancellation_reason`,
`waiting_area_id`, `warning_codes`.

Serialize it with `ensure_ascii=False`, `allow_nan=False`, and compact
separators `(',', ':')`. Require byte-for-byte equality with the supplied
receipt bytes before projection. This must fail closed for sorted/reordered
keys, added whitespace, CRLF, duplicate keys, alternate Unicode escaping and
any other noncanonical representation. Keep the existing strict field/value,
warning-registry and no-leakage checks.

Replace the clean projection test input with the exact compact physical bytes.
Add explicit negative tests for sorted/reordered keys, whitespace, CRLF,
duplicate keys and alternate escaping, plus a direct assertion that the clean
bytes use the frozen six-field order. Preserve all existing hostile evidence,
schemas, evidence JSON and semantics unchanged.

Run the focused test, relevant provider-free API Spine preflight test, Ruff and
`git diff --check`. Commit only the two modified files with explicit-path
staging; do not amend the rejected commit, push or change any other path. Return
the exact correction commit/tree, changed paths and tests.

All original closed boundaries remain in force: no product/route/schema/
migration edit or call, no database/Docker/SQL, no capability, data, provider,
credential, network, UI, deployment, release, Pages or protected refs.
