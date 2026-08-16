# Ariadne agent error and correction register — revision 314

Date: 2026-08-16

Timestamp: 2026-08-16T22:41:52.8064255+10:00 (Australia/Brisbane)

## Result

Revision 314 preserves 363 bounded known incidents. AER-0363 is corrected; no
incident is open or contained.

AER-0363 records the third occurrence of a short Git prefix being expanded
into a nonexistent full object ID in continuation evidence. The value existed
only in an uncommitted pre-push runtime state. Direct `git rev-parse HEAD`
exposed it before receipt generation, staging or publication; the accepted
product candidate and protected refs were unchanged.

The orchestrator preflight now extracts every full 40-character object ID from
the `git_refs_and_worktree` source and resolves each one as a commit in the
local repository. An unresolvable ID returns `revision_required` and forbids
dispatch or publication. The focused hostile test proves the erroneous value
fails closed, while existing five-source fixtures preserve valid admission.

The final tranche profile passes 523 provider-free tests. The independently
reviewed product candidate remains exact
`43e993a98ffec3f9ffe2740b0b38816bcb2d6adb`.

## Boundary

This is a locally observed orchestrator evidence error and harness correction,
not a model, provider or product-quality claim. It opened no route, database,
capability, product data, provider, network, deployment, Pages or protected
ref.
