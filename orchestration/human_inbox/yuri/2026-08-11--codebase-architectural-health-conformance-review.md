# EMR4 codebase architectural-health and conformance review — closeout

- Date: `2026-08-11`
- Outcome: `accepted_with_bounded_corrective_successor`
- Task branch: `codex/ariadne-bernie-davida-parallel-seam`
- Reviewed source: `95ce6b75723d57e672858619c3621d4a273c1f34`
- User attention required: `no`

## Lay summary

Raisa's main structural idea is holding together. The database-backed system,
read-only information paths, human-confirmed action paths and future AI paths
are still separated in the right way. I found no sign that an AI path can
quietly write clinical or appointment truth, and no current patient-data gate
was accidentally opened.

The review did find some workshop-maintenance problems. Our automatic Python
checks look at only part of the code, so they can miss an old non-running file
that no longer works with the Python version the project says it supports. One
old architectural checklist also still says the practitioner directory is
missing even though it has since been built. Finally, too much appointment
behavior has accumulated in one very large file, which will make future change
progressively harder unless it is separated gradually.

These findings do not call for tearing the system apart. They call for one
small housekeeping tranche that makes the automatic checks understand which
parts are current, dormant or historical and prevents stale instructions from
masquerading as current truth.

## Technical summary

The review reconstructed five repository states: mounted current, mounted
default-off, accepted unmounted, future planned and retired historical. The
live GraphQL runtime is Query-only and tenant-scoped. REST/OpenAPI retains
command ownership. Default-off provider, product-context, Rayleen and Davida
gates remain false. Context Fabric durability is accepted evidence, not an
applied migration or operational watcher.

Two P1 findings were recorded. The contradictory handover Git/next-work row is
corrected in this closeout. Protected CI still lacks maintained-surface Python
3.11 compilation and bounded correctness tests; diagnostic whole-app Ruff found
Python-3.11-incompatible syntax in a non-mounted historical evaluation module.
A focused API Spine run passed 79 tests, then reproduced one P2 stale
practitioner-gap assertion. A separate current GraphQL and maintenance packet
passed 22/22.

## Issues exposed or resolved

- Resolved: the live handover no longer directs a closed attempt-016 database
  path while simultaneously accepting attempt 048.
- Exposed: current CI can miss target-version and functional regressions outside
  a narrow allowlist.
- Exposed: historical API Spine packets need explicit supersession so their old
  status cannot be mistaken for current state.
- Exposed: `app/routers/appointments.py` has reached 8,658 lines and should be
  decomposed one characterized route family at a time before more material
  appointment behavior is added.
- Exposed: the legacy deterministic-fallback default must never be inherited by
  a model-required Bureau capability.

## Deliberately still closed

Patient, clinical, product and financial data; providers; applied migration;
operational database/source access; watchers/listeners; model tools; commands;
deployment; production; release; Pages; and protected refs remain closed.

## Place in the Raisa picture

This is an inspection of how Raisa's growing body fits together. It confirms
that the nervous system—read paths, action paths, events and future context—is
still organized around deterministic authority rather than model privilege. It
also gives the project a sustainable review rhythm so rapid agentic development
does not silently accumulate architectural debt.

## Planned next tranche

A bounded provider-free conformance repair will teach CI which Python source is
maintained versus protected/historical, compile and lint the maintained Python
3.11 surface, repair API Spine lifecycle tests without rewriting history and
add baton consistency checks. It can proceed immediately under standing
authority. AES-C0, the first Agent Execution Surface and Containment contract
tranche, follows after that repair passes.

## Evidence and controlling documents

- `docs/raisa-codebase-architectural-health-conformance-review.md`
- `docs/raisa-codebase-as-built-architectural-state-map.md`
- `docs/raisa-codebase-architectural-health-conformance-review-closeout.md`
- `docs/raisa-codebase-architectural-health-conformance-review-plan.md`
