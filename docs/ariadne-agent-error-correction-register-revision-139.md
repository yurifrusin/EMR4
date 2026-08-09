# Ariadne agent error and correction register revision 139

Date: 2026-08-09

Status: bounded register correction candidate

Revision 139 adds AER-0164 and brings the register to 164 bounded incidents
with zero open incidents.

## AER-0164 — unequal ordering in an exact JSON key-set comparison

Behavior attempt 026 failed safely at `BTR-E02` with `CF103` inside the
producer event-membership assertion. The renderer sorted the observed JSON
object keys but emitted the same fixed expected keys in declaration order.
Array equality therefore rejected an event whose key set was exact.

The deterministic diagnosis bound immutable failure evidence, the predecessor
artifact and immutable body program and required no additional PostgreSQL run.
Renderer 2.0.13 now canonicalizes only the expected order. It does not alter
the fixed key population or weaken exact missing/extra key rejection. Fresh
catalogue characterization, exact parse proof, behavior-parent rebind,
independent veto and behavior attempt 027 remain mandatory.
