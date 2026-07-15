# LC4V4D4 Sol Contract — Versioned Composed-Harness Integration

Date: 2026-07-16

Authority: GPT Sol owns architecture, acceptance, recovery, and protected
integration. One DeepSeek V4 Flash/high lane through Claude Code `--bare` may
implement the bounded candidate. A fresh Gemini 3.5 Flash Antigravity project
must independently veto the exact recovered head. DeepSeek Pro is not
authorized.

## Objective

Integrate the accepted LC4V4D3 Option A policy into the ordinary deterministic
composed development harness through an explicit policy-version selector. The
legacy path remains the default and must be byte-for-byte reproducible. Option
A must run after pure utterance extraction and before replay/scoring, carrying
its separate diary relation and resolved identities into versioned replay
evidence without changing utterance action, temporal, normalized, or entity
semantics.

Source baseline: `2ee30b8a90dd4128a4c533c51fcddbfba81a8bbb`.

Frozen evidence:

- D2 report hash:
  `sha256:3220ac943659ae1449c5c285144b1fa980f659668a705ca7aef98f0aea6d317a`;
- D3 selection hash:
  `sha256:d3c6618cb586f5dc43824ec7a6e9e33957fee587a45c19f89e5a4bb425006e2a`;
- accepted D3 report hash:
  `sha256:94b751aea657696329c6b6d394253aef3ef0dbe82316e7725efc1c16fac523a8`;
- legacy 60-probe composed baseline hash:
  `sha256:665851ffe055efb40f2ba1e43291d6b945c4764b4f441837781d4fc964d6ff27`.

The legacy baseline is the SHA-256 of canonical JSON for all 60 ordinary D1
probes in authored order, each row containing `scenario_id`,
`dataclasses.asdict(deterministic_interpret(spec))`, and
`dataclasses.asdict(deterministic_replay(spec, interpretation))`, serialized
with `sort_keys=True`, separators `(',', ':')`, and `ensure_ascii=False`.

## Required architecture

1. Add a public explicit version vocabulary with exactly a legacy value and an
   Option A value. The legacy value is the default.
2. Add one typed versioned composed result carrying:
   - policy version;
   - ordinary `InterpretationObservation`;
   - ordinary `ReplayObservation`;
   - separate diary relation and conflicting fields;
   - resolved patient, practitioner, and practitioner ID.
3. Add one ordinary composed runner accepting a `ReceptionScenarioSpec`, sample
   index, and explicit policy version.
4. The legacy branch delegates to the existing
   `deterministic_interpret`/`deterministic_replay` behavior without semantic or
   output changes. Do not silently make Option A the default.
5. The Option A branch performs `extract_semantics` once, passes only utterance
   text, that extraction, reference date, and synthetic initial diary state to
   `resolve_policy`, and then builds the typed interpretation/replay pair.
6. Option A interpretation preserves extraction values for intended action,
   action semantics, temporal relation, normalized values, entity semantics,
   completion claim, and negation. Only the operational policy fields
   (clarification, choices, selected tools, and authority) come from the policy
   result.
7. Option A replay uses the policy result for outcome, tools, clarification,
   deltas, and simulated-write marker. It must still calculate forbidden
   observations through the ordinary deterministic boundary.
8. Unsupported policy versions fail closed. Runtime policy code must not branch
   on scenario IDs, expected fields, scorer output, or protected evidence.

Do not change the frozen D3 resolver unless a directly demonstrated integration
defect makes a bounded Sol recovery amendment necessary. Do not change the
utterance parser or the generic composed scorer.

## Versioned scoring overlay

The D4 evidence layer may map the exact accepted 20 development IDs to an
explicit Option A expectation overlay. That ID mapping belongs only to the
evidence/scoring oracle, never to the composed runner or policy resolver.

The overlay must score complete typed observations, including:

- unchanged utterance semantic fields against the legacy extraction;
- clarification requirement and lossless choices;
- resolved identities;
- policy/replay tool sequence and authority;
- downstream outcome;
- separate diary relation and exact conflicting fields;
- appointment/audit deltas and simulated-write flag; and
- refusal/no-mutation safety.

For the one omitted-practitioner and five diary-state-join cases, the overlay
is authoritative for D4 scoring and must not force the incompatible frozen D1
expectations green. Other accepted D3 cases use their approved Option A
contract. Missing overlay members, duplicate members, wrong population/hash,
or partial observations must fail, not skip or auto-pass.

## Evidence and acceptance

Add a fail-closed D4 report that proves:

- exact D2 and D3 report hashes and exact D3 selection hash;
- the complete current 20-case population still matches the D3 selection;
- the 60-case legacy composed baseline hash remains exact;
- explicit legacy runner output equals direct legacy interpreter/replay output;
- all 20 Option A composed cases pass the versioned overlay twice;
- 40 complete Option A observations have zero variance;
- all pure utterance semantic fields equal the legacy observations;
- replay fields exactly equal the accepted policy output;
- the six incompatible D1 expectations are recorded as versioned overlay
  differences, not historical fixture repairs;
- no forbidden mutation occurs; and
- every gate controls the final decision and complete report hash.

Acceptance requires 20/20 Option A composed passes, 40 complete observations,
zero variance, exact category counts `5/2/1/2/5/5`, exact legacy baseline,
unchanged D1/D2/D3 artifacts, focused and adjacent serial tests, `git diff
--check`, and a fresh Gemini `DECISION: pass` on the exact recovered report
head.

## Owned paths

- narrow additive integration in
  `app/services/bernie/composed_corpus_evaluator.py`;
- new `app/services/bernie/lc4v4d4_composed_evidence.py`;
- new `tests/test_bernie_lc4v4d4_composed_integration.py`;
- new `docs/bernie-lc4v4d4-composed-integration.json` and `.md`;
- one durable worker receipt under `orchestration/agent_inbox/claude/`.

The worker must not edit `AGENTS.md`, existing D1/D2/D3 source, fixtures,
reports, tests, acceptances, protected evidence, providers, routes, databases,
UI, historical diary, deployment, release, or write surfaces. It may read only
the exact ordinary files named in its packet. Broad repository or `tests`
searches are prohibited.

## Closed gates

Holdouts v1-v4 remain sealed and unavailable. T3.1-T3.4 remain intact and
blocked; T3.5, live providers, product/runtime wiring, API/UI/database changes,
historical diary access, deployment, release, and write authority remain
deferred. D4 is development-only and is not a new certification run.
