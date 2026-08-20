# Preset-mount effective-tool projection prelaunch recovery

Status: frozen recovery addendum  
Date: 2026-08-20  
Operation: `raisa-provider-free-check-in-native-harness-preset-mount-effective-tool-projection-rehearsal`

## Immutable failed attempt

Attempt `check-in-preset-mount-effective-tool-native-001` failed closed before
checkpoint consumption and before `subprocess.Popen`. The controller created
`installation/proof` before calling the accepted offline installer; that
installer exclusively owns creation of `installation`, so Windows returned
`FileExistsError`. No package process, native Harness process, agent, session,
turn, broker, model, provider, network, Docker or database action occurred.
The disposable root was removed and no raw log was retained. The exact bounded
record is `native-attempt-001-prelaunch-failure.json`.

Attempt 001 is closed and must not be rerun, resumed or reclassified.

## Narrow correction

Attempt `check-in-preset-mount-effective-tool-native-002` is a new identity,
not a retry of attempt 001. It makes only these lifecycle corrections:

1. let the accepted offline installer create and populate `installation`;
2. create `installation/proof` only after offline installation succeeds;
3. preserve any future prelaunch failure as a sanitized terminal with native
   process count zero before failing closed;
4. use new checkpoint, consumed, terminal and report paths for attempt 002.

All accepted root, preset, guard, projected-tool, event, provider-denial,
timeout, cleanup and product boundaries remain unchanged. Attempt 002 requires
a fresh exact-candidate review, an exclusive checkpoint and a fresh five-source
preexecution receipt. No native process is authorised by this addendum itself.
