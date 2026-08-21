# Ariadne agent error and correction register — revision 600

Date: 2026-08-22

Timestamp: 2026-08-22T00:12:25.1998531+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 600
incident_count: 857
new_incident_ids: AER-0857
open_incident_count: 0
-->

This revision note binds one corrected native-Harness prelaunch process-ownership
incident to the prospective clockwork-projected register. The canonical JSON
register and pattern report remain clockwork-owned, and one closeout tick may
advance the register once.

## AER-0857

The rebound-runner controller reused the accepted Windows offline-install helper,
which launched `npm.cmd` through `subprocess.run`. The wrapper parent ended while
its Node npm-CLI descendant remained live and held the disposable installation
directory, so recursive cleanup failed closed before the native Harness `Popen`
site. The exact owned descendant was terminated and its verified disposable root
removed; no Harness process, runner, worker, model/provider request, target or
canonical attempt evidence existed. Recovery generation 2 invokes the hash-bound
Node executable and npm CLI directly, waits or terminates that one owned
materialiser, proves absence, and retains the original single native-process and
no-retry boundary.

