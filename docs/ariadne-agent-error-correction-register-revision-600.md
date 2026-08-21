# Ariadne agent error and correction register — revision 600

Date: 2026-08-22

Timestamp: 2026-08-22T00:49:06.0632417+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 600
incident_count: 858
new_incident_ids: AER-0857,AER-0858
open_incident_count: 0
-->

This revision note binds two corrected native-Harness prelaunch materialisation
incidents to the prospective clockwork-projected register. The canonical JSON
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

## AER-0858

Recovery generation 2 proved direct npm-process ownership, but the hash-bound
Node/npm-CLI materialiser remained nonterminal until its frozen 600-second
deadline. The controller terminated and waited for that exact process, cleaned
the disposable root and wrote no native-attempt evidence; the native Harness
`Popen` site was never reached. Generation 3 removes npm from prelaunch, binds a
dedicated package-only rc.7 seed by exact lockfile, package roster, file/byte
counts and canonical tree digest, and independently verifies the disposable copy
before the unchanged single native launch.
