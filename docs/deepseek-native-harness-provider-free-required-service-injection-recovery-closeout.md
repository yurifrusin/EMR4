# DeepSeek native Harness provider-free required-service injection recovery closeout

Date: 2026-08-20

Timestamp: 2026-08-20T09:54:56.7001117+10:00 (Australia/Brisbane)

Status: `accepted`

Exact reviewed candidate:
`056c59d14de4efc302898e84ec7a69cbf729dfce`

The accepted result explains the immutable `SERVICES_UNAVAILABLE` native boot
without rerunning it. Exact rc.7 cache evidence shows that the headless roster
keeps the base `tools` row but supplies no `agent-presets` row, while the
accepted loader entry and runner declared only `hmr`. Cordis merges entry
injection into the fiber and holds activation only for services that are
actually declared. The future composition must therefore add the official
`@deepseek-ai/dsh-agent-presets` row with `default: standard` and declare the
ordered services `hmr`, `agentPresets`, `tools` in both the entry and runner.

The first Gemini review returned `revision_required` for two real verification
defects. The candidate was repaired so its cache locator survives the exact
provider-free environment while failing closed without an owned cache, and the
isolated verifier manifest now omits only one non-transferable predecessor
assertion while the current suite directly binds both immutable failed
attempts. The corrected candidate passes 15 focused tests and 86 exact
provider-free neighboring tests.

The first corrected Gemini project executed all ten commands with exit code
zero and produced a substantive pass review, but its final machine envelope
mistranscribed C10 by inserting `diff`. The broker correctly admitted no
verdict. One fresh project repeated the complete review and returned an exact,
schema-admissible `pass`: ten commands, 86 tests, unchanged HEAD and clean
worktree.

`emr4-bounded-worker` is not a shipped rc.7 preset and remains unmaterialised.
This acceptance authorises no native Harness process, Node process, worker,
agent session, turn, broker, DeepSeek model or provider request. It changes no
product, API, client, feature flag, allowlist, grammar, ordinary-practice,
waiting-area, data, runtime, deployment, release, Pages or protected ref.

The next eligible tranche is a separate provider-free deterministic recovery
that materialises and proves the exact `emr4-bounded-worker` preset mapping to
the edit/glob/read tool boundary. It has no native-process or model/provider
authority.
