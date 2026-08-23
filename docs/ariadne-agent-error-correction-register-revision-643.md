# Ariadne Agent Error and Correction Register — Revision 643

Date: 2026-08-23

Timestamp: 2026-08-23T13:49:43.3762208+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

<!-- ariadne-agent-error-register-reading
revision: 643
incident_count: 1109
new_incident_ids: AER-1100,AER-1101,AER-1102,AER-1103,AER-1104,AER-1105,AER-1106,AER-1107,AER-1108,AER-1109
open_incident_count: 0
-->

## AER-1100 — Preplanning narrative repeated machine-owned Git object IDs

The first preplanning receipt draft put exact Git objects in the prose
`git_refs_and_worktree` source. The preflight rejected it before dispatch. The
corrected receipt leaves those readings exclusively to the machine snapshot.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1101 — Rehydration guessed two long retained artifact paths

Two read commands reconstructed long evaluator and kernel artifact names from
memory and found no file. The retained paths were then resolved with the file
inventory before reading; no repository state changed.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1102 — Planning staging command transcribed one path incorrectly

One explicitly staged test path used a hyphen where the real filename used an
underscore. Git rejected the entire pathspec before staging. The exact path was
copied from the verified inventory and the cached diff was checked.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1103 — Reusable coordinator lacked a direct-execution import binding

The first direct coordinator invocation could not import a repository module
because its repository root was not on `sys.path`. The coordinator now binds
the root before repository imports, and direct invocation plus focused tests
passed before any provider work.

Origin: operator. Severity: moderate. Status: corrected and contained.

## AER-1104 — Worker-owned empty test scaffold was not collectible

The command-manifest preflight rejected an intentionally empty future test
file because it contained no collectible test. A skipped placeholder made the
scaffold admissible while keeping the worker responsible for replacing it.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1105 — Native attempt 001 failed before provider delivery without a safe subcoordinate

Harness hot-module replacement completed, but the custom runner returned
`CUSTOM_RUNNER_FAILURE` before reaching DeepSeek. The retained terminal records
zero requests and no candidate. A sanitized setup guard and attempt-scoped
artifacts were added before the one permitted fresh attempt.

Origin: external provider or harness. Severity: moderate. Status: corrected and contained.

## AER-1106 — Native attempt 002 could not mount the exact tool preset

The fresh attempt again completed hot-module replacement, then failed at
`EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED`. DeepSeek received no task and
produced no candidate. The assignment ended without a third run, fallback or
generic diagnostic successor, and Sol recovery was recorded explicitly.

Origin: external provider or harness. Severity: moderate. Status: corrected and contained.

## AER-1107 — Initial Sol guard evaluated a regex against a missing value

The first local implementation constructed an `all` tuple eagerly, so a regex
received `None` despite an earlier false type predicate. Focused hostile-input
tests caught the exception before commit. Explicit primitive early returns now
precede every type-specific operation.

Origin: operator. Severity: moderate. Status: corrected and contained.

## AER-1108 — PowerShell misparsed a brace-suffixed Git revision expression

An unquoted revision expression became an invalid Git argument during verifier
worktree setup. Git stopped before mutation. The corrected command supplied the
already machine-read full 40-character current HEAD directly.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1109 — Fresh verifier process retained an empty worktree directory handle

After the clean Gemini receipt, Git removed worktree metadata but Windows could
not remove the empty directory while the newly launched `agy` process retained
its handle. Only that exact fresh process was stopped, and the validated empty
directory was removed without touching older processes or repository data.

Origin: operator. Severity: low. Status: corrected and contained.

## Aggregate reading

The durable register will contain 1,109 corrected or contained incidents and
zero open incidents after clockwork publication. The two native-Harness events
were pre-provider orchestration failures: zero DeepSeek requests and zero
candidates. The accepted product seam instead came from explicit Sol recovery
and a clean Gemini veto. None of these incidents opened ordinary practice,
product data, runtime, deployment, Pages or protected-ref authority.
