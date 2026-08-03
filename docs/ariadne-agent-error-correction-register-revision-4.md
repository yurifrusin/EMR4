# Ariadne agent-error register revision 4

Date: 2026-08-03

Status: contained and escalated before acceptance

`AER-0011` records the fifth-pair native reviewer's unapproved environment
bootstrap. Before inspecting the candidate it invoked `uv run` with another
Python version. That command replaced the ignored repository `.venv`,
temporarily changed `uv.lock` and then failed because a dependency was absent.
The reviewer restored the tracked lockfile and stopped, but root independently
confirmed that the verification environment had lost its installed tools.

The candidate and tracked repository remained unchanged. Root rebuilt only the
exact repository `.venv` from `requirements.txt`, `requirements-dev.txt` and
the existing verification-tool versions before resuming any acceptance check.
The rejected review and its two valid candidate findings remain preserved.

Future reviewer packets must bind one already-installed interpreter, expressly
forbid package/environment bootstrap, and require stop-and-report when a
dependency is absent. Reviews run from disposable exact candidate worktrees and
must leave the candidate HEAD and status unchanged. The final independent veto
is escalated to the already allocated fresh Gemini 3.6 Flash/high Antigravity
lane after deterministic repair.

This row records an observed command-scope failure. It does not establish a
causal claim about a model, provider or reviewer class.
