# Native Harness custom-runner pre-request source-coordinate diagnosis

Date: 2026-08-21

Timestamp: 2026-08-21T20:13:19.9793090+10:00 (Australia/Brisbane)

## Result

`pass`

The accepted attempt-005 runner and four relevant cached rc.7 source members
match their frozen SHA-256 bindings and required operation shapes. The runner's
generic catch spans seven source-visible pre-request or request-adjacent
coordinates:

- `loader_readiness_wait`
- `required_service_lookup`
- `preset_root_roster_admission`
- `agent_create_setup_publish`
- `initial_idle_wait`
- `first_followup_dispatch`
- `first_turn_idle_wait`

The future sidecar selects only from that list. It projects one closed cause
coordinate and one closed constructor/name kind, reads no raw message, stack,
code, cause or path, writes once with exclusive-create semantics and cannot
replace the primary rejection.

## Source boundary

- accepted runner: `1233d4fc14726800dcf063c1cab5e814f3df0091040126784c4a7d42c3ec0746`
- rc.7 dsh-agent: `e7e40c5ca66d9827a5084c5c0c68983f9685842bb9b6d604803d4cb4642bb263`
- rc.7 dsh-agent-loop: `bf8ca1e9b05e9b78320a5e2f0b4e25395eba91dd72db6d3cb5626e3dfb529204`
- rc.7 dsh-agent-presets: `a0b417514e3d285ad5fef74867e8049af333ebdec6e4d7639e388aa0903e0039`
- rc.7 dsh-session: `9270186b579bc8a4c6c53c256e4471d3f134e94308462c6a413a722e9c7556fb`

`agents.create` is one honest runner coordinate even though rc.7 performs
session preparation, setup/preset mounting, publication and loop start inside
it. This tranche does not claim a narrower internal coordinate. Likewise,
`first_turn_idle_wait` becomes a pre-request conclusion only when joined to an
independent broker reading of zero requests.

## Conclusion

The exact stage vocabulary and sidecar contract are ready for a separately
authorised provider-free integration rehearsal. No occupied retry is justified
by this diagnosis alone, and no DeepSeek performance or general Harness
readiness was measured.
