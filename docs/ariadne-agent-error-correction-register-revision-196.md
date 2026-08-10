# Ariadne agent error and correction register — revision 196

Date: 2026-08-08

Revision 196 adds AER-0230 and brings the register to 230 bounded incidents.

## AER-0230 — not-null telemetry applied to other rejection classes

The first telemetry implementation added `coordinate_status: missing` to three
existing non-`23502` rejection envelopes. Focused tests caught the exact shape
drift before commit or runtime. The corrected helper calls the allowlisted
not-null parser only for SQLSTATE `23502`; all other failure envelopes remain
unchanged.
