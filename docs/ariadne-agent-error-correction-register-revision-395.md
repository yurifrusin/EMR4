# Ariadne agent error and correction register — revision 395

Date: 2026-08-18

Status: accepted containment

## Revision

Revision 395 adds AER-0454 from provider-free container hardening. The exact
rc.7 headless profile passed in the minimum disposable enclosure and reached
`MISSING_CREDENTIAL` under Docker network mode `none`. Three additional probes
then added a read-only container root filesystem. Each failed during local
plugin load because the disabled HMR entry was applied and required
`--expose-internals`. No credential, broker request, provider request, model
step, product access or candidate change existed.

Read-only rootfs was optional hardening, not part of the technical host or
credential-isolation boundary. It is not bypassed with a broader Node flag.
The admitted minimum keeps a disposable container rootfs, exposes only exact
host mounts, supplies no real provider credential, attaches the worker only to
the internal broker network and mounts no model-facing shell. The broker
sidecar separately owns the provider credential and shares no mount.

## Population

- incidents: 454;
- corrected or explicitly contained: 454;
- open: 0;
- latest id: `AER-0454`.
