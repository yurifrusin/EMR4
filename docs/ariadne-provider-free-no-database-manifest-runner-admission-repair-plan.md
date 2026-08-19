# Ariadne provider-free no-database manifest and runner admission repair plan

Date: 2026-08-20T01:07:26+10:00 (Australia/Brisbane)

## Authority and exact source

This plan freezes the active operation
`ariadne-provider-free-no-database-manifest-runner-admission-repair` at exact
planning source `440fc7bbd071fbb97a97c986e8c80fe69b83f747`. It follows the accepted
check-in relay-free profile/cleanup repair at exact accepted clockwork source
`31cddb7511be306ecadbe02555cec8cd1f8c200e` and Yuri's standing uninterrupted-
development authority.

The prior tranche proved its mechanism but rejected its original tranche-wide
zero-database claim: two local verification entry points reached the shared
PostgreSQL fixture before collection could be treated as provider-free. This
repair therefore moves the no-database decision ahead of process launch.

## Frozen objective

Implement the narrowest deterministic admission control that:

1. rejects ordinary `pytest`, `py.test` and `python -m pytest` entry points in
   admitted command manifests;
2. parses selected literal `tests/*.py` files without importing or collecting
   them;
3. rejects any selected test whose statically resolved fixture graph can reach
   a fixture declared in `tests/conftest.py`, any direct or dynamic conftest
   import, any unknown fixture, or any ambiguous/dynamic fixture declaration;
4. admits only fixed pytest-core fixtures and completely resolved file-local
   fixtures, including their transitive dependencies, autouse fixtures,
   literal `usefixtures` marks and literal parametrization bindings;
5. produces one canonical no-database attestation whose digest is identical at
   manifest preflight and provider-free runner launch; and
6. binds the exact command-manifest and no-database-attestation digests into a
   v2 DeepSeek WorkOrder which the broker validates, with independently supplied
   artifact bytes, before `broker-ready` or any simulated upstream I/O.

The classifier is intentionally syntactic. It does not claim to prove arbitrary
Python safe. Unsupported syntax is a denial, not a heuristic success.

## Exact admitted surface

The implementation surface is restricted to:

- one reusable pure static-admission module;
- the existing provider-free pytest runner;
- the existing validation-manifest runner;
- the transactional WorkOrder builder and native-harness broker boundary;
- their exact unit, integration, plan and hostile-mutation tests;
- tranche-local contract, evidence, review and closeout artifacts; and
- the existing clockwork closeout path.

No selected test module, `tests/conftest.py`, pytest plugin, Docker client,
database driver or provider SDK may be imported or invoked by admission.

## Fail-closed rules

The engine must reject before subprocess creation when it observes any of:

- a selector other than a literal repository-relative `tests/*.py` file;
- a missing file, symlink/path escape, duplicate selector or source-read race;
- syntax error, star import, conftest import, dynamic import of conftest, dynamic
  fixture name, dynamic `usefixtures`, dynamic parametrization names/indirect
  controls, fixture override ambiguity or fixture dependency cycle;
- a test or local autouse fixture dependency supplied by shared conftest;
- a dependency absent from the file-local fixture set, literal parametrization
  bindings and the frozen pytest-core fixture set; or
- manifest/admission digest absence, mismatch, replay or mutation at the v2
  broker boundary.

The fixed pytest-core set is versioned in code and evidence. Adding a name is a
future reviewed change. File content is read once into bytes, hashed and parsed
from those exact bytes so the attestation cannot describe different source from
the source classified.

## Broker compatibility rule

`ariadne.deepseek_work_order.v2` is the only WorkOrder admitted for new command-
bound provider-free broker starts. It adds exact
`command_manifest_sha256` and
`provider_free_no_database_admission_sha256` bindings. Historical v1 validation
remains available to existing Python clock-chain evidence; the Node broker may
accept v1 only when both test mode and an explicit legacy-v1 compatibility flag
are set. There is no production or occupied broker enablement in this tranche.

## Acceptance

Acceptance requires all of the following without ordinary pytest, Docker,
PostgreSQL, a provider call or an occupied DeepSeek attempt:

1. the previously misclassified A5.1 test file is rejected before subprocess
   creation because its `tests.conftest` import and `practice` fixture are
   reachable;
2. fixed safe synthetic files and the tranche's own tests are admitted and run
   through `python -m scripts.ariadne_provider_free_pytest`;
3. direct pytest, path/symlink escape, conftest import, shared fixture, unknown
   fixture, autouse dependency, indirect parametrization, cycle, digest drift,
   missing artifact and legacy-v1-without-switch mutations all reject;
4. validation preflight and provider-free runner derive byte-identical
   attestations for identical inputs;
5. a v2 WorkOrder is derived with the two exact digests and the broker rejects
   every missing or mutated binding before `broker-ready` and upstream I/O;
6. existing clock/event validation and explicit test-only v1 historical
   compatibility remain intact;
7. deterministic provider-free tests, Ruff and compile checks pass;
8. one fresh Gemini 3.7 Flash/high read-only veto reviews the exact clean
   candidate; DeepSeek is not used to review its own admission repair; and
9. closeout uses the governance clockwork, an explicit-path commit/push, paired
   Yuri summary and the usual non-PHI Pushover notification.

## Explicit parallelism assessment

- DeepSeek: declined for implementation and review. Its native harness remains
  paused pending the separate stock-headless-to-custom-runner boot proof, and
  this tranche changes the very broker boundary that would control it. Claude
  Code is not a fallback.
- Gemini: reserved for one fresh exact-candidate read-only veto after the
  deterministic candidate is complete. It owns no implementation or repair.
- Native subagents: declined. Current session policy does not authorize them,
  and the classifier, manifest and broker bindings form one tightly coupled
  serial authority boundary.

## Protected boundaries

This tranche authorises no product or API behavior, ordinary-practice
enablement, action grammar, first-party client, waiting-area movement,
product/patient/clinical data, live provider, production runtime, deployment,
release, Pages or protected-ref movement. It authorises no attempt-004. Local
and origin `master` and `handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. All untracked files, especially
`docs/branding/`, remain preserved. Staging is by explicit path only.

## Reasoning level

Extra High for the reusable admission and WorkOrder authority boundary; High
for implementation and deterministic verification.
