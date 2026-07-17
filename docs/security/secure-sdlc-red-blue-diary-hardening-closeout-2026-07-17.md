# Secure SDLC Red/Blue and Diary Hardening Closeout

Date: 2026-07-17

## Outcome

The authorized security tranche passed. Ariadne now has an executable,
risk-triggered red/blue/purple review gate; the Diary defence-in-depth repairs
are complete; and GitHub delivery controls are enforced.

Final code candidate:
`73eba9c144ac1a41be5b2e150b9d2c1c7c77675c`.
Representative integration PR: https://github.com/yurifrusin/EMR4/pull/20.

The final PR head passed:

- GitHub aggregate CodeQL;
- `Analyze (python)`;
- `Analyze (javascript-typescript)`;
- Python `security`;
- `Run Manifest Validation & Security Audits`; and
- `Diary smoke review`.

No CodeQL alert was dismissed. Dependabot alert 5 remains the documented
moderate, dev-only, upstream-blocked TeamsFX dependency and was not forced.

## Ariadne protocol

`scripts/ariadne_security_review_gate.py` and
`orchestration/harness_settings/security_review_protocol.yaml` enforce:

- Sol-owned sprint materiality and a complete security delta;
- risk-triggered asymmetric blue and fresh-context red lanes;
- repository-contained, distinct packets and artifacts;
- normalized SHA-256, candidate, and decision binding;
- fail-closed finding schemas and canonical critical/high blocking;
- recovery-lease provenance plus an exact-final independent pass; and
- hash-bound purple cadence with mandatory cross-layer purple synthesis.

DeepSeek V4 Flash/high supplied the original blue review through Claude Code
`--bare`. Sol rejected its conceptual fail-open acceptance and recovered
without a correction loop. Gemini 3.5 Flash ran independent red reviews; each
new code head invalidated the previous pass. The final exact-head review and
Sol purple synthesis both returned `DECISION: pass`.

## Diary repair

The vulnerable/scanner-sensitive path began with URL-controlled smoke/dev
state influencing client authentication branches. The final invariant is:
URL state may select only the local mock-only loader; live Diary rendering can
be entered only by `loadAuthenticatedDiary`, which returns before the shared
renderer without a token. Startup no longer contains URL-controlled auth
conditions.

The tranche also:

- restricts smoke/dev capabilities to loopback or local `file:` QA;
- uses exact approved ngrok suffixes;
- allowlists all five signed-confirm endpoint families before POST;
- uses Web Crypto exclusively for client identifiers; and
- replaces identifier-built selectors with exact dataset comparisons.

Preservation evidence is 45 focused tests and 139/139 full Diary Playwright
cases on the final code, plus Node syntax and whitespace checks. Backend auth,
role, evidence, ownership, state/collision, audit, and idempotency controls
remain authoritative.

## GitHub controls readback

Repository readback after mutation:

- secret scanning: enabled;
- secret scanning push protection: enabled;
- `master` protection: enabled and enforced for administrators;
- required checks: `security`, `Analyze (python)`,
  `Analyze (javascript-typescript)`, and
  `Run Manifest Validation & Security Audits`;
- required checks are strict/up-to-date;
- linear history and conversation resolution are required;
- force pushes and branch deletion are disabled; and
- human PR approval is not required while there is only one maintainer.

Normal protected integration is now pull-request-only. The break-glass and
vulnerability-response SLA are recorded in
`docs/security/vulnerability-response-and-break-glass.md`.

## Process incident and residual risk

One intermediate draft-PR repush at carrier `7b367a5d` followed a passing
security plan gate but did not receive its own fresh push-continuation receipt.
It changed no protected ref or setting. Later final candidate/evidence pushes
had passed prepush receipts, and the complete GitHub gate reran green. The gap
is preserved here rather than retrospectively represented as authorized.

The executable gate cannot infer whether a dishonest manifest omitted a real
security-sensitive change. Sol-owned classification, protected integration,
Git review history, candidate-bound independent evidence, required checks,
and branch protection form the complete control. RLS, comprehensive audit,
JWT browser storage, and field-level encryption remain structural security
work, not regressions introduced here.

Holdouts V1-V10 and all T3/provider/historical-data/product-write boundaries
remained closed.
