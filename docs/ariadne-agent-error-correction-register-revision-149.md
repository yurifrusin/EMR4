# Ariadne agent error and correction register revision 149

Date: 2026-08-10

Status: corrected

Revision 149 adds AER-0174 and AER-0175 and brings the register to 175 bounded
incidents with zero open incidents.

## AER-0174 — exact pytest node name not verified

A manually selected node used `test_two_isolated_renders_are_byte_identical`
instead of the repository's exact `test_isolated_renders_are_byte_identical`.
Pytest failed closed before running tests. A scoped symbol search resolved the
exact node and the fresh invocation collected it. Future manual node selections
must first be resolved from the scoped source; otherwise the whole exact file
is preferred.

## AER-0175 — register seed count not reconciled

The AER-0173 edit updated aggregate pattern expectations but missed the
separate exact agent-behavior seed assertion. The focused packet failed only
that assertion. Revision 149 reconciles the seed and all aggregate counts to
the final population, and final acceptance requires the complete register test
file after every generated pattern-report update.
