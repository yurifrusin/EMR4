# C5 isolated-worktree interpreter binding repair

Date: 2026-08-06

## Finding

The fresh Gemini 3.6 Flash/high exact-HEAD veto correctly found that C5 derived
its Python path as `<source-root>/.venv/Scripts/python.exe`. A clean linked Git
worktree deliberately contains source only and therefore has no duplicate
virtual environment. Provider-free orchestration consequently failed before
the fake adapter ran, even though the test process was already executing under
the approved primary checkout interpreter.

This is a repository portability defect, not an authentication, provider,
operator or product-runtime failure. The veto remained read-only and opened no
C5 capability.

## Narrow repair

The controller now derives the child executable from the process-owned
`sys.executable` value, normalises it to an absolute path, hashes the exact file
before constructing the controller, rechecks that same active-interpreter
identity in the real process adapter, and rechecks its digest before every
launch. No caller may supply or override an executable path; the fixed
11-element argument vector, `-I`, `shell=False`, minimal credential-free child
environment and frozen source artifact remain unchanged.

This keeps the executable identity deterministic for the running controller
while allowing source to live in a clean linked worktree and the approved
interpreter to live in the primary checkout. It does not search `PATH`, inspect
another environment, or introduce a fallback.

Provider-free portable evidence represents the already validated interpreter
as `controller://active-python` and continues to represent the frozen target
as a repository-relative URI. It never persists an absolute checkout path.

## Separate test output

The veto log also contained a failing assertion from a differently named
`test_rehearsal_detects_tampered_rehearsal` task whose displayed exception text
already contained the asserted word `receipt`. That test does not exist in the
exact C5 candidate tree and is not evidence of a candidate source defect. The
material isolated-worktree failure above was reproduced directly at the exact
review HEAD and is repaired and regated independently.
