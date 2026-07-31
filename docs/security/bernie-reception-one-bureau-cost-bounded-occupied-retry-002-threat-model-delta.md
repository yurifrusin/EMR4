# Threat-model delta — Bureau cost-bounded occupied retry 002

Status: active
Recorded: 2026-07-31

## Added risks

- A compatibility wrapper could weaken the exact provider boundary instead of
  repeating it.
- The successor could erase or under-account the predecessor reservation.
- An inner exception diagnostic could retain unconstrained exception text.
- The outer UI harness could again mask the causal local failure code.

## Controls

- The compatibility object repeats the exact model, project, Bernie identity,
  keyless ADC, Sydney hostname and explicit false values for API key, fallback,
  global endpoint, tools, database access, product delivery and write
  authority.
- A focused test invokes the actual inner pre-call gate with the successor
  artifacts before any provider-capable execution.
- The successor ledger begins at USD 0.0238049 and hash-binds the predecessor
  terminal ledger hash; the full USD 0.02 predecessor reservation remains
  charged.
- Local diagnostics admit only a fixed allowlist of repository-owned reason
  codes plus booleans describing ledger/audit presence. Raw exception text,
  prompts, responses and credentials are forbidden.
- An HTTP error is classified before runtime-audit reference validation.
- All original isolation, one-call, proofreader, proposal-only, no-fallback,
  no-write and cleanup controls remain unchanged.

## Residual risk

The cost ledger remains a conservative application account, not a billing
quota. Provider billing and Google infrastructure remain external. A
successful Sydney endpoint request does not prove Australian physical or
sovereign processing.
