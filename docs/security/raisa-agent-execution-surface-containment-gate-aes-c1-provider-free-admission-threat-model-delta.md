# Threat-model delta: Raisa AES-C1 provider-free admission rehearsal

Date: 2026-08-11

Status: frozen authored-synthetic, provider-free and unmounted boundary

## Security delta

AES-C1 exercises the first deterministic decision over AES-C0 message objects.
It does not mount a broker or adapter. The security objective is that an
attacker-controlled but schema-shaped candidate cannot manufacture authority by
mixing a valid manifest, grant, lease, generation, authority snapshot, budget or
revocation record from different scopes or times.

## Assets and data

- immutable generation and manifest identity;
- principal/purpose, Bureau, work-cell and audience authority bindings;
- exact grant and broker-side lease scope;
- independent cumulative reasoning, information, egress, action, denial and
  time budgets;
- external revocation, supersession and kill-switch state;
- supply-chain and evidence digests; and
- authored-synthetic values only, with no patient, clinical or product data.

## Trust boundaries

1. frozen AES-C0 artifacts to the pure evaluator;
2. authored-synthetic current-generation/current-authority state to the
   evaluator;
3. untrusted candidate and proofreader result to the evaluator;
4. evaluator to closed `BrokerDecision` and minimized
   `AuditEvidenceEnvelope`; and
5. deterministic result to test evidence only, never an adapter.

## Attacker-controlled inputs

- candidate fields and values;
- requested capability and typed arguments;
- forged or stale message objects in hostile scenarios;
- over-budget prospective observations;
- cross-generation, cross-Bureau and cross-authority replay; and
- malformed additional, missing or wrong-type fields.

The current-generation state, current-authority state, evaluation clock and
external kill-switch observation are model-independent authored-synthetic
control inputs in this rehearsal. Their real runtime provenance is not proven.

## Dangerous capabilities

No dangerous capability is opened. Provider inference, authoritative reads and
the inert tool-adapter class are identifiers only. The evaluator cannot call a
provider, adapter, network, filesystem, database, source, process, tool or
command and cannot receive a credential.

## Abuse cases and required controls

| Abuse case | Control | Required evidence |
|---|---|---|
| Mix a lease from another generation with a valid grant | exact manifest/generation/digest intersection | cross-generation replay stops |
| Reuse authority after role/purpose/Bureau/work-cell change | fresh current-authority equality before grant admission | each authority-change scenario stops |
| Alter manifest content while retaining a plausible digest string | recompute canonical sentinel-normalized manifest digest | content-digest mutation stops |
| Smuggle adapter/destination/method/URL through candidate content | closed candidate keys and broker-observed operation identity | candidate-identity scenario denies |
| Use a broader source or field than the grant | exact set-subset and source-class checks | source/input/output overreach denies |
| Hide execution in a nominally allowed capability | no dispatch function and no adapter/runtime imports | static boundary checks pass |
| Split usage across counters or channels | prospective cumulative check over every AES-C0 dimension | dimension and overflow scenarios stop |
| Treat zero as free authority | requested counter above a zero ceiling stops while unrelated zero counters do not pre-exhaust | zero-disabled scenario stops |
| Probe repeatedly after denials | denial counters update and reached positive ceiling blocks the following attempt | paired denial-ceiling scenarios pass |
| Race revocation or supersession behind a valid grant | terminal control state precedes grant/lease checks | revocation/supersession outrank allow |
| Leak prompt, reasoning, exception or sensitive values into evidence | closed AES-C0 evidence allowlist plus recursive forbidden-key check | evidence mutations reject |
| Turn an allow into command authority | AES-C0 command fields remain false and no command path exists | focused API Spine tests pass |

## Verification evidence

- frozen AES-C0 input digests and full AES-C0 regression;
- exact 45-scenario decision/reason registry;
- generated malformed/hostile mutations with zero admission;
- independent digest and prospective-budget assertions;
- static import/I/O boundary checks;
- focused API Spine compatibility tests;
- DeepSeek blue defensive implementation/test evidence; and
- fresh exact-head Gemini red/veto review after deterministic gates.

## Residual risk owner

GPT Sol owns acceptance of this unmounted rehearsal. Later runtime risks remain
owned by their separate AES-C2 through AES-C5 gates: authoritative control-state
provenance, atomicity, time-of-check/time-of-use, broker/adapter defects,
credential custody, container/kernel escape, provider behavior and operations.

## Stop boundary

Any admitted mismatched record, candidate-controlled operation identity,
unaccounted budget dimension, stale/revoked authority allow, unminimized
evidence, external-effect code, provider/data access or unresolved critical/high
review finding returns `revision_required`. This delta grants no runtime,
adapter, provider, data, credential, tool, command, deployment, release, Pages
or protected-ref authority.
