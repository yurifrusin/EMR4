# Ariadne agent error and correction register — revision 229

Date: 2026-08-11

Revision 229 adds AER-0264. The register now contains 264 bounded known
incidents.

## AER-0264 — expired generic readiness check required as a passing AES-C5 gate

The first frozen AES-C5 plan explicitly recorded that the 2026-07
practitioner-directory general readiness approval expired on 2026-08-08, but
its deterministic gate list nevertheless required the legacy static readiness
checks as though they must pass. The exact check failed closed with
`route readiness approval has expired` before any product source or provider
operation.

Sol preserved the failure, did not renew or modify the old approval/fixture and
corrected the AES-C5 plan. The legacy checks must continue to produce the expiry
disposition; any pass or global readiness change is now a stop. The newer Yuri
selection supplies authority only for the exact one-run AES-C5 route/purpose
envelope, backed by fresh route/auth/tenancy/minimization tests. No product read,
database rehearsal, credential/cloud operation or provider call occurred.
