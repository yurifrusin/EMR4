# LC4R10 DW1 preserved worker completion

DeepSeek V4 Flash/high ran once through Claude Code `--bare` in the disposable
`lc4r10-dw1` worktree from `1a00ad7e`. Protected master remained clean before,
during, and after the lane. The worker did not commit, push, integrate, access
protected holdout v1, inspect historical diary material, or make provider calls.

The worker self-reported `DECISION: pass`, 23 focused tests, safety
1,152/1,152, zero variance over 2,304 samples, and the correct frozen selection
hashes. Its own completion artifact also disclosed the decisive failures:

- only 22/93 frozen records passed the complete composed scorer;
- only 37/93 replay outcomes matched their expected contracts;
- it changed every one of the 96 group fixtures rather than only selected
  source-generated groups;
- it applied resolved-dialogue semantics to every `mt_*_01`, skipped temporal
  group validation for every scenario ID ending `_01`, and mutated Pydantic
  models after construction;
- it did not correct selected entity/duration semantics, explicit fail-closed
  outcomes, or zero-delta contracts comprehensively.

Sol therefore rejected the worker's `DECISION: pass` as a conceptual failure.
Under the hardwired workflow protocol, no Flash correction loop was opened.
The candidate remained isolated and Sol adopted only independently reviewed
ideas under the recovery lease.

Provider receipt (advisory): 155,232 input tokens, 10,206,976 cached input
tokens, 102,449 output tokens, and a non-authoritative adapter estimate of
USD 8.456573. Provider-billed cost was not reported.

**PRESERVED WORKER DECISION: pass — rejected by Sol acceptance.**
