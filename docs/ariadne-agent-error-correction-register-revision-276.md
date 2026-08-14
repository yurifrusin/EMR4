# Ariadne agent error and correction register — revision 276

Date: 2026-08-15

Timestamp: 2026-08-15T03:10:21+10:00 (Australia/Brisbane)

Revision 276 records AER-0315. The register now contains 315 bounded known
incidents, all corrected or contained by an explicit control.

AER-0315 records a low-severity static-tool routing error. Sol passed two
JavaScript sources to Ruff, which attempted to parse them as Python and failed
with syntax noise. The preceding API Spine test had passed, and the Ruff
command made no source or external change.

The corrected verification partitions tools by language: `node --check` for
JavaScript and Ruff only for Python paths. Mixed-language parser input is
forbidden for the remainder of this tranche.
