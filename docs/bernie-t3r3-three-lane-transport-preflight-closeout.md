# Bernie T3R3 Three-Lane Transport Preflight Closeout

Date: 2026-07-18

Decision: `no_call_preflight_complete_material_transport_fork`

## Outcome

Yuri's DeepSeek amendment is complete. The frozen comparison now contains GPT,
Gemini, and DeepSeek lanes with a 144-sample maximum. T3R3 then carried all
three through a static, no-call transport, normalization, retention, and kill-
switch preflight.

No lane is execution-ready and no model prompt was sent. The T3 live gate
remains blocked.

## Transport result

| Lane | Local contract result | Remaining blockers |
|---|---|---|
| OpenAI `gpt-5.6-sol` through Codex subscription | isolated, read-only, ephemeral, schema-capable; not tool-free | no enforceable all-host-tools-off control, exact resolved revision unavailable, account data-control posture unverified |
| Google `Gemini 3.5 Flash (Medium)` through Antigravity subscription | non-interactive new project in plan/sandbox mode; not tool-free | no all-tools-off, structured-schema, no-session-persistence, or explicit no-fallback controls; Antigravity-specific retention mapping unresolved |
| DeepSeek `deepseek-v4-flash`/high through Claude Code `--bare` | tool-free, no local session persistence, schema-constrained, no fallback; adapter contract ready | exact resolved revision unavailable, mainland-China storage/security-log/cache posture not accepted, explicit run approval absent |

DeepSeek is the only lane with a mechanically tool-free local adapter contract.
That does not make it live-ready.

## Safety implementation

`app/services/ai/evals/bernie_shadow_transport_preflight.py` contains no
provider SDK, subprocess, HTTP, route, database, model, or audit import. It
defines static command templates only, a closed normalized-response schema, and
a kill switch bound to the current approval packet.

The blocked adapter validates the exact lane, frozen selected case, repeat
index, sample ceiling, prompt-character ceiling, and one-attempt rule, then
raises before any dispatch. Fake structured output can be normalized and hashed
without retaining raw provider text. The committed report regenerates exactly
at
`sha256:3f111b990e253c1471673222096cda063f60328b6b24c6f8f2981c43a7468c07`.

## API-spine classification

The API Steward review classifies this as a
`static_access_ai_evaluation_transport_preflight`. It adds no GraphQL or REST
route, Access AI runtime invocation, provider-executed tool, database/audit
write, appointment/confirmation authority, raw-response persistence, or
product wiring.

## Retention review

Official policy evidence is recorded in
`docs/bernie-t3r3-provider-retention-review.md`. The prompts would be synthetic
and non-PHI, but provider handling still matters:

- Codex consumer training/data controls are account-dependent and were not
  inspected;
- general Gemini controls do not establish Antigravity-specific retention; and
- DeepSeek documents mainland-China storage, minimum-necessary retention,
  security-log retention requirements, and default request-derived disk cache.

No provider-retention posture has been accepted for this run.

## Verification

- three-lane T3R2 packet: blocked, 24 cases, 144 samples maximum;
- T3R3 report: three lanes, one adapter-contract-ready, zero execution-ready,
  zero calls;
- focused T3R3/T3R2/live-gate/shadow-runner gate: 35/35;
- API-spine, handover/archive, and Pushover preservation gate: 39/39;
- report regeneration and `git diff --check`: passed;
- worker mix: Sol only; model transports were inspected through local help and
  metadata commands, not invoked; and
- protected evidence, historical/external data, product runtime, tools, and
  writes: none.

## Material fork

The next step is a Yuri decision between:

1. a strict model comparison using tool-free API transports for all three
   providers, requiring GPT/Gemini API credentials and separate API billing; or
2. a pragmatic agentic-surface comparison using the current GPT and Gemini
   subscriptions in empty sandboxes, explicitly labelled non-comparable to the
   tool-free DeepSeek lane and unable to make a clean pure-model claim.

DeepSeek's documented retention/data-residency posture also requires explicit
acceptance. Until those choices are made and the final packet is dated and
approved, the first external prompt remains blocked.
