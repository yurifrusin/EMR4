# Governance clockwork bound closeout entrypoint and explicit-stage manifest rehearsal — closeout

Date: 2026-08-23

Timestamp: 2026-08-23T21:18:20.9899474+10:00 (Australia/Brisbane)

Status: `accepted_pending_semantic_publication`

## Lay outcome

The clock can now take its own reading of the repository's Python installation
and exact Git identity, run the fixed safety sequence, and prepare the exact
list of files that are eligible for staging. It still cannot stage anything by
itself.

## Technical outcome

- the driver selects and attests `.venv/Scripts/python.exe` regardless of the
  caller's Python;
- full HEAD comes only from `git rev-parse --verify HEAD`;
- the verification-only tick executes all three semantic commands without
  publication;
- the five-file postpublication selection is fixed in code;
- committed publication results have a typed inline live-reading capture; and
- the stage manifest rejects unexpected tracked paths and excludes unrelated
  untracked paths.

## Accepted evidence

The clean-HEAD rehearsal passed from Windows' generic Python launcher. The
driver selected the repository interpreter, passed all three semantic commands,
125 semantic tests and 167 postpublication tests, changed no publication
surface and left the index empty. Its two-path manifest excluded 681 unrelated
untracked paths and `docs/branding/`.

One separately bounded live-adoption efficacy review is now the next gate. No
automatic staging, provider, worker, product/data, production runtime,
deployment, release, Pages or protected-ref surface opens.
