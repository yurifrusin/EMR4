# S4d D3 Fresh Recovery Packet

Own only:

- `tests/test_ariadne_deepcode_mailbox_settings.py`
- `orchestration/agent_inbox/codex/review-deepcode-s4d-d3-mailbox-settings.md`

Create focused, side-effect-free tests loading
`orchestration/harness_settings/deepcode_mailbox_profile.yaml` and reading
`orchestration/deepcode_pty/runner.mjs` as text where source-contract evidence
is required. Pin: local-only untrusted outbox; PTY event trust; cwd-wide write;
disposable containment; semantic-not-CLI scope; exact deny list; automated PTY
event; legacy notify hook not required; event emission requires valid artifact,
exit signal, completed turn, confirmed cleanup, and no permission prompt;
forced-cleanup receipt field; permission screen fails closed; and terminal
output is not persisted. Include meaningful negative assertions.

Do not edit `tests/test_ariadne_deepcode_pty.py` or any other file. Do not run
commands, commit, push, dispatch, or claim tests were executed. Then write the
artifact beginning `DECISION: pass` with an accurate files-read/files-edited
account and the three-part artifact/event/receipt completion contract.
