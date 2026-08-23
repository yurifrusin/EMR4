# Threat-model delta: historical-derived scenario first-use candidate gate evaluator rehearsal

Date: 2026-08-24

Timestamp: 2026-08-24T09:52:28.8027597+10:00 (Australia/Brisbane)

Operation: `raisa-provider-free-historical-derived-scenario-first-use-candidate-gate-evaluator-rehearsal`

## Scope

This delta covers one pure typed evaluator and authored-synthetic rehearsal. It
does not cover a historical-derived candidate materialiser, archive access,
product integration, provider transmission or production use.

## Protected assets

- raw historical Diary files and ignored local measurement outputs;
- source identities, contacts, notes, text, filenames, paths and timestamps;
- local HMAC tokens, keys and mappings;
- exact first-use authority and its non-transitive candidate binding;
- product, patient, appointment, clinical and protected evidence;
- protected Git refs, deployment, release and Pages state; and
- user-owned untracked files, especially `docs/branding/`.

## Threats and controls

### A candidate is persisted before admission

Control: the evaluator accepts an already in-memory typed model, exposes no
writer and returns only a typed reading. This tranche writes no candidate. A
later materialiser remains separately planned and gated.

### Free-form text smuggles source content through the form

Control: candidate strings are closed literals except for regex-constrained
Git and digest values. The payload has no prose field. Pydantic strict mode and
`extra="forbid"` reject unknown keys, types and event values before evaluation.

### The caller chooses an arbitrary source commit

Control: the policy freezes one machine-resolved full 40-character accepted
source. Abbreviations and all other hashes are rejected.

### Digest ambiguity or declaration substitution

Control: digest input is canonical UTF-8 JSON with sorted keys and compact
separators. The evaluator recomputes both the digest and structural utility;
any mismatch is `blocked`.

### A broad replay is admitted through a benign purpose

Control: `whole_day_or_near_lossless_replay` is always blocked and
`bounded_multi_event_scenario` remains revision-required. The sole initially
admissible class is minimised and has explicit event, span, subject and resource
bounds.

### A synthetic test result is mistaken for real first use

Control: every rehearsal result is labelled
`authored_synthetic_gate_behavior_only`. The existing gate excludes wholly
authored-synthetic tests from first use. No historical-derived candidate exists
or is admitted in this tranche.

### Exact-artifact authority becomes class-wide or transitive

Control: the typed binding includes the exact source, digest, class, purpose
and local provider-free test ceiling and states `non_transitive=true`.
Provider, product, runtime, ordinary-practice, publication and reusable write
authority remain false.

### Structural uniqueness is treated as anonymity

Control: no anonymity or identity-reconstruction probability is claimed. The
prior nontrivial uniqueness diagnostics justify minimisation and the default
denial of broad replay; they do not become input data in this rehearsal.

### The evaluator reopens private or external access

Control: implementation and tests contain no archive/attempt path, network,
provider/model, database, route, client or product import. Source scans and the
full provider-free historical-Diary suite enforce the boundary.

## Residual risk and claim ceiling

A future actual candidate may reveal a new candidate-specific privacy or
utility problem even if this evaluator behaves correctly. That candidate must
be generated under a separate bounded plan, held in memory until this gate
decides, and may not be written without its exact receipt.

Passing this rehearsal proves only deterministic gate behavior on
authored-synthetic inputs. It opens no archive access, first-use admission,
artifact materialisation, product/provider/runtime use, ordinary-practice,
production, deployment, release, Pages, protected evidence or protected refs.
