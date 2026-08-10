# Ariadne agent error and correction register — revision 168

Date: 2026-08-10

Revision 168 adds corrected incident `AER-0194`. The disposable PostgreSQL parse
harness sent a deliberately non-accepting catalogue characterization to the
same output path as an immutable historical exact-rerun failure. The new
characterization was preserved immediately, the historical failure was
restored byte-exact, the accepted mutable pass was unchanged, and no second
database run was opened.

The correction assigns pass, characterization-required and other failures to
three distinct paths. Mutation-oriented tests prepopulate all targets and prove
that each result class can change only its own file. Exact reproduction remains
closed until this candidate passes deterministic and independent review.
