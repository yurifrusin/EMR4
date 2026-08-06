# Ariadne agent-error register revision 54

Date: 2026-08-06

Status: sixth migration/transaction architecture recovery active

## AER-0053 is contained

The fresh native reviewer for candidate
`eda1039b959321ea1e602a6db5b35caf2cc85cb7` ran one out-of-packet broad
`git diff --name-only master...HEAD` readback. It enumerated forbidden prior-
review and agent-error-register path names but opened none of their contents,
made no file change, contacted no external surface and immediately self-
reported the breach. Sol independently verified the exact review worktree
remained clean and every protected ref remained unchanged.

The review is rejected for acceptance. Its four architecture findings are
retained only as untrusted diagnostic challenges. A genuinely fresh successor
must inspect exact file paths only; it receives no Git discovery command, and
orchestrator-owned exact preflight/postflight supplies ref and cleanliness
evidence.

## AER-0051 remains open

The untrusted diagnostic identified four additional requirements before a
fresh veto can be admitted:

1. freeze an exact PostgreSQL-version-specific `xid`/`xid8` comparison and an
   explicit no-subtransaction producer rule;
2. bind temporal-update eligibility to a database-derived command obligation
   so no-event and insert/delete paths fail while non-temporal updates remain
   legal;
3. expand the machine contract from relation names into exact columns, keys,
   delete actions, roles, entry points, RLS, trigger surfaces, admission,
   lifecycle, anchor, key and retention constraints; and
4. expand source parsing and adversarial mutations over those exact surfaces.

The sixth recovery remains architecture-only. No DDL, migration, database,
runtime, provider, product-data, command, deployment or protected authority is
opened.

Revision 54 contains 53 bounded incidents: 41 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
AER-0051 remains open and AER-0053 is contained pending a clean successor veto.
Counts remain workflow-improvement signals and do not establish model,
provider, transport or role causation.
