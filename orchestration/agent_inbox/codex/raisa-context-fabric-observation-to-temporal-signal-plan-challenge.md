# Independent plan challenge — observation to temporal signal

Date: 2026-08-06

Reviewed source:
`e9e9ab2fe9db866bbe82cc4053a429d7561c5d98`

Decision: `revision_required`

The isolated native reviewer found four P1 specification gaps and one P2
ambiguity before implementation admission:

1. keyed observation identity did not explicitly bind practice, source system,
   source-contract digest and observer id, permitting cross-scope collision;
2. no exact closed prior-coordinate/baseline object owned duplicate, replay,
   position and revision decision inputs;
3. the exact source-to-temporal schema mapping, aggregate class and mandatory
   frame floor were left selectable by implementation;
4. `FULL_INVALIDATION_REQUIRED` lacked an exact machine-readable impact shape
   and an explicit admission-only claim; and
5. activation mode and observation evidence mode were not named as distinct
   exact fields.

The reviewer confirmed that the no-live-authority and API Spine separation was
otherwise preserved. Its exact allowed serial packet passed 60/60. Before and
after HEAD remained `e9e9ab2fe9db866bbe82cc4053a429d7561c5d98` and the
review worktree remained clean.

Sol repaired every finding in the immediate plan descendant before permitting
the implementation worker to finalise source.
