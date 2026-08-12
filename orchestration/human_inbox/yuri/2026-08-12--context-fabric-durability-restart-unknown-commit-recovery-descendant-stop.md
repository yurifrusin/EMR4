# CF-D2 recovery descendant — stopped, with workflow diagnosis next

Date: 2026-08-12

Attention required now: **no**

## Lay summary

CF-D2 still has not proved that the Context Fabric can classify an interrupted
database commit correctly after a restart. The safer preliminary test reached
the same anchor failure twice. We corrected one genuine revision mistake, but
the second run showed that this was not the whole explanation.

Nothing escaped containment: there was no simulated crash, restart, retry,
provider call, product or patient access, external network operation or
deployment. The disposable database container was removed and proven absent.
The planned full crash/restart attempt was not run.

This stop is useful evidence. It shows that we were investing in exact plans,
receipts and reviews while the diagnostic itself still grouped several
possible failures behind one indistinguishable result. In plain terms, we were
counting the angels very carefully before making sure the pin was visible.

## Technical summary

- Last accepted durability result remains CF-D1 at Continuity 243 / Compass
  225.
- Reviewed diagnostic source was
  `fe8313d224a92115aa31bea14f0cd3b14e4c9967`.
- Diagnostic attempt 002 passed ten setup preconditions and the position-one
  atomic delta, then failed at `cfd2_r01_append_anchor_2` with minimized
  `unexpected_terminal_success`.
- Evidence SHA-256 is
  `c595cd56b5b9a24dfdecc77fe12d998d1f16d593a33142cc3e9e9deffe7f1d12`.
- The earlier lifecycle-revision-two correction was necessary-looking but not
  sufficient; its sole-cause framing is rejected and recorded as AER-0284 at
  register revision 252.
- Attempt 003 is ineligible because no diagnostic passed. Key rotation and
  retention/purge remain dependency-blocked.

## Deliberately closed

No further CF-D2 runtime, operational database/source access, real or product
data, provider use, credentials/IAM change, executable tool or command,
reusable runtime, deployment, production, release, Pages or protected-ref
movement is opened. `docs/branding/` and every unrelated untracked file remain
excluded.

## Next tranche

The next work is the independent workflow-incident diagnosis you requested.
It will distinguish indispensable safety controls from duplicated ceremony,
identify why the diagnostic lacked useful discriminators, and implement a
bounded structural repair that makes evidence drive the next move sooner. It
will preserve hard authority, privacy, immutable-evidence and fail-closed
boundaries while restoring room for useful improvisation.
