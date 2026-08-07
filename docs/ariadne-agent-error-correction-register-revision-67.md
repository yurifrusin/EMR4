# Ariadne agent-error register revision 67

Date: 2026-08-07

Status: recurrent Python package-path invocation corrected

Revision 67 adds AER-0066. While inspecting the function/trigger-body schema
generator, Sol invoked the import-dependent module by filesystem path. Python
failed closed with `ModuleNotFoundError: No module named scripts` before any
generator action or repository write. This recurs the command-shape error
already recorded by AER-0058.

The failed invocation is preserved. The distinct correction imports the public
module API from the repository root and confirms `build_schema` is available.
Future import-dependent scripts use `python -m scripts.<module>` when a module
CLI exists, or a repository-root package import when no CLI exists.

No candidate, worker, SQL, DDL, database, source, provider, runtime,
product/patient data, deployment, Pages or protected ref changed. Revision 67
contains 66 bounded incidents; counts remain workflow-improvement signals only.
