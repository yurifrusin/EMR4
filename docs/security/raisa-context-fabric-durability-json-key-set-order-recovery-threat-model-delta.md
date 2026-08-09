# Threat-model delta: durability JSON key-set order recovery

Date: 2026-08-09

Status: bounded provider-free renderer recovery; behavior runtime closed

## Scope change

Behavior attempt 026 exposed one deterministic renderer mismatch:
`JSON_KEYS_EXACT` sorted observed JSON object keys but did not canonicalize the
fixed expected key set. This change is limited to canonical expected-array
emission. It changes no admitted key, authority, database principal, policy,
trigger, entry point, scenario or product interface.

## Threats and controls

| Threat | Control | Required evidence |
|---|---|---|
| Canonicalization weakens exact key admission | Only order changes; array equality and the fixed unique body keys remain | Same six keys before/after; missing or extra keys still unequal |
| Renderer silently accepts arbitrary or duplicate keys | Body validator still requires fixed non-empty unique strings; renderer only sorts the admitted list | Existing validator tests plus direct duplicate/unknown hostile cases |
| A one-off producer patch leaves other guards inconsistent | Generic `JSON_KEYS_EXACT` lowering is corrected once | Exactly seven canonical artifact occurrences and zero predecessor occurrences |
| Sorting changes body authority | Immutable body source and contract remain exact | Parent hashes and body-program identity proof |
| Failed evidence is overwritten | Attempt 026 has an immutable byte-identical copy; mutable evidence remains unstaged until a pass | SHA-256 and byte-equality test |
| Diagnosis overclaims from a shared SQLSTATE | The repository coordinate maps to exact function assertion `p12`; predecessor SQL and body AST jointly identify its sole `JSON_KEYS_EXACT` | Deterministic diagnosis receipt, no new runtime and no raw error text |
| Recovery is mistaken for runtime readiness | Fresh characterization, exact parse, parent rebind, veto and full behavior pass remain mandatory | No behavior attempt 027 before all gates pass |

## Residual risk

Passing this repair will not prove concurrent execution, crash/unknown-commit
recovery, retention behavior, operational storage or credentials, performance,
watcher/listener integration or product wiring. Parse/catalogue installation
still does not execute every stored branch; the frozen twenty behavior
scenarios remain the next bounded execution proof.
