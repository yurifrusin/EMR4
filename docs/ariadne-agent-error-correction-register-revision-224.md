# Ariadne agent error and correction register — revision 224

Date: 2026-08-11

Revision 224 closes the already-recorded AER-0257 correction without adding a
new incident. The register remains at 258 bounded known incidents.

## AER-0257 — recovered AES-C3 evidence integrity

DeepSeek candidate `480a0301a1102108fa0779efb98809d55adf0ffa` and its
non-transferable self-pass remain rejected. Sol adopted only its seven source
paths as an untrusted candidate under the explicit recovery lease, then bound
every scenario to its declared inherited base and expected transition, added
exact lease/alias/token current-authority bindings, made malformed public
inputs return a closed rejection, required exact inner C1/C2 result evidence,
retained contradictory actual call counts while withholding their digests,
and verified every cumulative transition through the terminal third stop.

Recovered commit `c45ff191af420b801e9917a7efc69c17aeb5698b` passes the
complete deterministic packets and one fresh Gemini 3.6 Flash/high exact-HEAD
veto. That review ran 120 focused AES-C3/C2/C1/C0/plan/API/source-state tests,
Ruff and Git whitespace, then left the bound worktree clean at the same HEAD.
AER-0257 is therefore `corrected` by `recovery_lease_applied`; the immutable
worker failure evidence remains preserved.
