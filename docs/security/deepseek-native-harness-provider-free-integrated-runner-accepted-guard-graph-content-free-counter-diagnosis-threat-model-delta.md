# Threat-model delta: accepted guard-graph content-free counter diagnosis

Date: 2026-08-22

Timestamp: 2026-08-22T20:13:02.0990867+10:00 (Australia/Brisbane)

Status: frozen zero-process delta

Operation: `deepseek-native-harness-provider-free-integrated-runner-accepted-guard-graph-content-free-counter-diagnosis`

## Changed surface

The tranche adds a deterministic finite-grammar enumerator over one immutable
content-free process envelope. Its risks are grammar undercoverage, accidental
free-form domains, JSON serialization mismatch, hash-uniqueness overclaim,
predecessor reclassification and accidental process launch.

## Controls

- Every input file and executable source dependency is bound by exact bytes
  and SHA-256 before enumeration.
- Key order, constants, types, enums and numeric ceilings are derived from the
  exact fixture, runner and installed helper source and frozen in the contract.
- The grammar includes conservative bounded failure shapes as well as the
  expected success shape; it cannot contain unconstrained strings or numbers.
- Serialization is a dedicated JavaScript-compatible compact UTF-8 function
  with one final LF and hostile tests for ordering, whitespace, booleans and
  nulls.
- Acceptance requires one match over both byte length and SHA-256, not digest
  equality alone. The uniqueness claim is explicitly limited to the frozen
  grammar.
- The controller imports no subprocess launcher and performs no executable,
  network, database, Docker, provider or product action.
- Evidence retains the unique closed typed candidate and aggregate candidate
  counts only. It contains no raw stream, exception, path, environment,
  credential, prompt, response, reasoning or session content.
- The consumed predecessor artifacts are read-only and their rejected result
  remains unchanged.

## Claim ceiling

A pass proves only that one exact source-valid typed serialization uniquely
matches the retained 756-byte digest reading and that its coordinate passed the
old guard boundary. It does not make the predecessor an accepted attempt,
prove native Harness boot, a DeepSeek turn, provider reachability, useful
worker output, product behavior, deployment or production suitability.

Protected evidence, product/patient/clinical data, ordinary-practice changes,
deployment, release, Pages and protected-ref movement remain closed.
