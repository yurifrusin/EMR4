# Ariadne agent-error and correction register — revision 571

Date: 2026-08-20

Timestamp: 2026-08-20T01:05:00+10:00 (Australia/Brisbane)

## Revision scope

Revision 571 preserves AER-0661. The second separate clockwork closeout check
passed the corrected transaction manifest, then rejected the command manifest
before publication because its Ruff command named the direct executable.
Clockwork admits only the exact Python executable with a `-m` module argument
vector.

The command now uses `.venv/Scripts/python.exe -m ruff`. The candidate and
canonical surfaces remained unchanged, and a fresh read-only check is required
before publish. The register now contains 661 incidents, all corrected or
contained and none open.

## Prevention

Clockwork command manifests must be rendered through the admitted executable
template. Tool commands remain Python-module invocations; direct executable
paths are rejected during intent authoring or the read-only check.
