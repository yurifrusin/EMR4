# Claude Review - Sprint 200 Idempotency Continuity Index

Claude was dispatched for Sprint 200 with a compact review prompt but hit the
configured budget limit before producing a review artifact. The lane was treated
as unavailable and replaced with an additional DeepSeek review, following the
Ariadne plus three worker rule.

No Claude implementation changes were integrated.

Protocol note: this Sprint 200 Claude attempt did not follow the preferred
routine Claude protocol closely enough. Future Claude lanes should use the
standalone headless driver from Ariadne's shell with `--mint-session` for the
plan phase and a prompt that asks Claude to `handin`, submit a durable plan or
review packet, then stop. Poll/git and the submitted packet are the proof of
submission, not the CLI result JSON.
