# Ariadne agent error and correction register — revision 396

Date: 2026-08-18

Status: accepted correction

## Revision

Revision 396 carries forward AER-0454 and adds AER-0455.

AER-0454 contains the provider-free rc.7 read-only-rootfs/HMR incompatibility
without weakening the admitted minimum enclosure: the worker container remains
disposable, receives only exact host mounts, has no real provider credential,
joins only the internal broker network and mounts no model-facing shell.

AER-0455 records that the orchestrator combined an incident-location readback
and JSON parse validation in one newline-separated PowerShell process. Both
operations were read-only and passed, but this violated the established
one-process-per-gate rule. Every remaining readback, validation, generation,
staging and commit gate now runs in a distinct process invocation with its own
captured exit.

## Population

- incidents: 455;
- corrected or explicitly contained: 455;
- open: 0;
- latest id: `AER-0455`.
