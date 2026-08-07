# Ariadne agent-error register revision 82

Date: 2026-08-07

Status: two pre-implementation review-control incidents recorded

Revision 82 adds AER-0084 and AER-0085 from the inert durability DDL rehearsal
plan challenge. Neither attempt dispatched an implementation worker or changed
either immutable parent.

AER-0084 records that the first review predispatch state repeated the
unapproved `pre_dispatch` event label. Preflight stopped the attempt before
review, the failed receipt is preserved, and a distinct state using the
approved `pre_worker_dispatch` event passed before any verifier launch.

AER-0085 records that the subsequently completed verifier returned `pass` but
misstated both opcode populations and invented `42000`/`P0001` as registered
durability failure SQLSTATEs. Exact machine reconciliation found 22 declared/
21 observed instruction opcodes, 34 declared/34 observed expression opcodes and
the existing value-free `F_CARDINALITY`/`CF004` registry outcome. Because those
claims concern the security-critical lowering under challenge, the pass is not
admitted. Sol recovered the plan and requires one fresh exact-HEAD replacement
challenge.

Revision 82 contains 85 bounded incidents. AER-0084 is corrected. AER-0085 is
contained pending the replacement review; no implementation dispatch is
allowed from the rejected pass.
