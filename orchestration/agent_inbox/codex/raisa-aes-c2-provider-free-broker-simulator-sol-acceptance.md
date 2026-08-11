# Sol acceptance: Raisa AES-C2 provider-free inert broker simulator

Date: 2026-08-11

Decision: `accepted`

Result: `raisa_agent_execution_surface_containment_gate_aes_c2_provider_free_broker_simulator_pass`

Reviewed source HEAD: `d54f0476448f1218cd55477d42b958721359eae8`

## Basis

I accept AES-C2 as the exact provider-free in-process inert broker simulation
over the accepted AES-C0/C1 contract. The 26-scenario catalogue returns two
released simulations, four admission-driven non-dispatches and 20 terminal
stops. Exact fresh admission, immutable broker-owned identity, dispatch-time
current control state and exact cumulative budget commit are required before
the statically selected pure function can be called.

The pure function is actually called three times across the complete catalogue:
twice for released inert results and once for the deliberately malformed result,
which releases nothing. All 18 hostile attempt/result mutations and 14 hostile
contract mutations reject without release. The work cell receives no lease,
registry, credential fixture or operation selector, and the synthetic
noncredential fixture remains broker-private.

The final 95-test focused packet, 155-test maintained static packet and
161-test canonical fast profile pass. A fresh isolated Gemini 3.6 Flash/high
veto also passes 95 tests with the exact candidate HEAD unchanged and its
worktree clean. Evidence records zero real runtime, adapter, provider, network,
database/source, filesystem, executable/tool, command or product/patient
operation.

## Acceptance boundary

This acceptance admits deterministic authored-synthetic in-process simulation
evidence only. It grants no real runtime broker or work-cell process, real
adapter or credential, provider, product context, database/source, filesystem,
network, executable tool, command, deployment, production, release, Pages or
protected-ref authority.

AES-C3 hostile containment rehearsal is the next dependency-satisfied planned
descendant. It must freeze the narrowest provider-free attacks across local-
file, template/deserialization, metadata/credential probing, arbitrary or
encoded egress, cumulative probing, stale lease and cross-generation replay
surfaces before any occupied capability descendant.
