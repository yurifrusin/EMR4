# Ariadne agent error and correction register — revision 197

Date: 2026-08-08

Revision 197 adds AER-0231 and brings the register to 231 bounded incidents.

## AER-0231 — base SQLSTATE omitted by telemetry scope guard

The first SQLSTATE-`23502` scope guard correctly removed coordinate drift from
other failure classes but did not restore their established base SQLSTATE
field. The same three envelope tests caught the omission. The corrected path
always records the safe SQLSTATE first and then conditionally adds allowlisted
not-null coordinates only for `23502`.
