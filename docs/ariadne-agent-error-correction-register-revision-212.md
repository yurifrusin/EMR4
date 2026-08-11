# Ariadne agent error and correction register — revision 212

Date: 2026-08-11

Revision 212 adds AER-0246 and AER-0247 and brings the register to 247 bounded
incidents.

## AER-0246 — PowerShell evidence-probe composition recurrence

While diagnosing the uncommitted register draft, one read-only probe repeated
the AER-0242 pipeline-expression error and a following probe failed to quote a
Git `HEAD:path` argument before passing its empty output to Python. Both failed
before producing evidence and changed no file, ref, process or worker state.
The corrected probe used named intermediate values and one literal command per
step. All remaining AES-C2 PowerShell diagnostics must follow that form.

## AER-0247 — underspecified register patch context

An underspecified repeated-key patch intended for AER-0244 matched AER-0003,
and the draft proposed cross-attempt links that the register contract reserves
for same-attempt peers. Exact-ID inspection caught both before validation,
report generation, commit or worker dispatch. AER-0003 is restored to its exact
committed empty linkage; AER-0244 and AER-0245 are also unlinked. Every further
register patch must include the exact target `incident_id` in the same hunk and
must be followed by target-and-sentinel inspection.
