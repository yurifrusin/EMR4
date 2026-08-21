# Source-repaired sentinel boot historical-test selection

Date: 2026-08-21

The predecessor repaired-sentinel controller suite retains two assertions bound
to the pre-source-repair controller digest. They remain immutable historical
evidence and are not applicable to the accepted one-byte successor repair:

- `test_deterministic_check_never_launches_native_process`
- `test_direct_script_check_bootstraps_repository_imports`

The first widened invocation retained both selectors and they failed only at
`component_digest_mismatch:repaired_profile_controller`. No Node, Harness,
worker, model, provider or network process was launched. The four other
predecessor selectors passed unchanged when these exact historical selectors
were deselected. The fresh source-repaired suite separately passes all seven
selectors, including direct invocation, deterministic zero-Node admission and
the retained terminal/cleanup verifier.

The historical assertions are preserved; they are neither rewritten nor
treated as current-candidate failures.
