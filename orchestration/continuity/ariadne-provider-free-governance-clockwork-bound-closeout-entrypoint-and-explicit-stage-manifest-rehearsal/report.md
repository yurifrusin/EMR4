# Governance clockwork bound closeout entrypoint rehearsal

Date: 2026-08-23

Timestamp: 2026-08-23T21:18:20.9899474+10:00 (Australia/Brisbane)

Result: `candidate_pending_occupied_rehearsal`

## Provisional conclusion

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

## Evidence still required

One clean-HEAD occupied rehearsal must execute both verification phases, prove
the repository interpreter attestation, show zero canonical and index changes,
and emit a stage manifest that agrees with Git status. Live use remains closed
until that evidence is accepted.
