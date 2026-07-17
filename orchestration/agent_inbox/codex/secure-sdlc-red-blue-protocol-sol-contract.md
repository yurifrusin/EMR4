# Secure SDLC Red/Blue/Purple Protocol — Sol Contract

Date: 2026-07-17

## Authority and scope

Yuri authorized the risk-triggered security-review protocol, the bounded Diary
defence-in-depth remediation, and the protected-delivery controls recommended
by the completed Secure SDLC review. GPT Sol remains Conductor, security
adjudicator, integrator, commit/push owner, and GitHub-settings owner.

This tranche may change only:

- Ariadne security-review settings, gate code, tests, and protocol documents;
- the published Diary client and its focused security/UI tests;
- workflow trigger configuration needed to make selected required checks
  stable;
- security closeout, handover, and Ariadne evidence; and
- the authorized GitHub `master` protection and secret-scanning settings.

It may not open any holdout V1-V10, T3.1-T3.5, provider, historical-data,
clinical/runtime, database, deployment, release, or new write-authority gate.
Dependabot alert 5 remains upstream-blocked and must not receive a forced
override.

## Patch contract

The current backend independently enforces authentication, role, evidence,
current-state, owner, collision, audit, and idempotency boundaries, so the ten
validated CodeQL high candidates do not survive as high findings. The Diary
still exposes avoidable ambiguity and scanner noise through four client-side
patterns:

1. smoke/dev URL capabilities are not consistently restricted to localhost;
2. signed confirmation destinations are normalized but not client-allowlisted;
3. correlation/idempotency identifiers fall back to `Math.random`; and
4. appointment identifiers are interpolated into selector strings.

The remediation must preserve local smoke/dev review, the five canonical
signed-confirm route families, secure-context operation, and appointment
re-selection. It must fail closed for non-local dev flags, unknown confirmation
paths, unavailable secure randomness, and untrusted selector syntax.

## Executable protocol acceptance

- Every material sprint supplies a complete security delta.
- Named security-sensitive triggers require an independent blue control/test
  lane and a fresh-context red adversarial lane.
- Red and blue receive asymmetric packets and cannot share acceptance framing.
- A Sol-owned purple synthesis is required after four material sprints, for a
  cross-layer tranche, or before external exposure/deployment/release.
- The gate fails closed at plan and acceptance phases; acceptance requires
  passed artifacts and no unresolved critical/high issue.
- DeepSeek V4 Flash/high through Claude Code `--bare` is the economical blue
  worker; Gemini 3.5 Flash through a fresh Antigravity project is the preferred
  independent red worker. Neither can integrate or certify itself.

## Current worker packets

Blue packet: exact frozen implementation diff plus focused test commands;
review control completeness, preservation, and bypasses. It must not read the
red packet or author acceptance.

Red packet: exact frozen implementation diff, threat model, and malicious
inputs only; attempt bypasses without reading the blue artifact or Sol's
acceptance rationale. Return `pass` or `revision_required` with reproductions.

Purple synthesis: Sol reconciles both artifacts, independently reruns required
checks, records disagreements and residual risk, and alone decides integration.

## Delivery-control recommendation selected

Use required stable security checks with enforced administrators, but do not
require a human PR approval while the repository has a single maintainer.
Normal integration moves to pull requests whose checks must pass. Emergency
break glass is a temporary, owner-only settings relaxation with a committed
incident record, restoration within one business day, and retrospective
review. Vulnerability targets are: critical triage within 24 hours and repair
within 72 hours; high triage within 3 business days and repair within 14 days;
medium triage within 14 days and repair within 60 days; low/dev-only review
within 30 days and disposition within 90 days or documented upstream blocking.

## Acceptance gates

- focused Ariadne protocol and Diary regression tests pass;
- `node --check docs/diary/diary.js` passes;
- local Diary smoke and confirmation tests pass;
- Python Security, CodeQL Python/JavaScript, and Node production security checks
  are stable on the integration PR before becoming required;
- fresh blue and red artifacts pass, followed by Sol purple synthesis;
- secret push protection and `master` protection read back exactly;
- Git refs align and the worktree is clean after protected integration.
