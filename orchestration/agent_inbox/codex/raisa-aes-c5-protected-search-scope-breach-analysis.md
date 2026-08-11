# AES-C5 protected-search scope-breach analysis

Date: 2026-08-11

Status: `contained_no_output_admitted_exact_allowlist_required`

## Observation

During initial repository-only inspection for the selected AES-C5 practitioner
directory source, Sol issued one recursive text query over broad `app`,
`docs/api-spine`, `tests` and `orchestration` roots. That scope was not an
approved exact-path allowlist. It traversed protected holdout fixture paths and
returned protected-path matches before the command was stopped by output and
exit limits.

The search output supplies no AES-C5 evidence and must not inform design,
implementation, tests, review or acceptance. This analysis deliberately does
not repeat any protected filename, label, case, value or matched content.

No product database, application route, provider, prompt, credential, network
adapter, command, write, deployment or protected Git ref was touched. The
repository worktree was unchanged by the search.

## Containment and correction

- abandon the entire broad-search result;
- register the event as a material orchestrator command-scope violation;
- permit all further AES-C5 inspection only through explicit files named by the
  route imports, the already accepted practitioner-directory artifacts or an
  exact single-file query;
- never search or list `tests/fixtures`, holdout-named paths, protected support
  modules, manifests, receipts or reports; and
- require the corrected AES-C5 candidate and reviewer packet to carry an exact
  source allowlist and to exclude protected paths explicitly.

This containment cannot undo the prohibited traversal. It prevents the output
from becoming evidence or shaping the candidate and narrows every corrected
inspection to named non-protected source files.
