# Ariadne agent error and correction register — revision 210

Date: 2026-08-11

Revision 210 adds AER-0244 and brings the register to 244 bounded incidents.

## AER-0244 — closed severity enum violated in the first AER-0243 draft

The first AER-0243 register draft used the natural-language severity value
`medium`, while the closed register schema permits only `low`, `moderate` or
`material`. Deterministic validation rejected the draft before the derived
pattern report, corrected register or any worker dispatch could be accepted.

The corrected fresh attempt uses the exact schema-valid value `moderate` for
AER-0243 and records this bounded authoring failure separately. The prevention
control is to read every closed enum directly from the register schema and
validate a new incident's literals before the repository-wide report and test
step.
