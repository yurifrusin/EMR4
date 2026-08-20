# Provider-free emr4-bounded-worker preset materialisation report

Date: 2026-08-20

Timestamp: 2026-08-20T10:30:02.1366272+10:00 (Australia/Brisbane)

Result: **pass**

## Exact materialisation

The exact rc.7-compatible payload is retained at
`orchestration/continuity/deepseek-native-harness-provider-free-emr4-bounded-worker-preset-materialisation-recovery/materialised-home/.agent-presets/emr4-bounded-worker/agent.cordis.yml` and is installation-ready only for future relative
destination `.agent-presets/emr4-bounded-worker/agent.cordis.yml`. It contains exactly the
official `tool-fs` and `tool-fs-search` rows, with
`sampleOverCapGlobResults: false`.

The preset's raw inherited surface is deliberately broader than its admitted
model-facing surface. Exact source provides unconditional `edit`, `glob`,
`grep`, `read`, `write` and conditional `read_image`. The already accepted
post-mount guard reduces both admitted inheritance cases to exactly sorted
`edit`, `glob`, `read`; the outer broker allowlist remains separately required.

## Bindings

- exact local-cache packages checked: @deepseek-ai/dsh-base, @deepseek-ai/dsh-headless, @deepseek-ai/dsh-agent-presets, @deepseek-ai/dsh-tools, @deepseek-ai/dsh-tool-fs, @deepseek-ai/dsh-tool-fs-search;
- payload bytes: 158;
- payload SHA-256: `3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1`;
- hostile preset/path variants rejected: 21;
- both consumed native attempts: exact and unchanged; and
- Node, native Harness, occupied worker, agent/session/turn, broker, model,
  provider, network, Docker and database counts: all zero.

## Claim ceiling

This result does not prove live discovery, mount, combined service activation,
scope creation, a native effective-schema view, another Harness boot, an
occupied DeepSeek worker or model/provider reliability. Any native successor
requires a separately frozen one-process plan and latch.
