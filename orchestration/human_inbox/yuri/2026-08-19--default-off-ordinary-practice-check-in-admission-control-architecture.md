# Default-off ordinary-practice check-in admission-control architecture

Date: 2026-08-19

Timestamp: 2026-08-19T03:24:22.2795586+10:00 (Australia/Brisbane)

## Lay summary

We now have a precise design for how a practice could eventually be admitted
to ordinary check-in without confusing that permission with the existing
synthetic testing allowlist. Nothing has been switched on.

The design makes stopping safer than starting. A stopped or withdrawn admission
cannot quietly resume, rollback can only disable, and the global kill switch
overrides both lanes. Re-enabling in the future would require a wholly new,
fully evidenced generation.

The design passed an independent Gemini review and 390 deliberately hostile
contract changes were all rejected. The next step is only an unmounted kernel
rehearsal with zero active practices.

The clockwork idea also gained a concrete shape: Ariadne and the DeepSeek
broker can share a digest-bound sequence number, so each can advance only from
the other's exact recorded state. That remains a shadow workflow design and
does not control the product.

## Technical summary

- reviewed source: `752b521c59f5b44bf46de0cf776a33ac74b8134d`;
- admission record: 4 states, 6 allowed transitions, no resume;
- future unmounted commands: 5, all `authorized_now: false`;
- required operational evidence: 3 gates retained;
- observability: 5 non-PHI metric families, 6 non-actuating critical alerts;
- source bindings: 11/11 exact;
- hostile mutations: 390 rejected, zero escapes;
- focused tests: 20 passed;
- Gemini: 9/9 bounded commands, no P0-P2 finding;
- error register: revision 512, 591 corrected/contained, none open;
- protected refs remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`;
- non-PHI Pushover delivered as request
  `71b837b5-fb9a-482f-be7e-0d5056d5777e`;
- no application/configuration source or practice posture changed.

Next:
`raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal`.
