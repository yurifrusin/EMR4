# Provider-free unclassified pre-HMR structured diagnostic seam report

- Result: `pass`
- Installed Harness: `@deepseek-ai/dsh 0.1.0-rc.7`
- Installed source files bound: `6`
- Hostile fixtures passed: `11`
- Wrapper SHA-256: `39e4b5aa9b5dc3d8950f1a3b9a031a2a8f5f764fa92eb228efe43087199d3ce3`
- Historical fallback: `ariadne.native_harness_pre_hmr_startup_terminal.v1`
- Structured terminal: `ariadne.native_harness_pre_hmr_startup_terminal.v2`
- Node / Harness / broker / worker / model / provider activity: `0 / 0 / 0 / 0 / 0 / 0`
- Raw attempt-stream reads: `0`

The accepted seam catches only a future rejected import of the pinned native
Harness entrypoint. It projects a bounded typed cause chain, writes once, and
rethrows the identical value. The controller validates and embeds that safe
projection before destroying the disposable root. Absent or invalid structured
evidence falls back to the accepted v1 terminal.

Attempt 003 is unchanged and remains `unclassified_nonzero_exit`. This result
does not run DeepSeek, make the native Harness operationally ready or authorise
another occupied attempt.
