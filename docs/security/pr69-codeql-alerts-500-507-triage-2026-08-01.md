# PR 69 CodeQL security-alert triage and reconciliation

Date: 2026-08-01 (Australia/Brisbane)
Owner: `@yurifrusin`
Branch: `codex/ariadne-terra-gemini-comparative-rehearsal`
Required starting HEAD: `4ef4b75a89baafa1cd69636e7160308cbcbd6e14`

## Scope and boundaries

This record covers all seven CodeQL alerts with a non-null security severity on
the PR 69 merge ref at triage time. It authorises only repository repair,
regression tests, exact native alert reconciliation, and fast-forward commits
to the task branch. It grants no provider call, credential read, product-data
access, deployment, or movement of `master`, `handoff/current`, or their remote
counterparts.

The native state was read before mutation from each alert's
`most_recent_instance`: all seven were `open` on `refs/pull/69/merge` at merge
commit `236b4bc42a042b4f4d49ad8ab5f5f73defc3a993`. The top-level GitHub API
`state` field was null for these PR-scoped alerts, so the instance state is the
authoritative observed value recorded below.

## Exact inventory and disposition

| Alert | Rule | Severity | Exact instance | Triage | Repository disposition | Desired native state |
|---:|---|---|---|---|---|---|
| 500 | `js/file-access-to-http` | medium | `scripts/ariadne_comparative_one_use_broker.mjs:165` | confirmed, bounded accepted risk | The file is the explicit `/run/secrets/provider_key` broker input. It becomes only an authentication header to the exact HTTPS host selected from the closed Terra/Gemini lane table. The broker also enforces one-call accounting, fixed path/model, time and byte bounds, and no fallback. | dismissed, GitHub reason `won't fix` |
| 501 | `py/clear-text-storage-sensitive-data` | high | `scripts/ariadne_terra_gemini_comparative_rehearsal.py:771` | confirmed, bounded accepted risk | Docker's read-only file mount requires a host file. `_secret_file` creates it inside `TemporaryDirectory`, applies mode `0600`, mounts it read-only only into the broker, excludes it from the work cell and environment, and removes it when the context exits. | dismissed, GitHub reason `won't fix` |
| 503 | `py/incomplete-url-substring-sanitization` | high | `scripts/reception_one_bureau_post_admission_runtime_hardening.py:346` | confirmed | Replaced the `aiplatform.googleapis.com` substring check with exact membership in a three-host closed allowlist. | fixed by CodeQL rerun |
| 504 | `py/incomplete-url-substring-sanitization` | high | `scripts/reception_one_bureau_post_admission_runtime_hardening.py:347` | confirmed | Replaced the `generativelanguage.googleapis.com` substring check with the same exact membership boundary. | fixed by CodeQL rerun |
| 505 | `py/incomplete-url-substring-sanitization` | high | `scripts/reception_one_bureau_post_admission_runtime_hardening.py:348` | confirmed | Replaced the `api.openai.com` substring check with the same exact membership boundary. | fixed by CodeQL rerun |
| 506 | `py/polynomial-redos` | high | `app/services/bernie/semantic_extraction.py:825` | confirmed | User-controlled whitespace is collapsed in one pass before the `or later` matcher; the matcher now has fixed separators and no adjacent unbounded repetitions. | fixed by CodeQL rerun |
| 507 | `py/polynomial-redos` | high | `app/services/bernie/semantic_extraction.py:1622` | confirmed | The move-target suffix is whitespace-normalised in one pass and matched with a compact grammar that contains no unbounded whitespace quantifier. | fixed by CodeQL rerun |

## Regression evidence

- `tests/test_bernie_semantic_extraction.py` covers ordinary, repeated-space,
  tab, newline, compact move-time, and 100,000-character adversarial inputs.
- `tests/test_reception_one_bureau_post_admission_runtime_hardening.py` proves
  the three exact provider hosts are detected and all three
  `trusted-host.attacker.example` suffix variants are rejected.
- `review/test_diary_smoke.py` moves the seven stale legacy-review cases onto
  the authenticated non-smoke route. Smoke mode continues to expose the
  current `Project view` entry point and keep the retired Bernie launch button
  hidden.

## Native mutation protocol

1. Commit and fast-forward push this record, register revision 2, code repairs,
   and tests before changing any native alert.
2. Re-read alerts 500 and 501 and require their PR instance state to remain
   `open`; then dismiss them with GitHub reason `won't fix` and the exact
   register comment.
3. Push no manual disposition for 503-507. Require the PR CodeQL analysis to
   observe the code repairs and close them as fixed.
4. Read every alert back, persist the exact final state/timestamps/reasons in a
   separate PR 69 reconciliation artifact, update the register, and commit that
   evidence on the same task branch.

No native disposition is evidence of production suitability or authority for
another provider run. Expiry and reopening conditions remain binding in
`docs/security/security-finding-register.json`.

## Final reconciliation

At task head `ea6e1dfc41b1fbd1ea7875140492172e46f0e6a3`, GitHub CodeQL and
Diary smoke review both passed. Alerts 503-507 read back as `fixed`; alerts 500
and 501 read back as `dismissed` with reason `won't fix` and their exact durable
comments; the PR merge ref query returned zero open security-severity alerts.
The immediate mutation readback also detected and repaired one comment-
interpolation defect through an audited reopen/re-dismiss cycle. Exact states,
timestamps, checks, mutation counts, and closed boundaries are recorded in
`orchestration/continuity/pr69-security-ci-repair/native-alert-reconciliation-evidence.json`.

## Protected-review follow-up

The final protected review also inspected three unresolved CodeQL review
threads outside the security-severity inventory above. Alerts 533, 537 and 538
are `note`-severity maintainability findings with no `security-severity` tag.
The task branch removed the unreachable `generation_row = None` assignment and
replaced two protocol-body ellipses with explicit `pass` bodies. These changes
do not alter persistence, audit, authorization or transport behavior.

The affected shared-auth suites pass 100 selected tests. The immutable
`test_provider_free_acceptance_evidence_matches_runtime` historical-report
equality node was intentionally deselected because its accepted artifact hashes
the runtime source file; the accepted historical evidence was not regenerated.
Ruff and `git diff --check` also pass. Alerts 533, 537 and 538 must close as
fixed on the task-branch CodeQL rerun before protected integration.
