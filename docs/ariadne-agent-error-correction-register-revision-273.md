# Ariadne agent error and correction register — revision 273

Date: 2026-08-15

Timestamp: 2026-08-15T02:22:06+10:00 (Australia/Brisbane)

Revision 273 records AER-0312. The register now contains 312 bounded known
incidents, all corrected or contained by an explicit control.

AER-0312 records a recurrence of AER-0309. The bounded DeepSeek implementation
worker returned its decision object inside a Markdown code fence although the
frozen packet required exactly one JSON object and no prose. Its exact one-file
test commit exists, but neither the fenced decision nor the worker's narrative
is acceptance evidence.

The commit remains an untrusted candidate. Sol will inspect and integrate only
that exact Git object, repair its mismatched surface assumptions under explicit
orchestrator ownership, and independently reproduce the deterministic packet
before verifier dispatch. No runtime, product data, provider call or protected
ref was touched by this egress mismatch.
