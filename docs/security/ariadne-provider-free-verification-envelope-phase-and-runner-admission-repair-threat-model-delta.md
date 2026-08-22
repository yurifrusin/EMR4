# Threat-model delta — provider-free verification-envelope phase and runner admission

Date: 2026-08-23

Timestamp: 2026-08-23T05:30:28.8721970+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`ariadne-provider-free-verification-envelope-phase-and-runner-admission-repair`

This delta covers only deterministic verification-command admission. It opens
no database, product, provider, runtime or deployment surface.

## Assets

- the exact declared database-authority state;
- the exact prepublication/postpublication command partition;
- the invariant that database-closed verification never loads repository
  conftest or its shared PostgreSQL fixtures;
- stop-before-launch behavior for malformed or hostile envelopes; and
- historical v1 manifest replay without silent reinterpretation as v2.

## Threats and controls

| ID | Threat | Fail-closed control |
|---|---|---|
| VE-001 | A database-closed manifest invokes `python -m pytest`. | Shared runner classification rejects ordinary pytest before subprocess launch. |
| VE-002 | A database-closed manifest invokes `scripts.ariadne_serial_pytest`. | Shared runner classification rejects the serial database-capable launcher before subprocess launch. |
| VE-003 | A caller omits database authority and relies on prose. | V2 requires the exact manifest field; missing or unknown values reject. |
| VE-004 | A command receives a descriptive or unknown phase. | V2 accepts only the two closed phase values. |
| VE-005 | A postpublication command is run before publication. | The runner requires the caller to select one exact phase and executes only that partition. |
| VE-006 | A prepublication command appears after postpublication work. | Manifest admission requires monotonic phase order. |
| VE-007 | A hostile command hides pytest behind a permitted Python spelling. | Classification normalizes admitted Python executable names and `-m` module coordinates. |
| VE-008 | A provider-free test selection escapes the repository or reaches shared database fixtures. | Existing repository-bound static no-database admission and its digest remain mandatory. |
| VE-009 | A malformed v2 manifest reaches generation construction. | Clockwork validates authority, phase, command shape and runner semantics before preparing a generation. |
| VE-010 | V2 silently changes immutable historical v1 meaning. | V1 follows its existing exact schema and behavior; all new fields are opt-in v2 only. |
| VE-011 | Validation output persists command stdout, secrets or environment. | Existing validation receipts retain only bounded status, byte counts and SHA-256 digests. |
| VE-012 | A test of this repair itself loads conftest or PostgreSQL. | Every repository test is invoked through the accepted provider-free runner; subprocess behavior uses fakes or isolated temporary commands. |
| VE-013 | Phase typing is recorded but bypassed by free-form closeout commands. | This tranche's own clockwork command manifest uses v2, and acceptance admits only phase-bound manifest commands and their exact postpublication continuation. |
| VE-014 | The repair broadens product or occupied authority. | The active latch and plan prohibit product/API/client/configuration, database, provider, worker and attempt-008 action. |
| VE-015 | Unrelated user files or protected refs move. | Explicit-path staging, ref readback and preserved `docs/branding/` checks remain mandatory. |

## Residual risk

The gear can classify declared direct and serial pytest coordinates; it cannot
prove that an arbitrary non-pytest program never accesses a database. Future
database-closed manifests therefore remain allowlisted and evidence-bounded.
This tranche proves no occupied execution, database behavior, product safety or
attempt-008 readiness.
