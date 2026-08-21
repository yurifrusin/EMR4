# DeepSeek native Harness preset-composition safe-terminal implementation recovery

Date: 2026-08-22

Timestamp: 2026-08-22T04:31:24.1598131+10:00 (Australia/Brisbane)

Five operator errors were detected and corrected without running another
native Harness process.

First, the focused threat-control test asserted the positive phrase “No raw
guard errors escape” while the frozen threat table correctly names the threat
as “Raw guard errors escape.” The assertion now binds the exact frozen row.

Second, runner validation compared the successor private identity with the
dynamically rebound predecessor module global. The validation context itself
had changed that value, so a valid distinct identity failed. The validator now
compares with the captured accepted predecessor identity.

Third, the first preexecution receipt was generated while its own two receipt
paths were modified, and it honestly recorded a dirty tracked tree. Those bytes
remain historical. After committing them, a fresh receipt at
`7f0c1126d5017ebf660eea3b026d95d5e9a2c3c9` recorded a clean tracked tree and
branch/origin alignment before the single native attempt.

The corrections were admitted by deterministic tests before execution. None
consumed a native attempt, contacted a provider, created a target or altered an
accepted execution artifact after the attempt.

During closeout, the first new immutable-evidence test inferred a new attempt
schema name rather than reading the consumed artifact's inherited schema. The
test failed and now binds the exact retained schema value.

The first combined inherited closeout command also repeated the already known
mistake of using the provider-free wrapper for tests whose deterministic check
requires the host cache-location binding. It failed only with the typed
`localappdata_missing` guard and created no native process. The corrected
closeout command uses no-conftest pytest, exactly as the accepted predecessor
recovery requires.
