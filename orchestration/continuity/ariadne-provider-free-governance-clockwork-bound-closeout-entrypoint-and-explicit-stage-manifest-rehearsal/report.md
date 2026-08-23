# Governance clockwork bound closeout entrypoint rehearsal

Date: 2026-08-23

Timestamp: 2026-08-23T21:18:20.9899474+10:00 (Australia/Brisbane)

Result: `accepted_pending_semantic_publication`

## Conclusion

The driver now makes four formerly manual choices deterministic: it locates and
attests the repository interpreter, resolves the full Git HEAD, owns the exact
postpublication test selection and derives stage candidates from the admitted
intent plus Git state.

The stage output is deliberately inert JSON. It cannot call `git add`, mutate
the index or include an unexpected tracked path. Unrelated untracked paths are
counted and excluded, with `docs/branding/` separately forbidden.

## Safety retained

The existing three semantic command rows remain the prepublication gate. The
existing five-file postpublication selection remains a closed constant and
runs after the tick result. The verification-only rehearsal mode must report
zero publication and leave every canonical and clockwork metadata byte
unchanged.

## Occupied result

The clean-HEAD rehearsal was deliberately launched from Windows' generic
Python shim. The driver selected and exactly attested the repository virtual
environment, then passed all three semantic commands, 125 semantic governance
tests and all 167 postpublication tests.

No live publication occurred. Twelve unique canonical/metadata paths remained
byte-identical, the index remained empty and the stage manifest contained only
its two fixed generated outputs. It rejected no tracked path, excluded 681
unrelated untracked paths and included no `docs/branding/` path.

## Decision

Accept the nonpublishing rehearsal. A separate narrow live-adoption efficacy
review may exercise one exact live tick through the driver; automatic staging
and test reduction remain closed.
