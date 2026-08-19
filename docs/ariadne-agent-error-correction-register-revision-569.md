# Ariadne agent-error and correction register — revision 569

Date: 2026-08-19

Timestamp: 2026-08-19T22:18:00+10:00 (Australia/Brisbane)

## Revision scope

Revision 569 preserves AER-0661. The first post-repair static-admission command
omitted the module's required `--check` selector and argparse rejected it before
harness admission began. No Docker object, provider call, repository mutation
or occupied rerun occurred.

The correction resolves the exact mutually exclusive CLI mode before launch
and permits only the static `--check` path after consumed attempt 001.

## Population

- incidents: 661;
- corrected or explicitly contained: 661;
- open: 0;
- latest id: `AER-0661`.

No product, ordinary-practice, provider, deployment, Pages or protected-ref
surface opened.
