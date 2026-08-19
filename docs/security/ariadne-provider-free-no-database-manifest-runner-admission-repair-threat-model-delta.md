# Threat-model delta: provider-free no-database manifest and runner admission repair

Date: 2026-08-20T01:07:26+10:00 (Australia/Brisbane)

## Scope

This delta covers only pre-execution classification of provider-free pytest
selections and digest binding of that decision into the test-only DeepSeek
broker WorkOrder boundary. It opens no Docker, database, provider, product,
data, deployment, Pages or protected-ref surface.

## Threats and mandatory controls

| ID | Threat | Mandatory control |
|---|---|---|
| ND-001 | `--noconftest` is mistaken for proof that selected tests cannot require shared database fixtures. | Parse the selected tests and shared conftest before subprocess creation; reject every shared-fixture reachability edge. |
| ND-002 | Importing a helper from `tests.conftest.py` executes database-adjacent module code despite no fixture request. | Reject static and dynamic conftest imports without importing any selected module. |
| ND-003 | An unknown fixture is silently treated as a harmless pytest builtin. | Freeze an exact versioned core-fixture set; unknown names deny. |
| ND-004 | Autouse, `usefixtures`, local transitive dependencies or indirect parametrization hides an unsafe fixture edge. | Resolve all supported edges recursively; dynamic or ambiguous declarations deny. |
| ND-005 | Admission hashes one file but pytest executes another after a path or content race. | Require literal regular non-symlink files under the exact root; read once, hash and parse the same bytes; runner re-derives immediately before launch. |
| ND-006 | A path selector expands, escapes, duplicates or invokes node-id selection. | Literal `tests/*.py` files only; no globs, `..`, absolute paths, symlinks, duplicates, options or `::` selectors. |
| ND-007 | Manifest preflight and runner use different classifiers. | One reusable pure module and one canonical attestation schema/digest function serve both boundaries. |
| ND-008 | Ordinary pytest bypasses the no-database runner. | Validation manifest rejects `pytest`, `py.test` and `python -m pytest` before any receipt or subprocess. |
| ND-009 | A WorkOrder claims no-database admission but the broker receives different or missing artifacts. | v2 WorkOrder binds both canonical digests; broker loads exact JSON artifacts and validates their mutual binding before ready. |
| ND-010 | Historical v1 compatibility silently admits a new unbound worker. | Node broker accepts v1 only in test mode with an explicit legacy flag; new command-bound starts require v2. |
| ND-011 | Admission itself loads pytest plugins, conftest, database code or provider code. | AST-only standard-library implementation; tests instrument subprocess/import boundaries and require zero such calls. |
| ND-012 | A malformed AST construct is optimistically ignored. | Closed supported grammar; syntax errors, decorators/imports/parametrization that cannot be resolved literally deny. |
| ND-013 | Broker rejection occurs after readiness or simulated provider I/O. | Load and validate WorkOrder plus both bound artifacts synchronously before server creation/listen; hostile tests assert no ready event and no upstream record. |
| ND-014 | The repair becomes a route to occupied attempt-004. | Latch and plan explicitly forbid any occupied attempt; this tranche stops at provider-free broker-boundary proof. |

## Residual limits

The static classifier proves only that the supported pytest fixture declaration
graph contains no shared-conftest dependency. It is not a general Python
side-effect verifier. Test files containing unsupported dynamic behavior are
denied, while admitted test bodies remain governed by the provider-free process
environment, no-conftest launch and the tranche's narrow selected allowlist.
