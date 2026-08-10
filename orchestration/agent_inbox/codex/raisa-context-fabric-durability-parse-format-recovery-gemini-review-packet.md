# Independent veto packet: parse formatting recovery

Date: 2026-08-10

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r152`
- Branch: `codex/review-context-fabric-parse-format-e5a51232`
- Rejected candidate: `58538b3b98de4bf4f62a0eef898439d674f3f987`
- Replacement candidate: `e5a51232a7d1c503e772e8467f7241d971c184b7`
- Protected refs: exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform and name the complete five-source `AGENTS.md` rehydration.

## Purpose and required challenges

The r151 veto returned `revision_required` only because Ruff format identified
two non-canonical test files. Independently verify that the replacement changes
only canonical formatting plus preserves the immutable r151 provenance; that
both named files and the full twelve-file static packet are now formatted; and
that every substantive r151 challenge still passes.

Run the exact builder, inert rehearsal, 462-test pytest, twelve-file Ruff check,
twelve-file Ruff format check, exact parent resolution, diff check, HEAD and
clean-status commands listed in the committed
`orchestration/agent_inbox/codex/raisa-context-fabric-durability-parse-exact-evidence-gemini-review-packet.md`, replacing basetemp `emr4-gemini-r151` with
`emr4-gemini-r152` and the final candidate/diff endpoint with
`e5a51232a7d1c503e772e8467f7241d971c184b7`.

Additionally run:

```powershell
git diff --check 58538b3b98de4bf4f62a0eef898439d674f3f987..e5a51232a7d1c503e772e8467f7241d971c184b7
git diff --stat 58538b3b98de4bf4f62a0eef898439d674f3f987..e5a51232a7d1c503e772e8467f7241d971c184b7
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py
```

Report exact 462-test and 12-file formatting counts. Reconcile actual constants
and filenames directly from the code; do not repeat r151 prose that mislabeled
the generic characterization target or the historical failure filename.

## Boundaries and decision rule

Do not edit, format, commit, push, start Docker/PostgreSQL, inspect branding,
access product/protected data, deploy, move refs or use another provider. Return
`fail` for any P0-P2 finding, failed command, substantive drift or dirty
postcondition. Otherwise return one exact `pass` with HEAD and cleanliness.
