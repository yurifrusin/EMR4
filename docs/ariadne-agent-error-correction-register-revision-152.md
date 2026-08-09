# Ariadne agent error and correction register revision 152

Date: 2026-08-10

Status: corrected; database gate pending

Revision 152 adds AER-0178 and brings the register to 178 bounded incidents
with zero open incidents.

## AER-0178 — Windows shell and runtime preflight omitted

Five bounded read-only probes failed closed during the behavior parent rebind:
two Bash-style command chains were rejected by Windows PowerShell, the disabled
system Python alias was attempted before resolving the repository virtual
environment, one `rg` call received Windows-invalid wildcard path operands, and
one guessed receipt path did not exist. None changed candidate or evidence
bytes, invoked Docker, contacted a provider or opened protected evidence.

The intended checks were rerun with separate PowerShell-safe commands, exact
existing paths, real `rg` roots with `-g` filters, and
`.venv\\Scripts\\python.exe`. Those rules are now the explicit command
preflight for the rest of this tranche.
