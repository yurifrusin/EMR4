# Ariadne agent error and correction register — revision 221

Date: 2026-08-11

Revision 221 records AER-0256 and brings the register to 256 bounded known
incidents.

## AER-0256 — live worker outlived local shell wrapper

The local shell wrapper around the exact AES-C3 DeepSeek launch was configured
for 120 seconds and returned exit 124 before the external worker completed.
That was not a DeepSeek or Claude terminal result: exact process inspection
found the original launcher and `claude.exe` child still live with the
authorized packet, worktree and model arguments. At that moment there was no
receipt, commit or source edit.

Sol did not terminate or duplicate the worker. Bounded polling preserved the
single-worker invariant and observed the same process move from analysis into
the seven exact owned paths, commit candidate
`480a0301a1102108fa0779efb98809d55adf0ffa`, write a completed transport
receipt and exit. The worker worktree is clean and no protected ref moved.

The correction is operational: long external worker launchers must use a
wrapper that outlives the worker or yields asynchronously. A local wrapper
timeout is harness evidence, not a worker decision, while the exact authorized
process remains live. Candidate source is still subject to independent Sol and
Gemini review; this incident admits none of it.
