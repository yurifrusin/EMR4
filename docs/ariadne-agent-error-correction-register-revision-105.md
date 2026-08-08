# Ariadne agent error and correction register revision 105

Date: 2026-08-08

Status: accepted register correction

Revision 105 adds AER-0127 and brings the register to 127 bounded incidents.

## AER-0127 - verifier repeated an obsolete artifact digest

The fresh full-projection review passed its exact candidate and prescribed
checks, and correctly named the recovered artifact digest in its attempt
evidence. A later sentence nevertheless repeated the obsolete predecessor
digest. Sol reconciliation found the internal contradiction after the
successful contained parse run.

The sentence is preserved but rejected as authoritative evidence. Parse
acceptance is bound to the canonical contract, schema-validated successful
runtime evidence and deterministic readback. The descendant behavior parent-
binding review must independently recompute every digest.
