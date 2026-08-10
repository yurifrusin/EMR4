# Ariadne agent error and correction register — revision 176

Date: 2026-08-10

Revision 176 records AER-0204 and raises the bounded incident population to
204. Sol directly invoked the package-dependent typed-body builder script even
though this exact command pattern was already registered. It failed before any
repository write because the `scripts` package was unavailable from the direct
script path.

The corrected fresh invocation used `python -m` from the repository root,
returned the exact resealed body digest `sha256:b54b2e6800...`, and the focused
body tests passed. The failed invocation changed no candidate artifact. No
incident remains open.
