# Rebound future-runner boot prelaunch materialisation process-ownership recovery

Date: 2026-08-22

Timestamp: 2026-08-22T00:09:18.9799961+10:00 (Australia/Brisbane)

Status: **frozen recovery before another prelaunch invocation**

## Observed failure

The first controller invocation never reached the native Harness `Popen`. Its
offline `npm.cmd install` parent ended while a descendant `node npm-cli.js`
process remained live and held the disposable installation directory. The
controller's recursive cleanup therefore failed closed. The exact owned
descendant was terminated, the exact verified disposable root was removed, and
process/root absence was read back.

No native Harness process, HMR event, runner activation, agent creation, worker,
broker process, model/provider request, target creation or canonical attempt
evidence occurred. Under the frozen plan's explicit prelaunch rule, native
execution attempt `rebound-stock-headless-hmr-boot-attempt-001` is unconsumed.

The typed incident is
`orchestration/continuity/deepseek-native-harness-provider-free-rebound-future-runner-stock-headless-hmr-boot-proof/prelaunch-materialisation-failure-001.json`.

## Narrow correction

The controller must no longer launch the Windows `npm.cmd` wrapper through
`subprocess.run`. It must instead:

1. resolve the installed Node executable and npm's exact local `npm-cli.js`;
2. launch that JavaScript entry point as one directly owned prelaunch process;
3. retain no stdout or stderr;
4. wait within the separately frozen materialisation deadline;
5. terminate and wait for that exact owned process on every nonterminal path;
6. prove the owned materialiser is absent before either failing prelaunch or
   advancing to package/source validation; and
7. keep the native Harness `Popen` site singular and unchanged.

The recovery increases prelaunch materialisation generation from 1 to 2. It is
not a native Harness retry, resume, second runner or alternate runner. The exact
runner, helper, target, package, HMR, sidecar, broker-zero and terminal contracts
remain unchanged.

## Recovery acceptance

- deterministic tests prove direct Node/npm-CLI ownership and reject wrapper or
  `subprocess.run` regression;
- the materialisation process count is exactly one and its retry count is zero;
- a timeout or nonzero exit leaves the owned process and disposable root absent
  and writes no canonical native-attempt evidence;
- a passed materialisation may advance to exactly one native Harness process;
- all original provider-free, no-worker, no-target, no-data, no-product and
  protected-ref boundaries remain exact.

