# Provider-free required-service injection recovery report

Date: 2026-08-20

Timestamp: 2026-08-20T09:14:31.1452892+10:00 (Australia/Brisbane)

Result: **pass**

## Exact reading

The exact rc.7 `base` + `headless` composition contains the host `tools`
provider but no `agent-presets` provider. The consumed runner and loader row
declared only `hmr`, so Cordis had no dependency gate for `agentPresets` or
`tools`. The retained `SERVICES_UNAVAILABLE` result is therefore explained by
`headless_agent_presets_row_absent_and_runner_dependencies_underdeclared` without rerunning Harness.

The exact future declarations add the official rc.7 `agent-presets` host row
with `default: standard` and require `hmr`, `agentPresets`, `tools` in both the
loader row and module export. Cordis and loader source prove that these names
are merged into the plugin fiber and that activation waits while any declared
provider is absent.

## Bindings

- packages checked: @deepseek-ai/dsh, @deepseek-ai/dsh-base, @deepseek-ai/dsh-headless, @deepseek-ai/dsh-web-app, @deepseek-ai/dsh-agent-presets, @deepseek-ai/dsh-tools, @deepseek-ai/cordis, @deepseek-ai/cordis-plugin-loader;
- future patch SHA-256: `9d92d468b03ff7f7ebb7788ef0e56a03948973d47cc411350a4ca861143973b3`;
- future runner SHA-256: `d199c9aa8361a30a2f3f7de3a228ab93d962904dd2e9291c3d1c30666ca72367`;
- both consumed native attempts: exact and unchanged; and
- Node, native Harness, occupied worker, agent/session/turn, broker, model,
  provider, network, Docker and database counts: all zero.

## Claim ceiling

`emr4-bounded-worker` is not one of the shipped rc.7 presets. This result does
not materialise it or prove preset mount, scope creation, the effective
`edit`, `glob`, `read` view, a native boot, an occupied worker, or model/provider
reliability. A separate provider-free preset-materialisation recovery must pass
before any future native process can be considered.
