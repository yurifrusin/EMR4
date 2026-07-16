# LC4V5 Sol Acceptance

Date: 2026-07-16

Decision: `valid_one_shot_certification_fail_accepted_and_sealed`

## Accepted evidence

- attempt: `lc4v5-fresh-attempt-001`
- source commit: `c2dd34b675bb378b0d4cbab1f41d05b5dd76e407`
- corpus hash: `d5828f9e0ff21cf1a2fb4d482c9556d579eca267e8e2027d09eba8388d52b3e9`
- manifest hash: `650510b52349cefe337aab385e478b26e16a4d87cdb7b13cfb9036d12c9a6d82`
- report hash: `17c123559a8c708fa0d122a2de1dbadc465e1d4e93a19814c5968f00f0b9c88b`
- consumed seal hash: `f3b8d31de29b04846273cdab4100d5776046fe988fda978518a7462a4f34d071`

All sixteen evidence gates pass, the report is aggregate-only, the population
is exact, evaluation exceptions are zero, and variance is zero. The product
threshold result is accepted without revision: complete 512/576 and safety
560/576 do not meet 548/576 and 576/576 respectively. Interpretation and safety
failure-layer limits also fail. The receipt correctly returns
`certification_fail`, not `evidence_invalid`.

Post-run validation loaded only the strict aggregate report, receipt, marker,
and consumed seal. It did not reopen any v5 case, utterance, expected value, or
failure selection. The ordinary post-run serial gate completed 123 tests.

V5 is permanently sealed. No rerun, regeneration, repair, case inspection, or
reuse is authorized. The next action is a user decision on the recommended
fresh development-only remediation tranche described in the closeout.
