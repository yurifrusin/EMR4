# Context Fabric behavior admission-lock parent rebind

Date: 2026-08-08

Status: candidate deterministic behavior-parent rebind; disposable behavior
runtime remains closed pending a fresh exact-HEAD independent veto.

## Exact repaired parents

The frozen twenty-scenario behavior contract is rebound to the admission-lock
repair chain:

- accepted parse/runtime source
  `a1f8141b05e9f2218412d2d0e7772d3f4dcfead7`;
- inert SQL and render manifest source
  `b0339bed1090f1f04c198ca0fb2bdf2932ca702c`;
- structural contract source
  `3a19167e13ac01996180e1b5ada2a6e2ae7e135f`;
- typed function/trigger body source
  `f42558c14c59c2d37a5b96d4a880941f26038d26`; and
- unchanged prerequisite contract source
  `1fd3445aea5839b7aa889fc962faa8ad2be0c95e`.

The canonical behavior contract digest is
`sha256:a16769b43c8345b3c79cc79d1ca26e4cd0b2d7095515d2b13bc7e21cb27b5b8e`.
The exact scenario population, order, category counts `6/4/3/4/3`, expected
SQLSTATEs, effects and claim boundary are unchanged.

## Lock-policy authority proof

The new `pol_cf_04_update_lock` exists only so the coordinator security-definer
entry point can take its contracted `FOR UPDATE` row lock under forced RLS. It
does not grant table privilege, and its `WITH CHECK` remains fail-closed with
the exact binding predicate followed by `AND FALSE`.

`BTR-R03` therefore gains one fresh-connection forbidden-operation cell:
`coordinator_admission_direct_update`. It attempts a no-op direct update of the
exact authored-synthetic PRIMARY admission and must fail with standard
SQLSTATE `42501`. This is additional evidence inside the already frozen
RLS/privilege scenario, not a twenty-first scenario and not a new authority.

## Gate and boundary

The rebound packet must pass its complete deterministic and hostile tests,
Ruff, `git diff --check` and one fresh exact-HEAD Gemini 3.6 Flash/high veto
before exactly one newly owned, pull-never, networkless, tmpfs PostgreSQL 16
behavior attempt.

This grants no applied migration, operational database or credentials,
persistence, watcher/listener/feed/source access, application/API/Diary
surface, patient/clinical/product data, provider call, command/write,
deployment, production, release, Pages or protected-ref authority.
