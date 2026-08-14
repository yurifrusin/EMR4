# Ariadne agent error and correction register — revision 274

Date: 2026-08-15

Timestamp: 2026-08-15T02:31:40+10:00 (Australia/Brisbane)

Revision 274 records AER-0313. The register now contains 313 bounded known
incidents, all corrected or contained by an explicit control.

AER-0313 records a low-severity orchestrator module-discovery error. Sol
guessed `scripts.ariadne_orchestrator`; that module does not exist, and Python
stopped before any receipt, source, Git or external action. A bounded
filename-only search then identified the actual module as
`scripts.ariadne_orchestrator_preflight`.

For this tranche, every repository module not already named in the frozen plan
must first be resolved from an exact existing scripts filename. Canonical
source, external state and all refs remained unchanged.
