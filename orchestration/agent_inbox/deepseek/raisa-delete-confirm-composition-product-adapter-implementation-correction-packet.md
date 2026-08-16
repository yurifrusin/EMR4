# DeepSeek bounded correction — delete-confirm composition/product adapter

Exact worktree: `C:\Users\sarashera\EMR4-worktrees\deepseek-delete-confirm-adapter-eac9846e`

Exact branch: `codex/worker-delete-confirm-adapter-eac9846e`

Required starting HEAD: `d9df95874ea674420b626f5182a68a07e96e6d91`

This is the sole permitted same-lane mechanical correction. Read `AGENTS.md`,
the frozen implementation plan and machine contract completely, verify exact
HEAD/cleanliness/protected refs, and preserve the original candidate commit.

Edit and commit only the same four owned paths. Do not amend the original
commit. Do not edit any existing file, push, or open any forbidden runtime.

## Exact corrections

1. Make `canonical_delete_confirm_envelope_bytes` validate the full receipt
   semantics, not merely shape and warning membership. The simplest acceptable
   construction is to build exact private bytes from every receipt field using
   `canonical_delete_confirm_response_bytes`, validate those bytes, project the
   one expected public envelope, and require the supplied envelope to equal it.
   Reject wrong status, non-null waiting area, invalid/null reason code,
   non-string/overlong cancellation text, blank target, unknown/duplicate/
   reordered warnings, wrong registry text, every changed constant and every
   disclosure/extra field. Add focused hostile public-envelope tests.

2. Enforce the complete proposal/admission boundary before
   `command_session_factory` is called:

   - invalid authenticated bearer/session secret, server HMAC/idempotency/
     session-binding/evidence secrets, missing authenticated user identity,
     inactive/unrecognised role or non-positive server generation => closed 403
     without opening a command session;
   - missing/blank idempotency key => stable 409 without opening a command
     session;
   - unsupported/blocked/unsafe/unconfirmed proposal, warning mismatch, signed
     evidence failure, proposal-generation binding failure or freshness/state
     admission failure => typed 200 blocked without opening a command session;
   - call `delete_confirm_admission_adapter` once against the pre-command ingress
     before opening the session; only `kernel_request_ready` may proceed; and
   - retain the composition's independent repeated admission and locked
     re-admission. A command-session factory exception must fail closed as 503.

   Update tests to assert zero command-session calls and zero physical entries
   for every pre-command stop, and to distinguish proposal/evidence blocked
   results from authenticated-context 403 results.

3. Make the proposal-version HMAC cover exactly two fields:
   `source_version` and `evidence_signature`. Keep `schema_version` in the
   returned envelope and exact shape check, but exclude it from signature
   material. Add a test that independently recomputes the HMAC from exactly
   those two fields and proves schema/signature/output shape separately.

No architecture changes are authorised. Run the exact provider-free tests via
`C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.ariadne_provider_free_pytest --repo-root C:\Users\sarashera\EMR4-worktrees\deepseek-delete-confirm-adapter-eac9846e tests/test_appointment_delete_composition.py tests/test_appointment_delete_product_adapter.py`,
Ruff, compilation, diff checks and post-commit `git show --check`. Commit the
correction as a descendant of the required starting HEAD and report full SHA,
exact paths, test counts and advisory decision. Sol retains acceptance.
