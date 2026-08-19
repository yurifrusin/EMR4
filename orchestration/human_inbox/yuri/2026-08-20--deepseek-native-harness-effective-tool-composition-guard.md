# DeepSeek native Harness effective-tool composition guard

Date: 2026-08-20

Timestamp: 2026-08-20T05:00:08.3025395+10:00 (Australia/Brisbane)

Yuri attention required: `no`

## Lay summary

The missing pre-flight gauge for the DeepSeek Harness now exists. Before a
future DeepSeek worker can send anything to the model, the generated guard
checks that the worker really inherited exactly the three intended tools and
that no tool was accidentally installed in the unfilterable local layer. If
anything is wrong, it stops with a specific safe label rather than the opaque
`CUSTOM_RUNNER_FAILURE` seen previously.

This tranche made no DeepSeek call and did not start the native Harness. An
independent Gemini review repeated all 73 tests and passed the exact clean
candidate. The next step is a single provider-free native boot to prove the
gauge works inside the real rc.7 Harness before we consider another occupied
DeepSeek worker.

## Technical summary

- Exact candidate: `51fe669f7925a9468e036bb242d6f7bcf2613dc9`
- Verifier acceptance source: `dc167c20f5b54b783a57fccb7843f434136c8ca8`
- Generated helper SHA-256:
  `6678ed31bdcd30a5018689b72ad509c182854bf5d63862f59b397acc8de40894`
- Four exact rc.7 package identities and seven source-semantic checks passed.
- Thirteen deterministic guard projections passed.
- Focused tests: 21/21; combined provider-free tests: 73/73.
- Gemini 3.7 Flash/high: `pass`, ten commands, zero P0-P2 findings, unchanged
  clean candidate.
- DeepSeek launches/provider calls, Node/native boots, agent sessions, broker
  requests, network, Docker and database counts: all zero.
- Clockwork: one check, one publish, zero canonical drift, zero bespoke updater
  executions; Pushover delivery request
  `1fe0fd83-8365-45e8-a345-515fb1b51399` succeeded.

The efficiency result is candidly mixed. The guard prevented all expensive or
external waste, but the local construction/command/assertion path caused more
reruns than desired. The clockwork itself met the one-check/one-publication
target without mechanical repair. One semantic intent-authoring defect remains:
the generated Current-result suffix states the future native boot in the
present tense. The active latch and Next implementation still require that
proof, and the next closeout will replace the premature sentence with measured
native evidence.

## Deliberately closed

No attempt 005, occupied DeepSeek worker, agent/model/provider request,
ordinary-practice enablement, generic-status `Arrived`, action grammar,
first-party client, waiting-area movement, product/API/configuration change,
product/patient/clinical data, production runtime, deployment, release, Pages
or protected-ref movement is opened.

## Place in the Raisa direction and next tranche

This connects another physical gear between Ariadne's WorkOrder/broker
clockwork and the DeepSeek Harness: the tool view and terminal coordinate now
have a deterministic reading before provider dispatch. The next tranche will
freeze and execute exactly one offline, network-denied provider-free native
composition boot. It must reach the accepted guard, emit its exact terminal,
exit cleanly and make zero agent, broker, model or provider requests. Yuri's
attention is not required.
