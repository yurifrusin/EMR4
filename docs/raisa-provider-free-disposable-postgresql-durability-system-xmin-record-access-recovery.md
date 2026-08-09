# Disposable PostgreSQL durability system-`xmin` record-access recovery

Date: 2026-08-09

Status: bounded typed-renderer recovery candidate; behavior remains closed

Attempt 021 used the independently reviewed renderer 2.0.8 artifact, admitted
all parents and fixtures, then stopped at `BTR-E01` with SQLSTATE `42703`, zero
admitted scenarios and verified exact-ID cleanup. One fresh diagnosis-only
container reproduced the exact safe coordinate
`emr4_context_fabric.cf_fence_stream_head_v1` line 33, record `final_head`,
column `xmin`, with raw diagnostics retained only in process memory and exact
cleanup verified.

The explicit `AS xmin` projection was necessary but not sufficient. The
renderer subsequently emitted `(final_head).xmin`. Parenthesised SQL composite
field selection requires PostgreSQL to identify a fixed composite descriptor,
but `final_head` is deliberately an anonymous PL/pgSQL `record` whose field
shape is established by the preceding exact read. The direct PL/pgSQL record
form is `final_head.xmin`.

Renderer 2.0.9 therefore makes `SYSTEM_XMIN` valid only for a typed `LOCAL`
record populated by an exact read that projects `xmin`, and emits direct
`record.xmin` access. The typed validator independently rejects non-local
`SYSTEM_XMIN`; the artifact recognizer rejects every residual `(record).xmin`
form; the existing explicit-projection and explicit-alias controls remain in
force. All relations, predicates, roles, triggers, scenarios and expected
outcomes remain unchanged.

The regenerated inert artifact must pass deterministic typed/renderer checks,
fresh exact parse/catalogue proof, unchanged behavior-parent rebinding and a
fresh independent veto before another behavior attempt.

The bounded implementation candidate passes 210 focused typed-body,
transaction-fence, renderer and agent-error-register tests plus Ruff, format,
regeneration and diff checks. It retains 412 statements and all 62 explicit
`AS xmin` projections, contains 118 total `.xmin` tokens with zero
parenthesised record access, and is exactly 1,403,578 LF bytes at SHA-256
`sha256:42e7230a98447201400129ecba06fbc5e0cb4fddff2aab263133c21f5635f112`.
The render-manifest raw/canonical SHA-256 is
`sha256:566edc7be1be850711920ca88e89a2d520faaa057da13a8ddee456a5e5f51b14`;
the body semantic and structural parent hashes remain unchanged.

This recovery grants no applied migration, application/API/Diary runtime,
patient, product or protected data, provider, watcher/listener, tool or command
authority, deployment, production, release, Pages or protected-ref movement.
