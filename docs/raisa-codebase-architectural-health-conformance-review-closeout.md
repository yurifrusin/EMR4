# EMR4 codebase architectural-health and conformance review closeout

Date: 2026-08-11

Result: `raisa_codebase_architectural_health_conformance_review_accepted_with_bounded_corrective_successor`

Reviewed source: `95ce6b75723d57e672858619c3621d4a273c1f34`

## Accepted result

The bounded findings-only review reconstructs the mounted, default-off,
accepted-unmounted, future and retired architecture and traces the principal
read, command, event and future Bureau paths. The core architecture remains
sound: GraphQL is Query-only and practice-scoped; canonical state change is
REST/OpenAPI-owned; events trigger fresh reads rather than commands; product,
provider and command descendants fail closed by default; and Context Fabric
durability remains unmounted and unapplied.

No P0 or current patient/clinical authority breach was found. Two P1
conformance defects were recorded. The stale Required Git relation in the live
handover is corrected by this closeout. The remaining P1 is a protected-branch
verification gap: the Python 3.11 workflow neither compiles the maintained
application surface nor runs the bounded correctness tests, and whole-app Ruff
inspection found target-incompatible syntax in a tracked, non-mounted
historical evaluation module. One P2 API Spine regression test also fails
because a historical practitioner-directory gap packet is still treated as
current after REST and GraphQL implementation.

The review also records an 8,658-line appointment-router change hotspot, a
latent legacy deterministic-fallback conflict with the model-required doctrine
and stale historical diagrams in the master plan. These do not authorize or
justify a broad refactor.

## Verification result

- 79 focused API Spine/practitioner tests passed before the exact historical
  gap-inventory failure.
- 22/22 repository-maintenance and live GraphQL shell/hardening tests passed.
- Runtime GraphQL has no Mutation or Subscription root and retains its
  authentication, tenant, field and complexity controls.
- Whole-application Ruff under the configured `py311` target reproduced the
  historical-module syntax defect and 33 unused imports; this was diagnostic
  only and no automatic fix was applied.
- `git diff --check` passed.

The expected non-pass is evidence for the review finding, not acceptance of a
broken current runtime. Its bounded successor must repair the conformance suite
before AES-C0 begins.

## Fitness and cadence decision

The repository should own executable checks for source-state classification,
mounted route inventory, actual GraphQL read-only shape, command-family
authority, event/fresh-read behavior, default-off and no-fallback posture,
Python target compilation, baton consistency and lifecycle supersession.
Large-module detection should initially report and require a decomposition note
rather than force a risky rewrite.

Run those checks on every pull request. Run a bounded architecture pulse every
five to eight material tranches or seven active development days, and a deeper
composition review every four to six weeks or before a major product-data,
occupied-tool, command-family or clinical-authority integration.

## Claim boundary

This closeout changes documentation and programme state only. It does not
repair product code, alter route behavior, enable a provider, read product or
patient data, apply a migration, open a watcher, start a work cell, add a tool,
execute a command, deploy, release, rebuild Pages or move a protected ref.

## Programme handoff

The next safe tranche is one bounded provider-free conformance repair. It will:

1. introduce an explicit maintained/protected/historical Python source-state
   selection and make protected CI compile/lint the maintained Python 3.11
   surface without opening holdouts;
2. repair the practitioner-directory historical/current lifecycle test through
   explicit supersession rather than rewriting history; and
3. add baton/current-state consistency checks.

Once that narrow repair passes, AES-C0 architecture and contract proceeds with
the new fitness functions as acceptance constraints. No user decision fork is
present, so the successor may begin immediately under standing uninterrupted-
development authority.
