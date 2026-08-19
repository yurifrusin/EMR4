# DeepSeek native-Harness worker attempt 001 diagnosis

Date: 2026-08-20

Status: `consumed_failed_closed`

## Terminal facts

- The only occupied launch was bound to full source
  `b91733b11cbe28d0d22ae4d46308bdc706ea2897` and official
  `@deepseek-ai/dsh@0.1.0-rc.7`.
- The broker became ready, but no provider call started, completed or failed.
- No model step, request, tool call or file change occurred.
- The Harness exited `1` with runner coordinate `CUSTOM_RUNNER_FAILURE`.
- The broker and Harness processes were absent after cleanup; the disposable
  Harness home, raw logs and raw session were removed; and the provider key was
  absent from the worker environment.
- Automatic retries were zero. Resume and retry remain prohibited.

The sanitized terminal record has repository SHA-256
`b5e428236c4a251f77d8c37e80d1c5288fc673f23bca66de577cddfaf1ba543e`.

## Machine-grounded composition diagnosis

The custom runner mounted the `emr4-bounded-worker` preset and then called
`agentCtx.tools.restrict({ allow: ["edit", "glob", "read"] })`. The preset
registered filesystem tools in the agent scope, while the rc.7 tool runtime
defines `restrict()` as a filter over inherited global tools and rejects
unknown or scope-local names. The pinned runtime source at
`node_modules/@deepseek-ai/dsh-tools/lib/types/index.js` has SHA-256
`4f5094252285c11ca2fd7f3ab642023fa780d6f49ce2acc359a0c628e5d88b61`
and raises when an allow name is absent from `restrictableNames`.

This explains the pre-request failure: the controller attempted to restrict
scope-local preset tools as though they were global inherited tools. It is an
orchestrator/Harness profile-composition defect, not a DeepSeek provider,
reasoning or implementation failure.

## Traceability finding and successor guard

The controller's terminal sanitizer retained only `error.code` or the generic
fallback `CUSTOM_RUNNER_FAILURE`. Because the thrown composition error had no
stable code, the exact safe exception class/coordinate was lost even though the
session correctly failed closed. Before any later occupied DeepSeek worker:

1. a provider-free composition guard must assemble the exact preset and prove
   the effective tool set contains only `read`, `glob` and `edit`;
2. the guard must distinguish inherited global names from scope-local preset
   registrations and must not call `restrict()` with a scope-local name;
3. the custom runner must emit a bounded stable pre-provider composition
   coordinate without retaining stack traces, prompts, payloads or secrets;
4. the broker must remain at zero provider calls during that guard; and
5. a fresh one-run WorkOrder and latch are required for any later occupied
   launch.

No conclusion about DeepSeek model quality can be drawn from this attempt,
because the model was never invoked.
