# Ariadne agent error and correction register — revision 195

Date: 2026-08-08

Revision 195 adds two closed incidents and brings the register to 229 bounded
incidents.

## AER-0228 — assumed Docker executable location

An exact-ID absence check first assumed a system-wide Docker Desktop path. The
path was absent and Docker was never invoked. The corrected fresh command
resolved the known executable name locally and inspected only the exact
attempt-044 container ID, which returned `no such object`.

## AER-0229 — scenario not-null coordinate omitted

Attempt 044 safely persisted `BTR-I02` and SQLSTATE `23502`, but not the
affected relation or column. The bounded not-null parser existed only on the
bootstrap failure path. The correction reuses it behind an exact admission-
relation/column allowlist for unexpected scenario rejections; unlisted values
remain hidden and raw stderr remains digest-only.
