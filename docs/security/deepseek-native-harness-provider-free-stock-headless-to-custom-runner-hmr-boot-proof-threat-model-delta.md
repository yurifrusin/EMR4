# Threat-model delta: DeepSeek native Harness provider-free HMR boot proof

Date: 2026-08-20T02:07:29+10:00 (Australia/Brisbane)

## Scope

This delta covers one exact `@deepseek-ai/dsh@0.1.0-rc.7` provider-free native
process from stock headless boot through watched profile-patch convergence to a
local exit-owning custom runner. It opens no model, provider, occupied-worker,
product, data, database, Docker, deployment, Pages or protected-ref surface.

## Threats and mandatory controls

| ID | Threat | Mandatory control |
|---|---|---|
| HMR-001 | A different Harness build passes while rc.7 remains broken. | Verify exact name/version, package bin, tarball SHA-1 and npm integrity before materialisation. |
| HMR-002 | npm silently downloads a missing dependency or runs a package lifecycle hook. | Exact local tarball plus `--offline --ignore-scripts --no-audit --no-fund`; any cache miss is terminal denial. |
| HMR-003 | The proof bypasses the package launcher or uses an invented profile. | Invoke package-declared `lib/bin.js` with documented `--profile headless`; verify the shipped two-bundle profile tuple. |
| HMR-004 | The original HMR prerequisite is not actually exercised. | Pass Node `--expose-internals`; require the real rc.7 HMR service and its two exact `registerConfig` entries before mutation. |
| HMR-005 | The custom runner was mounted initially, so HMR did not cause convergence. | Initial patch digest and structural validation forbid the custom row; only the atomic second patch may add it. |
| HMR-006 | The stock runner reaches a model/provider before the proof runner. | Disable `headless-runner`, `code-runtime` and telemetry before boot; fail structural preflight if any is enabled. |
| HMR-007 | A loaded provider plugin makes an implicit credential or network request. | Scrub credential-bearing environment names, disable telemetry, install a fail-closed DNS/socket/TLS/HTTP/fetch guard and require zero attempt events. |
| HMR-008 | Controller polling fabricates readiness. | Only the in-process sentinel may record readiness, after inspecting the active HMR service's exact config registry. |
| HMR-009 | A file race yields a partial or unrelated patch. | Write fixed bytes to a sibling temporary file, flush/close, then use same-directory atomic replacement; retain before/after digests. |
| HMR-010 | Duplicate or reordered events disguise an early/late failure. | Strict schema, fixed unique event sequence, monotonic in-process sequence numbers and controller-side order validation. |
| HMR-011 | A hung or child process survives and is mistaken for success. | One process identity, bounded deadline, terminate/kill escalation, mandatory wait/readback and process-absence proof. |
| HMR-012 | Cleanup failure is hidden by a successful app exit. | Cleanup is an independent mandatory acceptance field; residual exact root or process makes the whole proof fail. |
| HMR-013 | Raw logs or environment disclose credentials or local paths. | Retain bounded classifications/counts/digests only; never persist raw environment, stdout/stderr, npm cache or disposable paths. |
| HMR-014 | A successful boot proof silently authorises occupied attempt-004. | Result wording and latch explicitly stop at provider-free startup proof; occupied work requires a new frozen tranche. |
| HMR-015 | A failed native terminal is casually retried until it passes. | The first native process terminal is immutable evidence; no automatic retry, and a successor requires a new plan/latch. |

## Residual limits

The proof demonstrates the pinned local rc.7 launcher/HMR lifecycle on the
observed Windows/Node runtime. It does not prove future Harness releases,
different Node versions, model or provider behavior, coding usefulness,
production isolation, or absence of all possible operating-system side
channels. The local network guard is a detection-and-denial control for the
Node primitives reachable by this composition, not a general VM boundary.
