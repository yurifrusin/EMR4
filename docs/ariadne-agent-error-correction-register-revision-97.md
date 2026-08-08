# Ariadne agent error and correction register revision 97

Date: 2026-08-08

Status: accepted register correction

Revision 97 adds AER-0117 and AER-0118, bringing the register to 118 bounded
incidents.

## AER-0117 — static diagnosis presented as sole runtime cause

The independent fixture-repair veto correctly observed the missing foreign-key
parents but overstated that static finding as the sole cause of the generic
bootstrap failure. The next exact-head run still failed at
`fixture/bootstrap_failed`. The topology correction remains valid; its claimed
causal sufficiency does not.

Future reviews may call such a finding a plausible contributor until a safe
runtime discriminator confirms the first-effective branch.

## AER-0118 — bootstrap failure discarded safe SQLSTATE

The harness correctly discarded raw PostgreSQL messages and SQL, but it also
discarded the single five-character SQLSTATE needed to distinguish repeated
bootstrap failures. Three attempts therefore retained cleanup and stage/code
evidence while losing the safe protocol discriminator.

The repair admits only one unambiguous SQLSTATE from a tightly anchored verbose
psql error line. It releases no message, SQL, row or identifier; zero or
multiple matches release no SQLSTATE. The evidence schema admits only the exact
`^[0-9A-Z]{5}$` token, and hostile tests cover ambiguity and prose rejection.
No further run is eligible until this diagnostic candidate passes deterministic
checks and a fresh exact-HEAD independent veto.
