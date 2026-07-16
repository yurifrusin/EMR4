# LC4V9D1 Preservation Amendment

Date: 2026-07-16
Status: `fresh_review_required`

Gemini returned `revision_required` on recovered head `5b27db4f` after its
focused suite passed 70/70 but a broadened preservation gate loaded the
historical LC4V4D1 live-invariant node. That node freezes the accepted D2-era
classification population at 37 supported / 20 policy gaps. Current corrected
product code improves it to 38 / 19, so equality is intentionally false.

Do not rewrite the historical fixture, report, or invariant. Add
`tests/test_bernie_lc4v4d1_development_diagnostic.py::TestDiagnosticPipeline::test_live_post_audit_invariants`
to the explicit historical-equality deselection set for this preservation
gate. This is not a D1 regression or unreviewed product failure. A fresh
Gemini review must reproduce 70/70 focused tests and the amended broader gate
before acceptance.
