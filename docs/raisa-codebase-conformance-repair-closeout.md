# EMR4 bounded codebase conformance repair closeout

Date: 2026-08-11

Result: `raisa_codebase_conformance_repair_pass`

Source baseline: `8ce3a591fa0e63ad2d68bf95a8d7e24369dd872f`

## Accepted result

The three frozen corrective slices pass without changing product behavior.

CR-1 adds one machine-readable maintained Python source-state manifest. It
selects 202 ordinary maintained Python files through exact files, recursive
safe roots and top-level-only roots; refuses escaping, absent, duplicate,
holdout-named and closed-recursive selections; compiles in memory without
creating bytecode; and derives Ruff's Python 3.11 surface from that one source.
The protected Python workflow now requires its existing exact Python 3.11
runner, compiles the selected surface, runs Ruff and leakage checks, and runs a
bounded 92-test static packet. `--noconftest` deliberately prevents that packet
from importing the shared PostgreSQL fixture or runtime-only dependencies.

CR-2 preserves the July 8 five-row API Spine gap inventory byte-for-byte as
historical posture and adds a current machine-readable lifecycle index. It
records `Query.practice.practitioners` as an implemented, mounted, read-only
REST and GraphQL surface while keeping deployment and production readiness
false. Patient reminders, patient messages, RACGP guidelines and Cochrane
Library remain explicit future gaps. No route, resolver, source or authority
was added.

CR-3 adds a live baton consistency test binding the pre-closeout Continuity
235 / Compass 217 position, protected Git relation, current result, next work
and master-plan handoff. The two diagnosed stale statements that described the
completed architecture review as future work are corrected. The closeout then
advances the accepted repair to Continuity 236 / Compass 218 and hands off to
AES-C0.

The sole product-source change removes one already-diagnosed unused import
from the mounted Bernie UI view-model module. It has no runtime behavior effect.

## Verification

- maintained source-state validation: 202 selected files compiled in memory;
  `protected_paths_enumerated: false`;
- hostile source-state and conformance packet: 30/30 passed;
- CI static packet with `--noconftest`: 92/92 passed;
- canonical local `fast` profile: 98/98 passed, including Ruff, in-memory
  compilation, focused API Spine/handover/receipt/maintenance checks, Diary
  JavaScript syntax and Git whitespace;
- focused practitioner/API Spine lifecycle packet: 117/117 passed;
- pinned local tools match `ruff==0.15.22`, `pytest==9.1.1` and
  `PyYAML==6.0.3`; and
- `git diff --check` passed.

The local development interpreter is Python 3.14. Exact Python 3.11 execution
therefore remains a fail-closed workflow property rather than a local runtime
claim: the workflow selects 3.11, `ci-correctness` rejects any other runtime,
and Ruff parses the selected source against the repository's `py311` target.

## Issues found and resolved

The first full gate found one unused import in the repaired historical API
test and the live handover at its 500-line compactness ceiling; both were
corrected without scope expansion. Review also caught that ordinary pytest
startup would load the shared database conftest in a clean CI environment.
The bounded static CI packet now uses `--noconftest`, while ordinary local tests
retain the serial PostgreSQL fixture contract.

## Claim boundary

This repair adds repository fitness and lifecycle evidence only. It does not
change a product route, GraphQL field, REST command, UI workflow, fallback
runtime, database schema or state. It opens no protected evidence, historical
Diary data, patient/clinical/product data, provider, model, watcher, source,
tool, command, credential, deployment, production, release, Pages or protected
ref.

## Programme handoff

AES-C0 architecture and contract is the next safe planned tranche. It will
freeze the Agent Execution Surface capability classes, external broker trust
boundary, immutable generation manifest, no-fallback state, route/command
separation and fail-closed acceptance. It grants no broker implementation or
executable/product/provider authority. No user-attention fork is present.
