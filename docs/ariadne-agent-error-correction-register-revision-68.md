# Ariadne agent-error register revision 68

Date: 2026-08-07

Status: recurrent Python package-path invocation corrected

Revision 68 adds AER-0067. After AER-0066 had already restated the package
invocation control, Sol invoked the function/trigger-body artifact builder by
filesystem path. Its in-memory contract validation completed, but the write
path imports the schema through the `scripts` package. Python failed closed at
that import before either generated artifact was opened or written.

The failed invocation is preserved. The distinct correction invoked the same
builder as a repository-root package module. It completed successfully and
generated the validated contract and structural schema. Because this is the
third occurrence of the same command-shape error, the tranche-level control is
tightened: files under `scripts` use package-module invocation unless a
recorded preflight proves that every execution path is package-independent.

No worker, SQL, DDL, database, source, provider, runtime, product/patient data,
deployment, Pages or protected ref changed. Revision 68 contains 67 bounded
incidents; counts remain workflow-improvement signals only.
